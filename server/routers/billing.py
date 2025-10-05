"""
Billing Router Module

This module provides billing and subscription management endpoints for the Tutor AI system,
integrating with Stripe for payment processing. It handles subscription creation, management,
billing portal access, and webhook processing for automated plan updates.

Key Features:
- User billing status retrieval with subscription details
- Stripe checkout session creation for subscription purchases
- Customer portal access for subscription management
- Subscription cancellation and resumption
- Webhook handling for automated subscription updates
- Price listing for development and configuration

Security Considerations:
- Stripe webhook signature verification
- User authentication required for billing operations
- Secure handling of customer and subscription IDs
- Graceful degradation when Stripe is not configured

Dependencies:
- FastAPI for API routing and request handling
- Stripe SDK for payment processing
- MongoDB for user and subscription data storage
- JWT authentication for user verification

Configuration Requirements:
- STRIPE_SECRET_KEY: Stripe API secret key
- STRIPE_WEBHOOK_SECRET: Webhook endpoint secret for signature verification
- STRIPE_PRICE_STANDARD/PREMIUM: Price IDs for subscription tiers
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from bson import ObjectId
from typing import Dict, Any, Optional

from ..auth import get_current_user
from ..database import col
from ..config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    STRIPE_PRICE_STANDARD,
    STRIPE_PRICE_PREMIUM,
)

# Create router with billing prefix and tags for API documentation
router = APIRouter(prefix="/billing", tags=["billing"])

try:
    import stripe  # type: ignore
except Exception:
    # Handle case where Stripe is not installed
    stripe = None


def _require_stripe():
    """
    Ensure Stripe is properly configured and available.

    This helper function checks if Stripe SDK is installed and configured
    with the required API keys. Raises HTTP 501 if Stripe is not available.

    Raises:
        HTTPException: 501 if Stripe is not configured
    """
    if not stripe or not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=501, detail="Stripe not configured on server")
    stripe.api_key = STRIPE_SECRET_KEY


@router.get("/me")
async def my_billing_status(user=Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user's billing status and subscription information.

    Retrieves the user's current plan, usage statistics, and subscription details
    from Stripe if available. Provides a comprehensive view of the user's billing state.

    Args:
        user: Current authenticated user information from JWT token

    Returns:
        Dict containing:
        - plan: Current subscription plan ("free", "standard", "premium")
        - usage: Usage statistics and counters
        - subscription: Stripe subscription details (if applicable)
    """
    # Retrieve user document from database
    u = await col("users").find_one({"_id": ObjectId(user.get("sub"))})
    plan = (u.get("plan") if u else None) or "free"
    usage = (u.get("usage") if u else None) or {}

    # Optionally enrich with subscription summary if Stripe configured and we have subscriptionId
    subscription: Optional[Dict[str, Any]] = None
    try:
        if stripe and STRIPE_SECRET_KEY and u and u.get("subscriptionId"):
            stripe.api_key = STRIPE_SECRET_KEY
            # Retrieve subscription details from Stripe
            sub = stripe.Subscription.retrieve(u.get("subscriptionId"))  # type: ignore

            # Extract basic subscription information
            item = (sub.get("items") or {}).get("data", [{}])[0]
            price = (item or {}).get("price") or {}
            subscription = {
                "status": sub.get("status"),
                "current_period_end": sub.get("current_period_end"),
                "cancel_at_period_end": sub.get("cancel_at_period_end", False),
                "price": {
                    "id": price.get("id"),
                    "unit_amount": (price.get("unit_amount") or 0),
                    "currency": price.get("currency"),
                    "interval": (price.get("recurring") or {}).get("interval"),
                },
            }

            # Try to fetch upcoming invoice for next amount due
            try:
                upcoming = stripe.Invoice.upcoming(subscription=sub.get("id"))  # type: ignore
                if upcoming:
                    subscription["next_invoice_amount_due"] = upcoming.get("amount_due")
                    subscription["next_invoice_currency"] = upcoming.get("currency")
                    subscription["next_payment_attempt"] = upcoming.get("next_payment_attempt")
            except Exception:
                # Swallow errors when upcoming invoice is not available
                pass
    except Exception:
        # Non-fatal: ignore subscription enrichment if anything fails
        subscription = None

    # Build response with plan and usage information
    out: Dict[str, Any] = {"plan": plan, "usage": usage}
    if subscription:
        out["subscription"] = subscription
    return out


