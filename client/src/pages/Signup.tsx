import { useState } from 'react'
import { Box, Button, Container, FormControl, FormLabel, Heading, Input, Link, Stack, Text, useToast } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { getErrorMessage } from '../api/client'

export default function Signup() {
  const toast = useToast()
  const navigate = useNavigate()
  const { signup } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

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
    <Box>
      <Navbar />
      <Container maxW="md" py={12}>
        <Stack spacing={6}>
          <Heading>Create your account</Heading>
          <Box as="form" onSubmit={onSubmit} p={6} borderWidth="1px" rounded="lg">
            <Stack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Name</FormLabel>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" />
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Password</FormLabel>
                <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
              </FormControl>
              <Button type="submit" colorScheme="teal" isLoading={loading}>Create account</Button>
              <Text fontSize="sm">Already have an account? <Link as={RouterLink} to="/login" color="teal.500">Log in</Link></Text>
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}
