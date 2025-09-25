import React from "react";
import { Box, Button, Flex, Heading, Text, List, ListItem, ListIcon, useColorModeValue, Icon } from "@chakra-ui/react";
import { CheckCircleIcon, StarIcon, AtSignIcon } from "@chakra-ui/icons";

const plans = [
  {
    name: "Free",
    price: "$0/month",
    icon: AtSignIcon,
    features: [
      "10 free question generations",
      "5 free feedback evaluations",
      "Basic features",
    ],
    gradient: "linear(to-br, gray.100, gray.50)",
    color: "gray.700",
    border: "2px solid #e2e8f0",
    button: "Choose Plan",
    highlight: false,
  },
  {
    name: "Pro",
    price: "$9.99/month",
    icon: StarIcon,
    features: [
      "Unlimited question generations",
      "Unlimited feedback evaluations",
      "Priority support",
    ],
    gradient: "linear(to-br, purple.400, blue.400)",
    color: "white",
    border: "2px solid #805ad5",
    button: "Choose Plan",
    highlight: true,
  },
  {
    name: "Enterprise",
    price: "$29.99/month",
    icon: CheckCircleIcon,
    features: [
      "Custom AI models",
      "Team access",
      "Dedicated support",
    ],
    gradient: "linear(to-br, blue.400, teal.400)",
    color: "white",
    border: "2px solid #319795",
    button: "Choose Plan",
    highlight: false,
  },
];

const PricingPlans: React.FC = () => {
  const cardBg = useColorModeValue("white", "gray.800");
  return (
    <Flex direction={{ base: "column", md: "row" }} gap={8} justify="center" align="center" py={8}>
      {plans.map((plan) => (
        <Box
          key={plan.name}
          bg={plan.highlight ? 'rgba(128,90,213,0.10)' : 'rgba(255,255,255,0.92)'}
          bgGradient={plan.gradient}
          color={plan.color}
          borderRadius="2xl"
          boxShadow={plan.highlight ? "0 24px 64px 0 rgba(128,90,213,0.22)" : "0 4px 16px rgba(0,0,0,0.08)"}
          border={plan.border}
          p={14}
          w={{ base: "95vw", sm: "370px" }}
          maxW="400px"
          textAlign="center"
          position="relative"
          zIndex={plan.highlight ? 2 : 1}
          backdropFilter="blur(12px)"
          _before={plan.highlight ? {
            content: '""',
            position: 'absolute',
            top: '-22px',
            left: '50%',
            transform: 'translateX(-50%)',
            w: '90%',
            h: '22px',
            bgGradient: 'linear(to-r, purple.400, blue.400, teal.400)',
            borderRadius: 'full',
            filter: 'blur(10px)',
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
            transform: 'translateY(-16px) scale(1.07)',
            boxShadow: plan.highlight
              ? '0 40px 120px 0 rgba(128,90,213,0.32)'
              : '0 16px 48px rgba(0,0,0,0.16)',
          }}
          transition="all 0.3s cubic-bezier(.4,0,.2,1)"
        >
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
          <Flex align="center" justify="center" mb={6}>
            <Icon as={plan.icon} boxSize={10} color={plan.highlight ? 'yellow.300' : 'purple.400'} />
          </Flex>
          <Heading size="lg" mb={2} fontWeight="extrabold" letterSpacing="tight" textShadow={plan.highlight ? '0 2px 12px rgba(128,90,213,0.18)' : undefined}>
            {plan.name}
          </Heading>
          <Text fontSize="4xl" fontWeight="extrabold" mb={4} letterSpacing="tight" textShadow={plan.highlight ? '0 2px 12px rgba(128,90,213,0.18)' : undefined}>
            {plan.price}
          </Text>
          <List spacing={5} mb={12}>
            {plan.features.map((feature) => (
              <ListItem key={feature} display="flex" alignItems="center" justifyContent="center" fontSize="lg" fontWeight="medium">
                <ListIcon as={CheckCircleIcon} color={plan.highlight ? "green.200" : "green.400"} boxSize={6} mr={2} />
                {feature}
              </ListItem>
            ))}
          </List>
          <Button
            size="lg"
            w="full"
            py={8}
            fontSize="xl"
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
  );
};

export default PricingPlans;