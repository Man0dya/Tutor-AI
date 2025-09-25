import { Box, Button, Flex, HStack, Heading, Spacer, Avatar, Text } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <Box 
      as="header" 
      bg="white" 
      borderBottomWidth="1px" 
      borderColor="gray.200"
      py={4} 
      px={6}
      boxShadow="0 1px 3px rgba(0, 0, 0, 0.05)"
    >
      <Flex align="center" gap={4}>
        <Heading 
          size="lg" 
          bgGradient="linear(to-r, purple.500, blue.500)"
          bgClip="text"
          fontWeight="bold"
        >
          <RouterLink to={user ? '/dashboard' : '/'}>Tutor AI</RouterLink>
        </Heading>
        <Spacer />
        {user ? (
          <HStack spacing={4}>
            <Flex align="center" gap={3}>
              <Avatar size="sm" name={user.email} bg="purple.500" />
              <Text fontSize="sm" fontWeight="500" color="gray.700">{user.email}</Text>
            </Flex>
            <Button 
              onClick={() => { logout(); navigate('/'); }} 
              colorScheme="red" 
              variant="outline" 
              size="sm"
              borderRadius="8px"
              className="btn-professional"
            >
              Logout
            </Button>
          </HStack>
        ) : (
          <HStack spacing={3}>
            <Button 
              as={RouterLink} 
              to="/login" 
              size="sm" 
              variant="outline"
              borderRadius="8px"
              className="btn-professional"
            >
              Login
            </Button>
            <Button 
              as={RouterLink} 
              to="/signup" 
              size="sm" 
              colorScheme="purple"
              borderRadius="8px"
              className="btn-professional"
            >
              Sign Up
            </Button>
          </HStack>
        )}
      </Flex>
    </Box>
  )
}
