import { Box, Button, Flex, Heading, Stack, VStack, Icon } from '@chakra-ui/react'
import Navbar from './Navbar'
import { Link as RouterLink, useLocation } from 'react-router-dom'
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
          minH="calc(100vh - 73px)" 
          bg="white"
          borderRightWidth="1px" 
          borderColor="gray.200"
          p={4}
          boxShadow="2px 0 4px rgba(0, 0, 0, 0.02)"
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
            {menuItems.map(item => 
              link(item.to, item.label, item.icon)
            )}
          </VStack>
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
    </Box>
  )
}
