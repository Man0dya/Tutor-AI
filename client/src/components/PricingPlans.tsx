import React from "react";
import { Box, Button, Flex, Heading, Text, List, ListItem, ListIcon, useColorModeValue, Icon } from "@chakra-ui/react";
import { IoCheckmarkCircle, IoStar, IoAt } from "react-icons/io5";

const plans = [
  {
    name: "Free",
    price: "$0/month",
    icon: IoAt,
    features: [
      "10 free question generations",
      "5 free feedback evaluations",
      "Basic features",
    ],
    gradient: "linear(to-br, #f8fafc, #fbeffb)", // pastel gray-pink
    color: "#6b7280", // slate gray
    border: "2px solid #f3e8ff",
    button: "Start Free",
    highlight: false,
    badge: null,
  },
  {
    name: "Pro",
    price: "$9.99/month",
    icon: IoStar,
    features: [
      "Unlimited question generations",
      "Unlimited feedback evaluations",
      "Priority support",
    ],
    gradient: "linear(to-br, #b5e4f7, #fbc2eb)", // pastel blue-pink
    color: "#4b5563", // dark slate
    border: "2px solid #b5e4f7",
    button: "Upgrade to Pro",
    highlight: true,
    badge: "Save 20%",
  },
  {
    name: "Enterprise",
    price: "$29.99/month",
    icon: IoCheckmarkCircle,
    features: [
      "Custom AI models",
      "Team access",
      "Dedicated support",
    ],
    gradient: "linear(to-br, #fbc2eb, #a1c4fd)", // pastel pink-blue
    color: "#374151", // deep slate
    border: "2px solid #fbc2eb",
    button: "Contact Sales",
    highlight: false,
    badge: "Best Value",
  },
];

