import { Button, SimpleGrid, Heading, Stack, Text, Icon, Flex, Box, Badge, HStack } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { Link as RouterLink } from 'react-router-dom'
import { MdDescription, MdQuiz, MdTrendingUp, MdArrowForward, MdCreate, MdAnalytics } from 'react-icons/md'

const quickActions = [
  {
    title: 'Generate Content',
    desc: 'Create personalized study materials with AI assistance',
    icon: MdDescription,
    path: '/content',
    gradient: 'linear(to-br, purple.400, purple.600)',
    available: true
  },
  {
    title: 'Create Questions',
    desc: 'Generate practice questions from your study content',
    icon: MdQuiz,
    path: '/questions',
    gradient: 'linear(to-br, blue.400, blue.600)',
    available: true
  },
  {
    title: 'View Progress',
    desc: 'Track your learning journey and performance analytics',
    icon: MdTrendingUp,
    path: '/progress',
    gradient: 'linear(to-br, teal.400, teal.600)',
    available: true
  }
]

const recentStats = [
  { label: 'Study Sessions', value: '12', change: '+3 this week' },
  { label: 'Questions Answered', value: '48', change: '+15 today' },
  { label: 'Average Score', value: '85%', change: '+5% improvement' }
]

export default function Dashboard() {
  return (
    <PrivateLayout>
      <Stack spacing={8}>
        <Box>
          <Heading size="xl" color="gray.800" mb={2}>Welcome back!</Heading>
          <Text color="gray.600" fontSize="lg">Ready to continue your learning journey?</Text>
        </Box>

        {/* Quick Stats */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          {recentStats.map((stat, index) => (
            <Box
              key={index}
              bg="white"
              p={6}
              borderRadius="12px"
              borderWidth="1px"
              borderColor="gray.200"
              boxShadow="0 2px 4px rgba(0, 0, 0, 0.04)"
            >
              <Text fontSize="sm" color="gray.500" fontWeight="500" mb={1}>{stat.label}</Text>
              <Heading size="lg" color="gray.800" mb={2}>{stat.value}</Heading>
              <Text fontSize="sm" color="green.500" fontWeight="500">{stat.change}</Text>
            </Box>
          ))}
        </SimpleGrid>

        {/* Quick Actions */}
        <Box>
          <Heading size="lg" mb={6} color="gray.800">Quick Actions</Heading>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
            {quickActions.map((action, index) => (
              <Box
                key={index}
                as={RouterLink}
                to={action.path}
                bg="white"
                p={6}
                borderRadius="16px"
                borderWidth="1px"
                borderColor="gray.200"
                boxShadow="0 2px 8px rgba(0, 0, 0, 0.06)"
                position="relative"
                overflow="hidden"
                cursor="pointer"
                transition="all 0.3s ease"
                _hover={{
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
                  textDecoration: 'none'
                }}
                textDecoration="none"
              >
                <Stack spacing={4}>
                  <HStack justify="space-between">
                    <Flex 
                      align="center" 
                      justify="center" 
                      w={12} 
                      h={12} 
                      borderRadius="12px"
                      bgGradient={action.gradient}
                    >
                      <Icon as={action.icon} boxSize={6} color="white" />
                    </Flex>
                    <Icon as={MdArrowForward} boxSize={5} color="gray.400" />
                  </HStack>
                  
                  <Stack spacing={2}>
                    <HStack>
                      <Heading size="md" color="gray.800">{action.title}</Heading>
                      {action.available && (
                        <Badge colorScheme="green" borderRadius="full" px={2}>Ready</Badge>
                      )}
                    </HStack>
                    <Text color="gray.600" fontSize="sm" lineHeight="1.5">{action.desc}</Text>
                  </Stack>
                </Stack>
              </Box>
            ))}
          </SimpleGrid>
        </Box>

        {/* Recent Activity */}
        <Box>
          <Heading size="lg" mb={4} color="gray.800">Recent Activity</Heading>
          <Box
            bg="white"
            borderRadius="12px"
            borderWidth="1px"
            borderColor="gray.200"
            p={6}
            boxShadow="0 2px 4px rgba(0, 0, 0, 0.04)"
          >
            <Text color="gray.500" textAlign="center" py={8}>
              Your recent study sessions will appear here
            </Text>
          </Box>
        </Box>
      </Stack>
    </PrivateLayout>
  )
}
