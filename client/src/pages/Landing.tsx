import { Box, Button, Container, Flex, Heading, HStack, Stack, Text, Icon, SimpleGrid } from '@chakra-ui/react'
import { Link as RouterLink, Navigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { MdAutoAwesome, MdQuiz, MdTrendingUp } from 'react-icons/md'

export default function Landing() {
  const { user } = useAuth()
  if (user) {
    return <Navigate to="/dashboard" replace />
  }
  return (
    <Box bg="#fafafa" minH="100vh">
      <Navbar />
      <Container maxW="7xl" py={20}>
        <Stack spacing={12} textAlign="center">
          <Stack spacing={6}>
            <Heading 
              size="3xl" 
              bgGradient="linear(to-r, purple.600, blue.500, teal.400)"
              bgClip="text"
              fontWeight="bold"
              lineHeight="1.2"
            >
              Your AI‑Powered Learning Companion
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="2xl" mx="auto" lineHeight="1.6">
              Transform your learning experience with AI-generated study materials, 
              intelligent question sets, and personalized feedback that adapts to your pace.
            </Text>
          </Stack>
          
          <HStack spacing={4} justify="center">
            <Button 
              as={RouterLink} 
              to="/signup" 
              size="lg"
              px={8}
              py={6}
              fontSize="lg"
              bgGradient="linear(to-r, purple.500, blue.500)"
              color="white"
              borderRadius="12px"
              className="btn-professional"
              _hover={{
                bgGradient: "linear(to-r, purple.600, blue.600)",
                transform: "translateY(-2px)",
              }}
            >
              Get Started Free
            </Button>
            <Button 
              as={RouterLink} 
              to="/login" 
              size="lg"
              px={8}
              py={6}
              fontSize="lg"
              variant="outline"
              borderRadius="12px"
              borderWidth="2px"
              borderColor="purple.500"
              color="purple.500"
              className="btn-professional"
              _hover={{
                bg: "purple.50",
                transform: "translateY(-2px)",
              }}
            >
              Sign In
            </Button>
          </HStack>
        </Stack>

        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} mt={20}>
          {[
            { 
              title: 'Smart Content Generator', 
              desc: 'AI creates personalized study materials tailored to your learning objectives and difficulty preferences.',
              icon: MdAutoAwesome,
              gradient: 'linear(to-br, purple.400, purple.600)'
            },
            { 
              title: 'Intelligent Questions', 
              desc: 'Generate diverse question types with adaptive difficulty and comprehensive explanations.',
              icon: MdQuiz,
              gradient: 'linear(to-br, blue.400, blue.600)'
            },
            { 
              title: 'Performance Analytics', 
              desc: 'Track your progress with detailed feedback and personalized improvement suggestions.',
              icon: MdTrendingUp,
              gradient: 'linear(to-br, teal.400, teal.600)'
            },
          ].map((feature, index) => (
            <Box 
              key={feature.title} 
              bg="white"
              p={8} 
              borderRadius="16px" 
              boxShadow="0 4px 16px rgba(0, 0, 0, 0.08)"
              border="1px solid #e2e8f0"
              textAlign="center"
              position="relative"
              className="professional-card"
              _hover={{
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)'
              }}
              transition="all 0.3s ease"
            >
              <Flex 
                align="center" 
                justify="center" 
                w={16} 
                h={16} 
                borderRadius="16px"
                bgGradient={feature.gradient}
                mx="auto"
                mb={6}
              >
                <Icon as={feature.icon} boxSize={8} color="white" />
              </Flex>
              <Heading size="lg" mb={4} color="gray.800">{feature.title}</Heading>
              <Text color="gray.600" fontSize="md" lineHeight="1.6">{feature.desc}</Text>
            </Box>
          ))}
        </SimpleGrid>

        <Box textAlign="center" mt={16} py={12}>
          <Text color="gray.500" fontSize="sm">
            Join thousands of learners who trust Tutor AI for their educational journey
          </Text>
        </Box>
      </Container>
    </Box>
  )
}