@router.post("/checkout/session")
async def create_checkout_session(payload: Dict[str, Any], user=Depends(get_current_user)) -> Dict[str, Any]:
    """
    Create a Stripe checkout session for subscription purchase.

    This endpoint creates a Stripe checkout session for purchasing or upgrading
    a subscription. It handles customer creation, price selection, and session configuration.

    Args:
        payload: Request payload containing:
            - price: Plan type ("standard" or "premium")
            - priceId: Optional direct Stripe price ID override
            - successUrl/cancelUrl: Redirect URLs for checkout completion
        user: Current authenticated user information

    Returns:
        Dict containing checkout session ID and URL

    Raises:
        HTTPException: 400 for invalid price configuration, 501 if Stripe not configured
    """
    _require_stripe()

    # Extract checkout parameters from payload
    price_key = payload.get("price")  # "standard" | "premium"
    price_id_override = payload.get("priceId")  # optional direct price id
    success_url = payload.get("successUrl") or payload.get("success_url") or ""
    cancel_url = payload.get("cancelUrl") or payload.get("cancel_url") or ""

    # Determine price ID to use for checkout
    price_id = None
    if price_id_override:
        price_id = price_id_override
    elif price_key == "standard":
        price_id = STRIPE_PRICE_STANDARD
    elif price_key == "premium":
        price_id = STRIPE_PRICE_PREMIUM

    if not price_id:
        # Provide a clearer message to help configure prices
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid or unconfigured price",
                "hint": (
                    "Pass a valid 'priceId' in the request or configure STRIPE_PRICE_STANDARD/STRIPE_PRICE_PREMIUM on the server, "
                    "or set VITE_STRIPE_PRICE_STANDARD/VITE_STRIPE_PRICE_PREMIUM on the client."
                ),
                "received": {"price": price_key, "priceId": bool(price_id_override)},
            },
        )

    # Ensure customer mapping on user
    user_id = user.get("sub")
    udoc = await col("users").find_one({"_id": ObjectId(user_id)})
    customer_id = (udoc or {}).get("stripeCustomerId")

    if not customer_id:
        # Create new Stripe customer if one doesn't exist
        c = stripe.Customer.create(email=user.get("email"))
        customer_id = c["id"]
        # Store customer ID in user document
        await col("users").update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"stripeCustomerId": customer_id}},
        )

    # Ensure success_url contains the session id placeholder so the client can confirm
    def with_session_id(url: str) -> str:
        """Add session ID placeholder to success URL if not present."""
        if not url:
            return "http://localhost:5173/dashboard?session=success&session_id={CHECKOUT_SESSION_ID}"
        sep = '&' if ('?' in url) else '?'
        if '{CHECKOUT_SESSION_ID}' in url or 'session_id=' in url:
            return url
        return f"{url}{sep}session_id={{CHECKOUT_SESSION_ID}}"

    # Determine plan label for metadata
    plan_label = "standard" if price_key == "standard" else ("premium" if price_key == "premium" else "standard")

    # Create Stripe checkout session
    checkout = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=with_session_id(success_url),
        cancel_url=cancel_url or "http://localhost:5173/pricing?session=cancel",
        metadata={"user_id": user_id, "plan": plan_label},
    )
    return {"id": checkout["id"], "url": checkout.get("url")}


