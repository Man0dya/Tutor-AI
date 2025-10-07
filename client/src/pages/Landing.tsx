import { 
  Box, 
  Button, 
  Container, 
  Flex, 
  Heading, 
  HStack, 
  Stack, 
  Text, 
  Icon, 
  SimpleGrid,
  VStack,
  Badge,
  Divider
} from '@chakra-ui/react'
import { Link as RouterLink, Navigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { 
  MdAutoAwesome, 
  MdQuiz, 
  MdTrendingUp, 
  MdRocketLaunch,
  MdSchool,
  MdSpeed
} from 'react-icons/md'
import PricingPlans from '../components/PricingPlans';

export default function Landing() {
  const { user } = useAuth()
  if (user) {
    return <Navigate to="/dashboard" replace />
  }
  
  return (
    <Box minH="100vh" bg="white">
      <Navbar />
      
      {/* Hero Section */}
      <Container maxW="8xl" py={{ base: 16, md: 24 }}>
        <VStack spacing={12} textAlign="center">
          {/* Main Hero Content */}
          <Stack spacing={8} maxW="6xl">
            <Heading
              fontSize={{ base: '5xl', md: '7xl', lg: '8xl' }}
              fontWeight="800"
              lineHeight="1.1"
              color="gray.900"
              letterSpacing="tight"
            >
              Learn Smarter with{' '}
              <Text 
                as="span" 
                bgGradient="linear(to-r, purple.600, blue.500)"
                bgClip="text"
              >
                AI-Powered
              </Text>
              {' '}Tutoring
            </Heading>
            
            <Text
              fontSize={{ base: 'lg', md: 'xl' }}
              color="gray.600"
              maxW="3xl"
              mx="auto"
              lineHeight="1.7"
              fontWeight="400"
            >
              Transform your learning experience with personalized AI-generated study materials, 
              intelligent assessments, and detailed feedback that adapts to your unique learning style.
            </Text>
          </Stack>
          
          {/* CTA Buttons */}
          <HStack spacing={4} flexWrap="wrap" justify="center">
            <Button
              as={RouterLink}
              to="/signup"
              size="lg"
              px={8}
              py={6}
              fontSize="lg"
              bg="purple.600"
              color="white"
              borderRadius="xl"
              fontWeight="600"
              _hover={{
                bg: "purple.700",
                transform: "translateY(-2px)",
                boxShadow: "lg"
              }}
              transition="all 0.2s"
              leftIcon={<MdRocketLaunch />}
            >
              Start Learning Free
            </Button>
            <Button
              as={RouterLink}
              to="/login"
              size="lg"
              px={8}
              py={6}
              fontSize="lg"
              variant="outline"
              borderColor="gray.300"
              color="gray.700"
              borderRadius="xl"
              fontWeight="600"
              _hover={{
                bg: "gray.50",
                borderColor: "gray.400",
                transform: "translateY(-2px)"
              }}
              transition="all 0.2s"
            >
              Sign In
            </Button>
          </HStack>
        </VStack>
      </Container>

      {/* Features Section */}
      <Container maxW="6xl" py={{ base: 16, md: 24 }}>
        <VStack spacing={16}>
          {/* Section Header */}
          <Stack spacing={4} textAlign="center" maxW="3xl">
            <Heading
              fontSize={{ base: '3xl', md: '4xl' }}
              fontWeight="700"
              color="gray.900"
            >
              Everything you need to excel
            </Heading>
            <Text fontSize="xl" color="gray.600" lineHeight="1.6">
              Our AI-powered platform provides comprehensive tools to enhance your learning journey
            </Text>
          </Stack>

            {/* Features Grid */}
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} w="full">
              {[
                {
                  icon: MdAutoAwesome,
                  title: 'Smart Content Generation',
                  description: 'AI creates personalized study materials tailored to your learning objectives and current skill level.',
                  color: 'purple.500'
                },
                {
                  icon: MdQuiz,
                  title: 'Intelligent Assessments',
                  description: 'Generate diverse question types with adaptive difficulty and comprehensive explanations.',
                  color: 'blue.500'
                },
                {
                  icon: MdTrendingUp,
                  title: 'Progress Analytics',
                  description: 'Track your learning progress with detailed insights and personalized improvement recommendations.',
                  color: 'green.500'
                }
              ].map((feature, index) => (
                <Box
                  key={index}
                  bg="white"
                  p={8}
                  borderRadius="2xl"
                  boxShadow="sm"
                  border="1px"
                  borderColor="gray.200"
                  textAlign="center"
                  _hover={{
                    boxShadow: "md",
                    transform: "translateY(-4px)"
                  }}
                  transition="all 0.2s"
                >
                  <Flex
                    align="center"
                    justify="center"
                    w={16}
                    h={16}
                    bg={`${feature.color.split('.')[0]}.50`}
                    borderRadius="xl"
                    mx="auto"
                    mb={6}
                  >
                    <Icon as={feature.icon} boxSize={8} color={feature.color} />
                  </Flex>
                  <Heading size="md" mb={4} color="gray.900" fontWeight="600">
                    {feature.title}
                  </Heading>
                  <Text color="gray.600" lineHeight="1.6">
                    {feature.description}
                  </Text>
                </Box>
              ))}
            </SimpleGrid>
        </VStack>
      </Container>

      {/* How it Works Section */}
      <Container maxW="6xl" py={{ base: 16, md: 24 }}>
        <VStack spacing={16}>
          <Stack spacing={4} textAlign="center" maxW="3xl">
            <Heading
              fontSize={{ base: '3xl', md: '4xl' }}
              fontWeight="700"
              color="gray.900"
            >
              How Tutor AI Works
            </Heading>
            <Text fontSize="xl" color="gray.600" lineHeight="1.6">
              Get started in three simple steps and transform your learning experience
            </Text>
          </Stack>

          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={12} w="full">
            {[
              {
                step: '01',
                icon: MdSchool,
                title: 'Choose Your Subject',
                description: 'Select the topic you want to learn and set your learning goals and preferences.'
              },
              {
                step: '02',
                icon: MdAutoAwesome,
                title: 'AI Generates Content',
                description: 'Our AI creates personalized study materials, questions, and assessments just for you.'
              },
              {
                step: '03',
                icon: MdSpeed,
                title: 'Learn & Improve',
                description: 'Study with AI-powered feedback and track your progress as you master new concepts.'
              }
            ].map((step, index) => (
              <VStack key={index} spacing={6} textAlign="center">
                <Flex
                  align="center"
                  justify="center"
                  w={20}
                  h={20}
                  bg="purple.600"
                  borderRadius="full"
                  position="relative"
                >
                  <Text
                    position="absolute"
                    top="-8px"
                    right="-8px"
                    bg="white"
                    color="purple.600"
                    fontSize="sm"
                    fontWeight="bold"
                    w={8}
                    h={8}
                    borderRadius="full"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    border="2px"
                    borderColor="purple.600"
                  >
                    {step.step}
                  </Text>
                  <Icon as={step.icon} boxSize={10} color="white" />
                </Flex>
                <VStack spacing={3}>
                  <Heading size="md" color="gray.900" fontWeight="600">
                    {step.title}
                  </Heading>
                  <Text color="gray.600" lineHeight="1.6" maxW="sm">
                    {step.description}
                  </Text>
                </VStack>
              </VStack>
            ))}
          </SimpleGrid>
        </VStack>
      </Container>

      {/* Pricing Section */}
      <Container maxW="6xl" py={{ base: 16, md: 24 }}>
        <VStack spacing={16}>
          <Stack spacing={4} textAlign="center" maxW="3xl">
            <Heading
              fontSize={{ base: '3xl', md: '4xl' }}
              fontWeight="700"
              color="gray.900"
            >
              Choose Your Learning Plan
            </Heading>
            <Text fontSize="xl" color="gray.600" lineHeight="1.6">
              Start free and upgrade as you grow. All plans include our core AI features.
            </Text>
          </Stack>
          <PricingPlans />
        </VStack>
      </Container>

      {/* CTA Section */}
      <Container maxW="4xl" py={{ base: 16, md: 24 }}>
        <Box
          bg="purple.600"
          borderRadius="3xl"
          p={{ base: 12, md: 16 }}
          textAlign="center"
          color="white"
        >
          <VStack spacing={8}>
            <Stack spacing={4}>
              <Heading
                fontSize={{ base: '3xl', md: '4xl' }}
                fontWeight="700"
              >
                Ready to revolutionize your learning?
              </Heading>
              <Text fontSize="xl" opacity={0.9} maxW="2xl">
                Join thousands of students who are already learning smarter with AI. 
                Start your free trial today.
              </Text>
            </Stack>
            <Button
              as={RouterLink}
              to="/signup"
              size="lg"
              px={10}
              py={6}
              fontSize="lg"
              bg="white"
              color="purple.600"
              borderRadius="xl"
              fontWeight="600"
              _hover={{
                transform: "translateY(-2px)",
                boxShadow: "xl"
              }}
              transition="all 0.2s"
              leftIcon={<MdRocketLaunch />}
            >
              Get Started Free
            </Button>
          </VStack>
        </Box>
      </Container>

      {/* Footer */}
      <Box borderTop="1px" borderColor="gray.200" py={8}>
        <Container maxW="6xl">
          <Flex
            direction={{ base: 'column', md: 'row' }}
            justify="space-between"
            align="center"
            gap={4}
          >
            <Text color="gray.600" fontSize="sm">
              © 2025 Tutor AI. All rights reserved.
            </Text>
            <HStack spacing={6}>
              <Text as="a" href="#" color="gray.600" fontSize="sm" _hover={{ color: 'purple.600' }}>
                Privacy Policy
              </Text>
              <Text as="a" href="#" color="gray.600" fontSize="sm" _hover={{ color: 'purple.600' }}>
                Terms of Service
              </Text>
              <Text as="a" href="#" color="gray.600" fontSize="sm" _hover={{ color: 'purple.600' }}>
                Contact
              </Text>
            </HStack>
          </Flex>
        </Container>
      </Box>
    </Box>
  )
}