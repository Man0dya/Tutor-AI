# Security Policy

Last updated: 2025-09-26

We take the security of Tutor-AI seriously. Please report vulnerabilities privately so we can fix them quickly and responsibly.

## Supported Versions

We currently support the latest code on the active development branch:

- Manodya-New (default working branch)

Security fixes will generally target the latest commit on this branch. Older snapshots may not receive patches.

## Reporting a Vulnerability

Please do NOT open a public GitHub issue for security reports.

Preferred (private) channels:

1) GitHub Security Advisories (recommended)
- Submit a private report here: https://github.com/Man0dya/Tutor-AI/security/advisories/new

2) Email
- Send details to: security@example.com (replace with your contact address)

When reporting, include where possible:
- A clear description of the issue and its impact
- Steps to reproduce (or a proof‑of‑concept)
- Affected component (frontend/client vs backend/server) and commit hash, if known
- Any logs or stack traces (redact secrets and personal data)
- Your contact info for follow‑up

We will acknowledge receipt within 48 hours. We’ll provide an initial assessment within 5 business days and strive to deliver a fix or mitigation within 7–14 days, depending on severity and complexity. Critical issues may be prioritized for immediate patches.

## Scope

In scope:
- Backend: FastAPI app (authentication, content, questions, answers, progress, billing routers), MongoDB integration, JWT handling
- Frontend: React (Vite + TypeScript + Chakra UI) application and its auth/plan/billing flows
- Configuration impacting security (e.g., CORS, Stripe webhook handling)

Out of scope (non‑exhaustive):
- Social engineering, phishing, or physical security attacks
- Denial‑of‑Service without an accompanying exploit that demonstrates data exposure or integrity compromise
- Issues in third‑party services or dependencies unless you can demonstrate a direct impact on this project’s security posture
- Best‑practice recommendations without a concrete vulnerability (we still welcome hardening suggestions separately)

## Coordinated Disclosure

Please keep vulnerabilities confidential until a patch is released. We will communicate timelines and coordinate a disclosure window. We are happy to credit reporters in release notes unless you prefer to remain anonymous.

## Safe Harbor

We support good‑faith security research. As long as you:
- Report vulnerabilities promptly
- Avoid privacy violations and do not access or exfiltrate data you do not own
- Do not degrade services or harm users
- Comply with applicable laws

We will not pursue legal action related to your research. This Safe Harbor does not cover actions that are illegal or that go beyond what is necessary to demonstrate the vulnerability.

## Encryption / Keys

We do not currently publish a security PGP key. If you require encrypted communication, mention this in your report and we can arrange a secure channel.

## Thank You

We appreciate responsible security disclosures. Your efforts help keep the community safe.
