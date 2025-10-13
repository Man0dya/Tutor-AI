import { useState } from 'react'
import { Box, Button, Checkbox, Container, FormControl, FormLabel, Heading, HStack, Icon, IconButton, Input, InputGroup, InputRightElement, Link, Progress, Stack, Text, useDisclosure, useToast, VStack } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import AnimatedBackground from '../components/AnimatedBackground'
import { useAuth } from '../context/AuthContext'
import { getErrorMessage } from '../api/client'
import { MdPerson, MdMail, MdLock, MdVisibility, MdVisibilityOff, MdCheckCircle } from 'react-icons/md'

export default function Signup() {
  const toast = useToast()
  const navigate = useNavigate()
  const { signup } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { isOpen: showPassword, onToggle } = useDisclosure()

  const getPasswordStrength = (pwd: string): { score: number; label: string; color: string } => {
    let score = 0
    if (pwd.length >= 8) score += 25
    if (/[A-Z]/.test(pwd)) score += 20
    if (/[a-z]/.test(pwd)) score += 20
    if (/\d/.test(pwd)) score += 20
    if (/[^A-Za-z0-9]/.test(pwd)) score += 15
    if (score > 100) score = 100
    if (score >= 80) return { score, label: 'Strong', color: 'green' }
    if (score >= 55) return { score, label: 'Medium', color: 'yellow' }
    if (score > 0) return { score, label: 'Weak', color: 'red' }
    return { score: 0, label: '', color: 'gray' }
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await signup(name, email, password)
      toast({ title: 'Account created', status: 'success' })
      navigate('/dashboard')
    } catch (err: any) {
      toast({ title: 'Signup failed', description: getErrorMessage(err) || 'Try different email', status: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box minH="100vh" bg="bg" position="relative">
      <AnimatedBackground />
      <Box position="relative" zIndex={1}>
        <Navbar />
        <Container maxW="7xl" pt={{ base: 8, md: 12 }} pb={0}>
        <Stack direction={{ base: 'column', lg: 'row' }} spacing={{ base: 8, lg: 12 }} align="center" justify="center" minH="70vh">
          {/* Left Side Content */}
          <VStack align="flex-start" spacing={4} flex="1" maxW="lg" pt={{ base: 0, lg: 2 }}>
            {/* Text Section */}
            <VStack align="flex-start" spacing={3}>
              <Heading size="2xl" color="text" fontWeight="700" lineHeight="1.2">
                Create your account
              </Heading>
              <Text color="muted" fontSize="lg" lineHeight="1.6">
                Join thousands of students learning smarter with AI-powered tutoring and personalized content.
              </Text>
            </VStack>
            <Box h="1px" w="full" bg="border" />
            {/* Features Section */}
            <VStack align="flex-start" spacing={3}>
              <Text color="muted" fontSize="sm" fontWeight="600">
                What you'll get:
              </Text>
              <VStack align="flex-start" spacing={2}>
                <HStack>
                  <Icon as={MdCheckCircle} color="accent" boxSize={4} />
                  <Text color="muted" fontSize="sm">Personalized study content</Text>
                </HStack>
                <HStack>
                  <Icon as={MdCheckCircle} color="accent" boxSize={4} />
                  <Text color="muted" fontSize="sm">AI-powered practice questions</Text>
                </HStack>
                <HStack>
                  <Icon as={MdCheckCircle} color="accent" boxSize={4} />
                  <Text color="muted" fontSize="sm">Progress tracking & insights</Text>
                </HStack>
              </VStack>
            </VStack>
            <Text color="muted" fontSize="sm" fontWeight="500">
              Free to start. No credit card required.
            </Text>
          </VStack>

          {/* Right Side Form */}
          <Box
            as="form"
            onSubmit={onSubmit}
            flex="1"
            maxW="md"
            bg="surface"
            p={6}
            borderRadius="xl"
            border="1px"
            borderColor="border"
            boxShadow="sm"
            mt={{ base: 0, lg: 8 }}
          >
            <Stack spacing={6}>
              <VStack align="flex-start" spacing={2}>
                <Heading size="lg" color="text" fontWeight="600">
                  Get started
                </Heading>
                <Text color="muted" fontSize="sm">
                  Create your account to begin your learning journey
                </Text>
              </VStack>

              <FormControl isRequired>
                <FormLabel color="muted" fontWeight="600" fontSize="sm" textTransform="uppercase" letterSpacing="wide">
                  Full Name
                </FormLabel>
                <InputGroup>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your full name"
                    size="lg"
                    borderRadius="lg"
                    borderColor="border"
                    focusBorderColor="accent"
                    _hover={{ borderColor: 'border' }}
                  />
                  <InputRightElement>
                    <Icon as={MdPerson} color="muted" boxSize={5} />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <FormControl isRequired>
                <FormLabel color="muted" fontWeight="600" fontSize="sm" textTransform="uppercase" letterSpacing="wide">
                  Email
                </FormLabel>
                <InputGroup>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    size="lg"
                    borderRadius="lg"
                    borderColor="border"
                    focusBorderColor="accent"
                    _hover={{ borderColor: 'border' }}
                  />
                  <InputRightElement>
                    <Icon as={MdMail} color="muted" boxSize={5} />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <FormControl isRequired>
                <FormLabel color="muted" fontWeight="600" fontSize="sm" textTransform="uppercase" letterSpacing="wide">
                  Password
                </FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Create a strong password"
                    size="lg"
                    borderRadius="lg"
                    borderColor="border"
                    focusBorderColor="accent"
                    _hover={{ borderColor: 'border' }}
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      variant="ghost"
                      size="sm"
                      icon={<Icon as={showPassword ? MdVisibilityOff : MdVisibility} />}
                      onClick={onToggle}
                      _hover={{ bg: 'transparent' }}
                    />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              {password && (
                <Box>
                  {(() => {
                    const ps = getPasswordStrength(password)
                    return (
                      <VStack spacing={2} align="stretch">
                        <HStack justify="space-between">
                          <Text fontSize="xs" color="muted" fontWeight="500">
                            Password strength
                          </Text>
                          <Text fontSize="xs" color={`${ps.color}.400`} _dark={{ color: `${ps.color}.300` }} fontWeight="600">
                            {ps.label}
                          </Text>
                        </HStack>
                        <Progress
                          value={ps.score}
                          colorScheme={ps.color as any}
                          size="sm"
                          borderRadius="md"
                          bg="gray.100"
                          _dark={{ bg: 'gray.700' }}
                        />
                      </VStack>
                    )
                  })()}
                </Box>
              )}

              <Checkbox
                colorScheme="purple"
                size="md"
                defaultChecked
                sx={{
                  '& .chakra-checkbox__control': {
                    borderColor: 'border',
                    _checked: {
                      bg: 'accent',
                      borderColor: 'accent'
                    }
                  }
                }}
              >
                <Text fontSize="sm" color="muted">
                  I agree to the{' '}
                  <Link
                    color="accent"
                    fontWeight="500"
                    _hover={{ textDecoration: 'underline' }}
                  >
                    Terms of Service
                  </Link>
                  {' '}and{' '}
                  <Link
                    color="accent"
                    fontWeight="500"
                    _hover={{ textDecoration: 'underline' }}
                  >
                    Privacy Policy
                  </Link>
                </Text>
              </Checkbox>

              <Button
                type="submit"
                colorScheme="purple"
                isLoading={loading}
                size="lg"
                w="full"
                borderRadius="lg"
                fontWeight="600"
                py={6}
                _hover={{
                  transform: "translateY(-1px)",
                  boxShadow: "md"
                }}
                transition="all 0.2s"
              >
                Create account
              </Button>

              <Text fontSize="sm" color="muted" textAlign="center">
                Already have an account?{' '}
                <Link
                  as={RouterLink}
                  to="/login"
                  color="accent"
                  fontWeight="600"
                  _hover={{ textDecoration: 'underline' }}
                >
                  Sign in
                </Link>
              </Text>
            </Stack>
          </Box>
        </Stack>
      </Container>
      </Box>
    </Box>
  )
}
