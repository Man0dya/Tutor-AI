import { useState } from 'react'
import { Box, Button, Checkbox, Container, FormControl, FormLabel, Heading, HStack, Icon, IconButton, Input, InputGroup, InputRightElement, Link, Stack, Text, useDisclosure, useToast, VStack } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { MdLock, MdMail, MdVisibility, MdVisibilityOff } from 'react-icons/md'

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
    <Box bgGradient={{ base: 'linear(to-b, white, purple.50)', md: 'linear(to-r, white, purple.50)' }} minH="100vh">
      <Navbar />
      <Container maxW="6xl" py={{ base: 8, md: 16 }}>
        <Stack direction={{ base: 'column', md: 'row' }} spacing={{ base: 8, md: 16 }} align="center">
          <VStack align="flex-start" spacing={4} flex="1" display={{ base: 'none', md: 'flex' }}>
            <HStack>
              <Icon as={MdLock} color="purple.500" boxSize={7} />
              <Heading size="lg" color="gray.800">Welcome back</Heading>
            </HStack>
            <Text color="gray.600">Sign in to continue learning with personalized content, practice questions, and progress tracking.</Text>
            <Box h="1px" w="80%" bg="purple.200" borderRadius="full" />
            <Text color="gray.500" fontSize="sm">Secure authentication. Your data stays private.</Text>
          </VStack>

          <Box
            as="form"
            onSubmit={onSubmit}
            flex="1"
            bg="white"
            p={{ base: 6, md: 8 }}
            borderWidth="1px"
            borderColor="gray.200"
            borderRadius="16px"
            boxShadow="0 6px 20px rgba(0,0,0,0.06)"
          >
            <Stack spacing={6}>
              <VStack align="flex-start" spacing={1} display={{ base: 'flex', md: 'none' }}>
                <HStack>
                  <Icon as={MdLock} color="purple.500" boxSize={6} />
                  <Heading size="md" color="gray.800">Welcome back</Heading>
                </HStack>
                <Text color="gray.600" fontSize="sm">Sign in to continue</Text>
              </VStack>

              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <InputGroup>
                  <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" pr={10} />
                  <InputRightElement pointerEvents="none">
                    <Icon as={MdMail} color="gray.400" />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" pr={10} />
                  <InputRightElement>
                    <IconButton aria-label={showPassword ? 'Hide password' : 'Show password'} variant="ghost" size="sm" icon={<Icon as={showPassword ? MdVisibilityOff : MdVisibility} />} onClick={onToggle} />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <HStack justify="space-between">
                <Checkbox defaultChecked>Remember me</Checkbox>
                <Link color="purple.600" as={RouterLink} to="#">Forgot password?</Link>
              </HStack>

              <Button type="submit" colorScheme="purple" isLoading={loading} size="lg" borderRadius="12px">Log in</Button>

              <Text fontSize="sm" color="gray.600">No account? <Link as={RouterLink} to="/signup" color="purple.600" fontWeight="600">Create one</Link></Text>
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}
