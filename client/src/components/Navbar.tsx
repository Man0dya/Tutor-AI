import { Box, Button, Flex, HStack, Heading, Spacer } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <Box as="header" borderBottomWidth="1px" py={3} px={4}>
      <Flex align="center" gap={4}>
        <Heading size="md">
          <RouterLink to="/">Tutor AI</RouterLink>
        </Heading>
        <HStack spacing={4}>
          <Button as={RouterLink} to="/" variant="ghost">Home</Button>
          {user && (
            <>
              <Button as={RouterLink} to="/dashboard" variant="ghost">Dashboard</Button>
              <Button as={RouterLink} to="/content" variant="ghost">Content</Button>
              <Button as={RouterLink} to="/questions" variant="ghost">Questions</Button>
              <Button as={RouterLink} to="/progress" variant="ghost">Progress</Button>
            </>
          )}
        </HStack>
        <Spacer />
        {user ? (
          <HStack>
            <Box fontSize="sm">{user.email}</Box>
            <Button onClick={() => { logout(); navigate('/'); }} colorScheme="red" variant="outline" size="sm">Logout</Button>
          </HStack>
        ) : (
          <HStack>
            <Button as={RouterLink} to="/login" size="sm" variant="outline">Login</Button>
            <Button as={RouterLink} to="/signup" size="sm" colorScheme="teal">Sign Up</Button>
          </HStack>
        )}
      </Flex>
    </Box>
  )
}
