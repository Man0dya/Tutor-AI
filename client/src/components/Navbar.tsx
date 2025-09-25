import { Box, Button, Flex, HStack, Heading, Spacer, Avatar, Text, useDisclosure } from '@chakra-ui/react'
import { useEffect } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Badge } from '@chakra-ui/react'
import { createBillingPortal } from '../api/client'
import UserProfileModal from './UserProfileModal'

export default function Navbar() {
  const { user, plan, upgrade, logout, refreshBilling } = useAuth()
  const navigate = useNavigate()
  const profile = useDisclosure()

  // Ensure plan is always fresh when the navbar mounts or user changes
  useEffect(() => {
    if (user) {
      refreshBilling().catch(() => {})
    }
  }, [user])
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
              <Badge
                colorScheme={plan === 'premium' ? 'purple' : plan === 'standard' ? 'blue' : 'gray'}
                variant="subtle"
                borderRadius="6px"
              >
                {plan.toUpperCase()}
              </Badge>
            </Flex>
            {plan === 'free' ? (
              <Button 
                onClick={upgrade}
                colorScheme="purple"
                variant="solid"
                size="sm"
                borderRadius="8px"
                className="btn-professional"
              >
                Upgrade
              </Button>
            ) : (
              <Button 
                onClick={async () => {
                  try {
                    const p = await createBillingPortal()
                    if (p.url) window.location.assign(p.url)
                  } catch (e) {
                    console.error(e)
                  }
                }}
                colorScheme="purple"
                variant="outline"
                size="sm"
                borderRadius="8px"
                className="btn-professional"
              >
                Manage Billing
              </Button>
            )}
            <Button
              onClick={profile.onOpen}
              variant="ghost"
              size="sm"
              borderRadius="8px"
            >
              Settings
            </Button>
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
      <UserProfileModal isOpen={profile.isOpen} onClose={profile.onClose} />
    </Box>
  )
}
