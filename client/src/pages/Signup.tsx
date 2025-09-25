import { useState } from 'react'
import { Box, Button, Checkbox, Container, FormControl, FormLabel, Heading, HStack, Icon, IconButton, Input, InputGroup, InputRightElement, Link, Stack, Text, Textarea, useDisclosure, useToast, VStack } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../context/AuthContext'
import { getErrorMessage } from '../api/client'
import { MdPerson, MdMail, MdLock, MdVisibility, MdVisibilityOff } from 'react-icons/md'

export default function Signup() {
  const toast = useToast()
  const navigate = useNavigate()
  const { signup } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { isOpen: showPassword, onToggle } = useDisclosure()

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
    <Box bgGradient={{ base: 'linear(to-b, white, teal.50)', md: 'linear(to-r, white, teal.50)' }} minH="100vh">
      <Navbar />
      <Container maxW="6xl" py={{ base: 8, md: 16 }}>
        <Stack direction={{ base: 'column', md: 'row' }} spacing={{ base: 8, md: 16 }} align="center">
          <VStack align="flex-start" spacing={4} flex="1" display={{ base: 'none', md: 'flex' }}>
            <HStack>
              <Icon as={MdPerson} color="teal.500" boxSize={7} />
              <Heading size="lg" color="gray.800">Create your account</Heading>
            </HStack>
            <Text color="gray.600">Join to generate tailored content, practice effectively, and track progress.</Text>
            <Box h="1px" w="80%" bg="teal.200" borderRadius="full" />
            <Text color="gray.500" fontSize="sm">Takes less than a minute. No credit card required.</Text>
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
                  <Icon as={MdPerson} color="teal.500" boxSize={6} />
                  <Heading size="md" color="gray.800">Create your account</Heading>
                </HStack>
                <Text color="gray.600" fontSize="sm">It’s quick and easy</Text>
              </VStack>

              <FormControl isRequired>
                <FormLabel>Name</FormLabel>
                <InputGroup>
                  <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" pr={10} />
                  <InputRightElement pointerEvents="none">
                    <Icon as={MdPerson} color="gray.400" />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

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
                <Checkbox defaultChecked>I agree to the Terms</Checkbox>
                <Link color="teal.600" as={RouterLink} to="#">View policy</Link>
              </HStack>

              <Button type="submit" colorScheme="teal" isLoading={loading} size="lg" borderRadius="12px">Create account</Button>

              <Text fontSize="sm" color="gray.600">Already have an account? <Link as={RouterLink} to="/login" color="teal.600" fontWeight="600">Log in</Link></Text>
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}