const PricingPlans: React.FC = () => {
  const cardBg = useColorModeValue("white", "gray.800");
  return (
    <Box position="relative" py={8}>
      {/* Animated floating icons background */}
      <Box position="absolute" top="-40px" left="-60px" zIndex={0} opacity={0.13} pointerEvents="none">
        <Icon as={IoStar} boxSize={32} color="#b5e4f7" animation="spin 18s linear infinite" />
      </Box>
      <Box position="absolute" bottom="-40px" right="-60px" zIndex={0} opacity={0.11} pointerEvents="none">
        <Icon as={IoCheckmarkCircle} boxSize={36} color="#fbc2eb" animation="spin 22s linear reverse infinite" />
      </Box>
      <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
      
      <Text fontSize="lg" mb={10} textAlign="center" color="gray.600" zIndex={2} position="relative">
        Pick the plan that fits your learning journey and unlock your full potential.
      </Text>
      <Flex direction={{ base: "column", md: "row" }} gap={6} justify="center" align="center" zIndex={2} position="relative">
        {plans.map((plan) => (
          <Box
            key={plan.name}
            bg={plan.highlight ? 'rgba(128,90,213,0.10)' : 'rgba(255,255,255,0.92)'}
            bgGradient={plan.gradient}
            color={plan.color}
            borderRadius="2xl"
            boxShadow={plan.highlight ? "0 18px 48px 0 rgba(128,90,213,0.18)" : "0 2px 8px rgba(0,0,0,0.06)"}
            border={plan.border}
            p={8}
            w={{ base: "95vw", sm: "300px" }}
            maxW="320px"
            textAlign="center"
            position="relative"
            zIndex={plan.highlight ? 2 : 1}
            backdropFilter="blur(12px)"
            _before={plan.highlight ? {
              content: '""',
              position: 'absolute',
              top: '-18px',
              left: '50%',
              transform: 'translateX(-50%)',
              w: '90%',
              h: '16px',
              bgGradient: 'linear(to-r, purple.400, blue.400, teal.400)',
              borderRadius: 'full',
              filter: 'blur(8px)',
              opacity: 0.5,
              zIndex: -1,
              animation: 'shine 2.5s linear infinite',
              '@keyframes shine': {
                '0%': { opacity: 0.5 },
                '50%': { opacity: 1 },
                '100%': { opacity: 0.5 },
              },
            } : {}}
            _hover={{
              transform: 'translateY(-10px) scale(1.05)',
              boxShadow: plan.highlight
                ? '0 28px 80px 0 rgba(128,90,213,0.22)'
                : '0 10px 32px rgba(0,0,0,0.13)',
            }}
            transition="all 0.3s cubic-bezier(.4,0,.2,1)"
          >
            {/* Plan badge */}
            {plan.badge && (
              <Box
                position="absolute"
                top={6}
                left={6}
                bgGradient={plan.badge === 'Best Value' ? "linear(to-r, #fbc2eb, #a1c4fd)" : "linear(to-r, #fbeffb, #b5e4f7)"}
                color="#374151"
                px={4}
                py={1}
                borderRadius="full"
                fontWeight="bold"
                fontSize="sm"
                letterSpacing="wide"
                boxShadow="0 2px 12px #fbc2eb55"
                zIndex={3}
              >
                {plan.badge}
              </Box>
            )}
            {/* Highlight badge */}
            {plan.highlight && (
              <Box
                position="absolute"
                top={6}
                right={6}
                bgGradient="linear(to-r, purple.500, blue.500)"
                color="white"
                px={5}
                py={2}
                borderRadius="full"
                fontWeight="bold"
                fontSize="md"
                letterSpacing="wide"
                boxShadow="0 2px 12px rgba(128,90,213,0.18)"
                zIndex={3}
              >
                Most Popular
              </Box>
            )}
            <Flex align="center" justify="center" mb={4}>
              <Icon as={plan.icon} boxSize={8} color={plan.highlight ? 'yellow.300' : 'purple.400'} />
            </Flex>
            <Heading size="md" mb={1} fontWeight="extrabold" letterSpacing="tight" textShadow={plan.highlight ? '0 2px 12px rgba(128,90,213,0.18)' : undefined}>
              {plan.name}
            </Heading>
            <Text fontSize="2xl" fontWeight="extrabold" mb={3} letterSpacing="tight" textShadow={plan.highlight ? '0 2px 12px rgba(128,90,213,0.18)' : undefined}>
              {plan.price}
            </Text>
            <List spacing={3} mb={7}>
              {plan.features.map((feature) => (
                <ListItem key={feature} display="flex" alignItems="center" justifyContent="center" fontSize="md" fontWeight="medium">
                  <ListIcon as={IoCheckmarkCircle} color={plan.highlight ? "green.200" : "green.400"} boxSize={5} mr={2} />
                  {feature}
                </ListItem>
              ))}
            </List>
            <Button
              size="md"
              w="full"
              py={5}
              fontSize="lg"
              bgGradient={plan.highlight ? "linear(to-r, purple.500, blue.500)" : "linear(to-r, gray.300, gray.400)"}
              color={plan.highlight ? "white" : "gray.700"}
              fontWeight="bold"
              borderRadius="xl"
              letterSpacing="wide"
              _hover={{
                bgGradient: plan.highlight
                  ? "linear(to-r, purple.600, blue.600)"
                  : "linear(to-r, gray.400, gray.500)",
                transform: "translateY(-2px) scale(1.04)",
                boxShadow: plan.highlight ? "0 6px 24px rgba(128,90,213,0.18)" : undefined,
              }}
              boxShadow={plan.highlight ? "0 2px 12px rgba(128,90,213,0.18)" : undefined}
            >
              {plan.button}
            </Button>
          </Box>
        ))}
      </Flex>
      <Text mt={12} textAlign="center" color="gray.500" fontSize="md" fontWeight="medium" zIndex={2} position="relative">
        7-day money-back guarantee. Cancel anytime.
      </Text>
    </Box>
  );
};

export default PricingPlans;