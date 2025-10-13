import { Box, Button, Flex, HStack, Heading, Spacer, Avatar, Text, IconButton, useColorMode, Tooltip, Image } from '@chakra-ui/react'
import { MdDarkMode, MdLightMode } from 'react-icons/md'
import { useEffect } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Badge } from '@chakra-ui/react'
import { createBillingPortal } from '../api/client'
import logo from '../../assets/favicon.svg'

export default function Navbar() {
  const { user, plan, upgrade, logout, refreshBilling } = useAuth()
  const navigate = useNavigate()
  const { colorMode, toggleColorMode } = useColorMode()

  // Ensure plan is always fresh when the navbar mounts or user changes
  useEffect(() => {
    if (user) {
      refreshBilling().catch(() => {})
    }
  }, [user])
  return (
    <Box 
      as="header" 
      position="sticky"
      top={0}
      zIndex={1000}
      bg="transparent"
      backdropFilter="blur(4px)"
      borderBottomWidth="1px" 
      borderColor={{ base: 'rgba(226, 232, 240, 0.3)', _dark: 'rgba(74, 85, 104, 0.3)' }}
      py={4} 
      px={6}
      boxShadow="none"
    >
      <Flex align="center" gap={3}>
        <RouterLink to={user ? '/dashboard' : '/'}>
          <Image src={logo} alt="Tutor AI logo" boxSize={{ base: '28px', md: '32px' }} draggable={false} />
        </RouterLink>
        <Heading 
          size="lg" 
          color="text"
          fontWeight="bold"
        >
          <RouterLink to={user ? '/dashboard' : '/'}>Tutor AI</RouterLink>
        </Heading>
        <Spacer />
        <Tooltip label={colorMode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}>
          <IconButton
            aria-label="Toggle color mode"
            icon={colorMode === 'dark' ? <MdLightMode /> : <MdDarkMode />}
            onClick={toggleColorMode}
            variant="ghost"
            color={colorMode === 'dark' ? 'yellow.300' : 'gray.600'}
          />
        </Tooltip>
        {user ? (
          <HStack spacing={4}>
            <Flex align="center" gap={3}>
              <Avatar size="sm" name={user.email} bg="purple.500" />
              <Text fontSize="sm" fontWeight="500" color="muted">{user.email}</Text>
              <Badge colorScheme={plan === 'premium' ? 'purple' : plan === 'standard' ? 'blue' : 'gray'} variant="subtle" borderRadius="6px">
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
              size="md" 
              variant="outline"
              borderRadius="8px"
              className="btn-professional"
              px={6}
            >
              Login
            </Button>
            <Button 
              as={RouterLink} 
              to="/signup" 
              size="md" 
              colorScheme="purple"
              borderRadius="8px"
              className="btn-professional"
              px={6}
            >
              Sign Up
            </Button>
          </HStack>
        )}
      </Flex>
    </Box>
  )
}