@router.get("/prices")
async def list_prices(user=Depends(get_current_user)) -> Dict[str, Any]:
    """
    List active Stripe prices for development and configuration.

    Development helper endpoint that returns active Stripe prices with essential
    information for copying price IDs and understanding available products.

    Args:
        user: Current authenticated user (required for authentication)

    Returns:
        Dict containing list of active prices with id, nickname, currency, amount, and interval

    Raises:
        HTTPException: 501 if Stripe not configured, 500 for API errors
    """
    _require_stripe()
    try:
        # Retrieve active prices with product expansion
        prices = stripe.Price.list(active=True, expand=["data.product"])  # type: ignore
        items = []
        for p in prices.get("data", []):
            product = p.get("product") or {}
            items.append({
                "id": p.get("id"),
                "nickname": p.get("nickname") or product.get("name"),
                "currency": p.get("currency"),
                "unit_amount": p.get("unit_amount"),
                "recurring": (p.get("recurring") or {}).get("interval"),
            })
        return {"prices": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list prices: {e}")


@router.post("/confirm")
async def confirm_checkout(payload: Dict[str, Any], user=Depends(get_current_user)) -> Dict[str, Any]:
    """
    Confirm a completed checkout session and update user subscription.

    This endpoint is used to confirm checkout completion when webhooks are not
    configured (development mode). It retrieves session details and updates the
    user's plan and subscription information.

    Args:
        payload: Request payload containing session_id or sessionId
        user: Current authenticated user information

    Returns:
        Dict containing confirmed plan

    Raises:
        HTTPException: 400 for invalid session, 501 if Stripe not configured
    """
    _require_stripe()
    session_id = payload.get("session_id") or payload.get("sessionId")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    try:
        # Retrieve checkout session from Stripe
        sess = stripe.checkout.Session.retrieve(session_id)
        customer_id = sess.get("customer")
        sub_id = sess.get("subscription")

        if not (customer_id and sub_id):
            raise HTTPException(status_code=400, detail="Invalid checkout session")

        # Retrieve subscription details
        sub = stripe.Subscription.retrieve(sub_id)
        price_id = (sub["items"]["data"][0]["price"]["id"]) if sub["items"]["data"] else None
        if not price_id:
            raise HTTPException(status_code=400, detail="Subscription has no price")

        # Prefer explicit plan label from session metadata if provided
        meta = sess.get("metadata") or {}
        plan = meta.get("plan") if meta.get("plan") in ("standard", "premium") else None

        # Fallback: infer plan by comparing price IDs configured on server
        if not plan:
            plan = "standard"
        if STRIPE_PRICE_PREMIUM and price_id == STRIPE_PRICE_PREMIUM:
            plan = "premium"
        elif STRIPE_PRICE_STANDARD and price_id == STRIPE_PRICE_STANDARD:
            plan = "standard"

        # Update user document with new plan and subscription information
        await col("users").update_one(
            {"_id": ObjectId(user.get("sub"))},
            {"$set": {"plan": plan, "stripeCustomerId": customer_id, "subscriptionId": sub_id}},
        )
        return {"plan": plan}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm session: {e}")


@router.post("/portal")
async def create_customer_portal(user=Depends(get_current_user)) -> Dict[str, Any]:
    """
    Create a Stripe customer portal session for subscription management.

    This endpoint creates a Stripe billing portal session where users can manage
    their subscriptions, update payment methods, and view billing history.

    Args:
        user: Current authenticated user information

    Returns:
        Dict containing portal session URL

    Raises:
        HTTPException: 400 if no Stripe customer exists, 501 if Stripe not configured
    """
    _require_stripe()

    # Retrieve user document to get Stripe customer ID
    udoc = await col("users").find_one({"_id": ObjectId(user.get("sub"))})
    if not udoc or not udoc.get("stripeCustomerId"):
        raise HTTPException(status_code=400, detail="No Stripe customer for user")

    # Create billing portal session
    session = stripe.billing_portal.Session.create(
        customer=udoc["stripeCustomerId"],
        return_url="http://localhost:5173/dashboard",
    )
    return {"url": session["url"]}


@router.post("/subscription/cancel")
async def cancel_subscription(payload: Dict[str, Any], user=Depends(get_current_user)) -> Dict[str, Any]:
    """
    Cancel a user's subscription.

    Cancels the user's active subscription, either immediately or at the end of
    the current billing period. Updates user plan accordingly.

    Args:
        payload: Request payload with optional atPeriodEnd flag (default: True)
        user: Current authenticated user information

    Returns:
        Dict containing cancellation status and plan information

    Raises:
        HTTPException: 400 if no active subscription, 501 if Stripe not configured
    """
    _require_stripe()
    at_period_end = payload.get("atPeriodEnd", True)

    # Retrieve user document to get subscription ID
    udoc = await col("users").find_one({"_id": ObjectId(user.get("sub"))})
    sub_id = (udoc or {}).get("subscriptionId")
    if not sub_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    try:
        if at_period_end:
            # Cancel at end of billing period
            sub = stripe.Subscription.modify(sub_id, cancel_at_period_end=True)  # type: ignore
            # Keep plan as-is until end of period
        else:
            # Immediate cancellation
            stripe.Subscription.delete(sub_id)  # type: ignore
            # Immediate cancellation: downgrade to free
            await col("users").update_one(
                {"_id": ObjectId(user.get("sub"))},
                {"$set": {"plan": "free"}, "$unset": {"subscriptionId": ""}},
            )
            return {"status": "canceled", "plan": "free"}

        # Return updated subscription summary
        return {"status": sub.get("status"), "cancel_at_period_end": sub.get("cancel_at_period_end", False)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {e}")


@router.post("/subscription/resume")
async def resume_subscription(user=Depends(get_current_user)) -> Dict[str, Any]:
    """
    Resume a subscription that was set to cancel at period end.

    Removes the cancellation flag from a subscription, allowing it to continue
    billing normally.

    Args:
        user: Current authenticated user information

    Returns:
        Dict containing updated subscription status

    Raises:
        HTTPException: 400 if no active subscription, 501 if Stripe not configured
    """
    _require_stripe()

    # Retrieve user document to get subscription ID
    udoc = await col("users").find_one({"_id": ObjectId(user.get("sub"))})
    sub_id = (udoc or {}).get("subscriptionId")
    if not sub_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    try:
        # Remove cancellation flag
        sub = stripe.Subscription.modify(sub_id, cancel_at_period_end=False)  # type: ignore
        return {"status": sub.get("status"), "cancel_at_period_end": sub.get("cancel_at_period_end", False)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume subscription: {e}")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events for automated subscription management.

    Processes incoming webhook events from Stripe to automatically update user
    subscriptions and plans. Handles checkout completion and subscription deletion events.

    Args:
        request: Raw HTTP request containing webhook payload and signature

    Returns:
        JSONResponse with status confirmation

    Raises:
        HTTPException: 400 for invalid webhook signature or data
    """
    _require_stripe()

    # Extract and verify webhook payload
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

    # Handle subscription events to set plan on user
    event_type = event["type"]
    data = event["data"]["object"]

    # Handle checkout session completion
    if event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        sub_id = data.get("subscription")
        meta = data.get("metadata") or {}

        # Look up subscription to determine price and plan
        if customer_id and sub_id:
            sub = stripe.Subscription.retrieve(sub_id)
            # Assume single item subscription
            price_id = (sub["items"]["data"][0]["price"]["id"]) if sub["items"]["data"] else None

            # Prefer plan from metadata when available
            plan = meta.get("plan") if meta.get("plan") in ("standard", "premium") else None
            if not plan:
                plan = "standard" if price_id == STRIPE_PRICE_STANDARD else ("premium" if price_id == STRIPE_PRICE_PREMIUM else "free")

            # Update user with new plan and subscription information
            await col("users").update_one(
                {"stripeCustomerId": customer_id},
                {"$set": {"plan": plan, "subscriptionId": sub_id}},
            )

    # Handle subscription deletion (downgrade to free)
    if event_type == "customer.subscription.deleted":
        customer_id = data.get("customer")
        if customer_id:
            await col("users").update_one(
                {"stripeCustomerId": customer_id},
                {"$set": {"plan": "free"}, "$unset": {"subscriptionId": ""}},
            )

    return JSONResponse({"status": "ok"})
