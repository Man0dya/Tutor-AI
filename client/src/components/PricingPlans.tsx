import React from "react";
import { Box, Button, Flex, Heading, Text, List, ListItem, ListIcon, VStack, HStack, Badge } from "@chakra-ui/react";
import { FaCheck } from "react-icons/fa";
import { createCheckoutSession } from "../api/client";

const plans = [
  {
    name: "Free",
    price: "0",
    period: "Forever free",
    description: "Perfect for getting started with AI tutoring",
    features: [
      "10 content generations per month",
      "Basic AI feedback",
      "Community support",
      "Basic progress tracking"
    ],
    button: "Get Started",
    highlight: false,
    popular: false
  },
  {
    name: "Pro",
    price: "15",
    period: "per month",
    description: "Everything you need for serious learning",
    features: [
      "100 content generations per month",
      "100 question generations per month", 
      "100 feedback evaluations per month",
      "Advanced analytics",
      "Priority support",
      "Custom difficulty levels"
    ],
    button: "Upgrade to Pro",
    highlight: true,
    popular: true
  },
  {
    name: "Unlimited",
    price: "50",
    period: "per month",
    description: "For power users and intensive learning",
    features: [
      "Unlimited content generations",
      "Unlimited question generations",
      "Unlimited feedback evaluations",
      "Advanced analytics & insights",
      "Priority support",
      "Custom integrations",
      "Team collaboration tools"
    ],
    button: "Upgrade to Unlimited",
    highlight: false,
    popular: false
  },
];

const PricingPlans: React.FC = () => {
  return (
    <Box maxW="6xl" mx="auto">
      <Flex 
        direction={{ base: "column", lg: "row" }} 
        gap={6} 
        justify="center" 
        align="stretch"
      >
        {plans.map((plan) => (
          <Box
            key={plan.name}
            bg="white"
            borderRadius="xl"
            border="1px"
            borderColor={plan.highlight ? "purple.200" : "gray.200"}
            boxShadow={plan.highlight ? "0 10px 40px rgba(139, 92, 246, 0.1)" : "0 4px 12px rgba(0, 0, 0, 0.05)"}
            p={8}
            flex="1"
            maxW={{ base: "100%", lg: "400px" }}
            position="relative"
            _hover={{
              boxShadow: plan.highlight 
                ? "0 20px 60px rgba(139, 92, 246, 0.15)" 
                : "0 8px 24px rgba(0, 0, 0, 0.08)",
              transform: "translateY(-4px)"
            }}
            transition="all 0.3s ease"
          >
            {/* Popular Badge */}
            {plan.popular && (
              <Badge
                position="absolute"
                top="-12px"
                left="50%"
                transform="translateX(-50%)"
                bg="purple.600"
                color="white"
                px={4}
                py={1}
                borderRadius="full"
                fontSize="sm"
                fontWeight="600"
                boxShadow="0 4px 12px rgba(139, 92, 246, 0.3)"
              >
                Most Popular
              </Badge>
            )}

            <VStack spacing={6} align="stretch">
              {/* Plan Header */}
              <VStack spacing={2} align="start">
                <Heading size="lg" color="gray.900" fontWeight="600">
                  {plan.name}
                </Heading>
                <Text color="gray.600" fontSize="md" lineHeight="1.5">
                  {plan.description}
                </Text>
              </VStack>

              {/* Pricing */}
              <HStack align="baseline" spacing={1}>
                <Text fontSize="sm" color="gray.500" fontWeight="500">
                  $
                </Text>
                <Text fontSize="5xl" fontWeight="700" color="gray.900" lineHeight="1">
                  {plan.price}
                </Text>
                <Text color="gray.500" fontSize="md" fontWeight="500">
                  {plan.period}
                </Text>
              </HStack>

              {/* Features */}
              <VStack spacing={4} align="stretch">
                <Text fontSize="sm" fontWeight="600" color="gray.900" textTransform="uppercase" letterSpacing="wider">
                  What's included
                </Text>
                <List spacing={3}>
                  {plan.features.map((feature, index) => (
                    <ListItem key={index} display="flex" alignItems="flex-start" gap={3}>
                      <ListIcon 
                        as={FaCheck} 
                        color="green.500" 
                        mt={1}
                        boxSize={4}
                        flexShrink={0}
                      />
                      <Text fontSize="sm" color="gray.700" lineHeight="1.6">
                        {feature}
                      </Text>
                    </ListItem>
                  ))}
                </List>
              </VStack>

              {/* CTA Button */}
              <Button
                size="lg"
                w="full"
                bg={plan.highlight ? "purple.600" : "white"}
                color={plan.highlight ? "white" : "purple.600"}
                border="1px"
                borderColor={plan.highlight ? "purple.600" : "purple.600"}
                borderRadius="lg"
                fontWeight="600"
                fontSize="md"
                py={6}
                _hover={{
                  bg: plan.highlight ? "purple.700" : "purple.50",
                  borderColor: plan.highlight ? "purple.700" : "purple.700",
                  transform: "translateY(-2px)"
                }}
                _active={{
                  transform: "translateY(0)"
                }}
                transition="all 0.2s ease"
                onClick={async () => {
                  if (plan.name.toLowerCase() === 'free') {
                    alert('You are on the Free plan with 10 question generations and basic features.')
                    return
                  }
                  let key: 'standard' | 'premium' = 'standard'
                  if (plan.name.toLowerCase() === 'pro') key = 'standard'
                  else if (plan.name.toLowerCase() === 'unlimited') key = 'premium'
                  
                  const priceId = key === 'standard'
                    ? (import.meta.env.VITE_STRIPE_PRICE_STANDARD as string | undefined)
                    : (import.meta.env.VITE_STRIPE_PRICE_PREMIUM as string | undefined)
                  try {
                    const session = await createCheckoutSession(
                      key as 'standard' | 'premium',
                      window.location.origin + '/dashboard',
                      window.location.origin + '/pricing',
                      priceId
                    )
                    if (session.url) {
                      window.location.assign(session.url)
                    } else {
                      alert('Checkout session created. Please check your email if the redirect did not happen.')
                    }
                  } catch (e) {
                    console.error(e)
                    alert('Failed to start checkout. Please try again later.')
                  }
                }}
              >
                {plan.button}
              </Button>
            </VStack>
          </Box>
        ))}
      </Flex>
    </Box>
  );
};

export default PricingPlans;