import { Box, Button, Container, Flex, Heading, HStack, Stack, Text, Icon, SimpleGrid } from '@chakra-ui/react'
import { Link as RouterLink, Navigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { MdAutoAwesome, MdQuiz, MdTrendingUp } from 'react-icons/md'
import PricingPlans from '../components/PricingPlans';

export default function Landing() {
  const { user } = useAuth()
  if (user) {
    return <Navigate to="/dashboard" replace />
  }
  return (
    <Box
      minH="100vh"
      position="relative"
      overflow="hidden"
      bg="#fafafa"
    >
  {/* Animated gradient blobs for extra visual interest */}
      {/* Animated floating shapes for extra depth */}
      <Box
        position="absolute"
        top="30%"
        left="5%"
        w="80px"
        h="80px"
        zIndex={0}
        borderRadius="full"
        bgGradient="linear(to-br, purple.300, blue.200)"
        opacity={0.18}
        filter="blur(8px)"
        animation="float1 7s ease-in-out infinite alternate"
        sx={{
          '@keyframes float1': {
            '0%': { transform: 'translateY(0) scale(1)' },
            '100%': { transform: 'translateY(-30px) scale(1.15)' },
          },
        }}
      />
      <Box
        position="absolute"
        bottom="18%"
        right="12%"
        w="60px"
        h="60px"
        zIndex={0}
        borderRadius="full"
        bgGradient="linear(to-br, teal.200, blue.200)"
        opacity={0.15}
        filter="blur(6px)"
        animation="float2 9s ease-in-out infinite alternate"
        sx={{
          '@keyframes float2': {
            '0%': { transform: 'translateY(0) scale(1)' },
            '100%': { transform: 'translateY(24px) scale(1.12)' },
          },
        }}
      />
      <Box
        position="absolute"
        top="-120px"
        left="-120px"
        w="340px"
        h="340px"
        zIndex={0}
        filter="blur(60px)"
        opacity={0.45}
        bgGradient="radial(ellipse at 60% 40%, #a78bfa 0%, #8ec5fc 80%, transparent 100%)"
        animation="blob1 18s ease-in-out infinite alternate"
        sx={{
          '@keyframes blob1': {
            '0%': { transform: 'scale(1) translate(0,0)' },
            '100%': { transform: 'scale(1.2) translate(60px, 40px)' },
          },
        }}
      />
      <Box
        position="absolute"
        bottom="-100px"
        right="-100px"
        w="300px"
        h="300px"
        zIndex={0}
        filter="blur(70px)"
        opacity={0.35}
        bgGradient="radial(ellipse at 40% 60%, #5eead4 0%, #a78bfa 80%, transparent 100%)"
        animation="blob2 22s ease-in-out infinite alternate"
        sx={{
          '@keyframes blob2': {
            '0%': { transform: 'scale(1) translate(0,0)' },
            '100%': { transform: 'scale(1.15) translate(-40px, -30px)' },
          },
        }}
      />
      <Navbar />
  <Container maxW="7xl" py={20} position="relative" zIndex={1}>
  <Stack spacing={12} textAlign="center">
          <Stack spacing={6}>
            <Heading
              size="3xl"
              bgGradient="linear(to-r, purple.600, blue.500, teal.400)"
              bgClip="text"
              fontWeight="extrabold"
              lineHeight="1.2"
              letterSpacing="tight"
              textShadow="0 2px 16px rgba(128,90,213,0.08)"
              style={{ textTransform: 'uppercase', fontFamily: 'Poppins, Inter, sans-serif' }}
            >
              Your AI‑Powered Learning Companion
            </Heading>
            <Text
              fontSize={{ base: 'lg', md: 'xl' }}
              color="gray.600"
              maxW="2xl"
              mx="auto"
              lineHeight="1.6"
              fontWeight="medium"
              letterSpacing="wide"
              textShadow="0 1px 8px rgba(0,0,0,0.04)"
            >
              Transform your learning experience with <b>AI-generated study materials</b>, <b>intelligent question sets</b>, and <b>personalized feedback</b> that adapts to your pace.
            </Text>
          </Stack>
          
          <HStack spacing={4} justify="center">
            <Button
              as={RouterLink}
              to="/signup"
              size="lg"
              px={10}
              py={7}
              fontSize="xl"
              bgGradient="linear(to-r, purple.500, blue.500)"
              color="white"
              borderRadius="16px"
              boxShadow="0 4px 24px rgba(128,90,213,0.18)"
              fontWeight="bold"
              letterSpacing="wide"
              className="btn-professional"
              _hover={{
                bgGradient: "linear(to-r, purple.600, blue.600)",
                transform: "translateY(-4px) scale(1.04)",
                boxShadow: '0 8px 32px rgba(128,90,213,0.22)'
              }}
            >
              Get Started Free
            </Button>
            <Button
              as={RouterLink}
              to="/login"
              size="lg"
              px={10}
              py={7}
              fontSize="xl"
              variant="outline"
              borderRadius="16px"
              borderWidth="2px"
              borderColor="purple.500"
              color="purple.500"
              fontWeight="bold"
              letterSpacing="wide"
              className="btn-professional"
              _hover={{
                bg: "purple.50",
                transform: "translateY(-4px) scale(1.04)",
                boxShadow: '0 8px 32px rgba(128,90,213,0.10)'
              }}
            >
              Sign In
            </Button>
          </HStack>
        </Stack>

  {/* Decorative divider */}
  <Box w="100%" h="8px" bgGradient="linear(to-r, purple.400, blue.400, teal.400)" borderRadius="full" my={16} opacity={0.8} boxShadow="0 2px 12px rgba(128,90,213,0.10)" />

  <SimpleGrid columns={{ base: 1, md: 3 }} spacing={12} mt={10}>
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
              bg="rgba(255,255,255,0.85)"
              p={12}
              borderRadius="2xl"
              boxShadow="0 12px 48px rgba(128,90,213,0.13)"
              border="2px solid #e2e8f0"
              textAlign="center"
              position="relative"
              className="professional-card"
              backdropFilter="blur(8px)"
              _hover={{
                transform: 'translateY(-12px) scale(1.05)',
                boxShadow: '0 24px 64px rgba(128,90,213,0.22)'
              }}
              transition="all 0.3s cubic-bezier(.4,0,.2,1)"
            >
              <Flex
                align="center"
                justify="center"
                w={24}
                h={24}
                borderRadius="2xl"
                bgGradient={feature.gradient}
                mx="auto"
                mb={8}
                boxShadow="0 4px 24px rgba(128,90,213,0.16)"
              >
                <Icon as={feature.icon} boxSize={14} color="white" />
              </Flex>
              <Heading size="lg" mb={4} color="gray.800" fontWeight="extrabold">{feature.title}</Heading>
              <Text color="gray.600" fontSize="lg" lineHeight="1.8" fontWeight="medium">{feature.desc}</Text>
            </Box>
          ))}
        </SimpleGrid>

        

        

        {/* Pricing Plans Section */}
        <Box mt={20} position="relative" zIndex={2} animation="fadeInUp 1.2s cubic-bezier(.4,0,.2,1)">
          <Heading size="xl" mb={6} textAlign="center" color="gray.800" fontWeight="extrabold" letterSpacing="tight">
            Choose Your Plan
          </Heading>
          <PricingPlans />
          <style>{`
            @keyframes fadeInUp {
              0% { opacity: 0; transform: translateY(40px); }
              100% { opacity: 1; transform: translateY(0); }
            }
          `}</style>
        </Box>
      </Container>
    </Box>
  )
}