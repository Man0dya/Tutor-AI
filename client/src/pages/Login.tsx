import { useState } from 'react'
import { Box, Button, Checkbox, Container, FormControl, FormLabel, Heading, HStack, Icon, IconButton, Input, InputGroup, InputRightElement, Link, Stack, Text, useDisclosure, useToast, VStack } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { MdMail, MdVisibility, MdVisibilityOff } from 'react-icons/md'

export default function Login() {
  const toast = useToast()
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { isOpen: showPassword, onToggle } = useDisclosure()

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      toast({ title: 'Logged in', status: 'success' })
      navigate('/dashboard')
    } catch (err: any) {
      toast({ title: 'Login failed', description: err?.response?.data?.detail || 'Check your credentials', status: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box minH="100vh" bg="bg">
      <Navbar />
      <Container maxW="7xl" pt={{ base: 8, md: 12 }} pb={0}>
        <Stack direction={{ base: 'column', lg: 'row' }} spacing={{ base: 8, lg: 12 }} align="center" justify="center" minH="70vh">
          {/* Left Side Content */}
          <VStack align="flex-start" spacing={4} flex="1" maxW="lg" pt={{ base: 0, lg: 2 }}>
            {/* Text Section */}
            <VStack align="flex-start" spacing={3}>
              <Heading size="2xl" color="text" fontWeight="700" lineHeight="1.2">
                Welcome back
              </Heading>
              <Text color="muted" fontSize="lg" lineHeight="1.6">
                Sign in to continue learning with personalized content, practice questions, and progress tracking.
              </Text>
            </VStack>
            <Box h="1px" w="full" bg="border" />
            <Text color="muted" fontSize="sm" fontWeight="500">
              Secure authentication. Your data stays private.
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
                  Sign in to your account
                </Heading>
                <Text color="muted" fontSize="sm">
                  Enter your credentials to access your dashboard
                </Text>
              </VStack>

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
                    placeholder="Enter your password"
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

              <HStack justify="space-between" align="center">
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
                  <Text fontSize="sm" color="muted">Remember me</Text>
                </Checkbox>
                <Link
                  color="accent"
                  fontSize="sm"
                  fontWeight="500"
                  _hover={{ textDecoration: 'underline' }}
                >
                  Forgot password?
                </Link>
              </HStack>

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
                Sign in
              </Button>

              <Text fontSize="sm" color="muted" textAlign="center">
                Don't have an account?{' '}
                <Link
                  as={RouterLink}
                  to="/signup"
                  color="accent"
                  fontWeight="600"
                  _hover={{ textDecoration: 'underline' }}
                >
                  Sign up
                </Link>
              </Text>
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}
