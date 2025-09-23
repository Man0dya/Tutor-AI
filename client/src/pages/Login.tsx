import { useState } from 'react'
import { Box, Button, Container, FormControl, FormLabel, Heading, Input, Link, Stack, Text, useToast } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const toast = useToast()
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

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
    <Box>
      <Navbar />
      <Container maxW="md" py={12}>
        <Stack spacing={6}>
          <Heading>Welcome back</Heading>
          <Box as="form" onSubmit={onSubmit} p={6} borderWidth="1px" rounded="lg">
            <Stack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Password</FormLabel>
                <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
              </FormControl>
              <Button type="submit" colorScheme="teal" isLoading={loading}>Log in</Button>
              <Text fontSize="sm">No account? <Link as={RouterLink} to="/signup" color="teal.500">Sign up</Link></Text>
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}
