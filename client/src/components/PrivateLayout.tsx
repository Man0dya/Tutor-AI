import { Box, Button, Flex, Heading, Stack, VStack, Icon, useDisclosure } from '@chakra-ui/react'
import Navbar from './Navbar'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import UserProfileModal from './UserProfileModal'
import { 
  MdDashboard, 
  MdDescription, 
  MdQuiz, 
  MdFeedback, 
  MdTrendingUp 
} from 'react-icons/md'

const menuItems = [
  { to: '/dashboard', label: 'Dashboard', icon: MdDashboard },
  { to: '/content', label: 'Content', icon: MdDescription },
  { to: '/questions', label: 'Questions', icon: MdQuiz },
  { to: '/feedback', label: 'Feedback', icon: MdFeedback },
  { to: '/progress', label: 'Progress', icon: MdTrendingUp },
]

export default function PrivateLayout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()
  const settings = useDisclosure()
  
  const link = (to: string, label: string, IconComponent: any) => {
    const isActive = pathname === to
    return (
      <Button 
        as={RouterLink} 
        to={to} 
        variant={isActive ? 'solid' : 'ghost'}
        colorScheme={isActive ? 'purple' : 'gray'}
        justifyContent="flex-start" 
        width="100%"
        leftIcon={<Icon as={IconComponent} boxSize={5} />}
        borderRadius="10px"
        py={6}
        fontWeight="500"
        fontSize="sm"
        _hover={isActive ? {
          bg: 'purple.500',
          transform: 'translateX(2px)',
          transition: 'all 0.2s ease'
        } : {
          bg: { base: 'purple.50', _dark: 'whiteAlpha.200' },
          transform: 'translateX(2px)',
          transition: 'all 0.2s ease'
        }}
        transition="all 0.2s ease"
      >
        {label}
      </Button>
    )
  }

  return (
    <Box bg="bg" minH="100vh">
      <Navbar />
      <Flex>
        <Box 
          as="nav" 
          width="260px" 
          height="calc(100vh - 73px)" 
          bg="surface"
          borderRightWidth="1px" 
          borderColor="border"
          p={4}
          boxShadow={{ base: 'sm', _dark: 'none' }}
          display="flex"
          flexDirection="column"
          overflow="hidden"
        >
          <VStack align="stretch" spacing={2}>
            <Heading 
              size="sm" 
              px={3} 
              mb={4} 
              color="muted"
              letterSpacing="wide"
              textTransform="uppercase"
              fontSize="xs"
            >
              Navigation
            </Heading>
          </VStack>
          <Box flex="1" overflowY="auto" mt={2} pr={1}>
            <VStack align="stretch" spacing={2}>
              {menuItems.map(item => 
                link(item.to, item.label, item.icon)
              )}
            </VStack>
          </Box>
          <Box position="sticky" bottom={0} bg="surface" pt={2} borderTop="1px solid" borderColor="border">
            <Button 
              onClick={settings.onOpen}
              variant="ghost"
              justifyContent="flex-start"
              width="100%"
              borderRadius="10px"
              py={6}
              fontWeight="500"
              fontSize="sm"
              _hover={{ bg: { base: 'purple.50', _dark: 'whiteAlpha.200' }, transform: 'translateX(2px)' }}
              transition="all 0.2s ease"
            >
              Settings
            </Button>
          </Box>
        </Box>
        <Box flex="1" p={6} bg="bg">
          <Box 
            bg="surface" 
            borderRadius="16px" 
            p={6}
            boxShadow={{ base: 'md', _dark: 'none' }}
            borderWidth="1px"
            borderColor="border"
            minH="calc(100vh - 134px)"
          >
            {children}
          </Box>
        </Box>
      </Flex>
      {/* Settings modal at app level */}
      <UserProfileModal isOpen={settings.isOpen} onClose={settings.onClose} />
    </Box>
  )
}
