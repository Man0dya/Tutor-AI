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
        _hover={{
          bg: isActive ? 'purple.500' : 'purple.50',
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
    <Box bg="#fafafa" minH="100vh">
      <Navbar />
      <Flex>
        <Box 
          as="nav" 
          width="260px" 
          height="calc(100vh - 73px)" 
          bg="white"
          borderRightWidth="1px" 
          borderColor="gray.200"
          p={4}
          boxShadow="2px 0 4px rgba(0, 0, 0, 0.02)"
          display="flex"
          flexDirection="column"
          overflow="hidden"
        >
          <VStack align="stretch" spacing={2}>
            <Heading 
              size="sm" 
              px={3} 
              mb={4} 
              color="gray.600"
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
          <Box position="sticky" bottom={0} bg="white" pt={2} borderTop="1px solid" borderColor="gray.200">
            <Button 
              onClick={settings.onOpen}
              variant="ghost"
              justifyContent="flex-start"
              width="100%"
              borderRadius="10px"
              py={6}
              fontWeight="500"
              fontSize="sm"
              _hover={{ bg: 'purple.50', transform: 'translateX(2px)' }}
              transition="all 0.2s ease"
            >
              Settings
            </Button>
          </Box>
        </Box>
        <Box flex="1" p={6} bg="#fafafa">
          <Box 
            bg="white" 
            borderRadius="16px" 
            p={6}
            boxShadow="0 2px 8px rgba(0, 0, 0, 0.06)"
            border="1px solid #e2e8f0"
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
