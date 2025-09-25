import { Button, SimpleGrid, Heading, Stack, Text, Icon, Flex, Box, Badge, HStack, useToast } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { MdDescription, MdQuiz, MdTrendingUp, MdArrowForward, MdCreate, MdAnalytics } from 'react-icons/md'
import { useEffect, useState } from 'react'
import { getMyProgress, ProgressOut } from '../api/client'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

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

export default function Dashboard() {
  const { user, refreshBilling } = useAuth()
  const toast = useToast()
  const location = useLocation()
  const [progressData, setProgressData] = useState<ProgressOut>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMyProgress()
      .then(setProgressData)
      .catch(() => {})
      .finally(() => setLoading(false))
    // If returning from Stripe checkout success, refresh billing status
    const params = new URLSearchParams(location.search)
    const sid = params.get('session_id') || undefined
    // Confirm if we have a session_id, regardless of presence of a 'session=success' flag
    if (sid) {
      api.post('/billing/confirm', { session_id: sid })
        .catch(() => {})
        .finally(() => {
          refreshBilling().then(() => {
            toast({ title: 'Subscription activated', status: 'success', duration: 4000, isClosable: true })
          }).catch(() => {})
        })
    }
  }, [])

  // Calculate study sessions from content count (content creation sessions)
  const studySessions = (progressData.content_count ?? 0) + (progressData.recent_question_sets?.length ?? 0)
  
  const recentStats = [
    { 
      label: 'Study Sessions', 
      value: studySessions.toString(), 
      change: progressData.content_count ? `${progressData.content_count} content created` : 'Start creating content'
    },
    { 
      label: 'Questions Answered', 
      value: (progressData.questions_answered ?? 0).toString(), 
      change: progressData.questions_answered ? 'Keep practicing!' : 'Start answering questions'
    },
    { 
      label: 'Average Score', 
      value: `${(progressData.average_score ?? 0).toFixed(1)}%`, 
      change: progressData.average_score ? (progressData.average_score >= 70 ? 'Great performance!' : 'Room for improvement') : 'Take your first quiz'
    }
  ]

  if (loading) {
    return (
      <PrivateLayout>
        <Stack spacing={8}>
          <Box>
            <Heading size="xl" color="gray.800" mb={2}>Loading...</Heading>
            <Text color="gray.600" fontSize="lg">Fetching your progress data</Text>
          </Box>
        </Stack>
      </PrivateLayout>
    )
  }

  return (
    <PrivateLayout>
      <Stack spacing={8}>
        <Box>
          <Heading size="xl" color="gray.800" mb={2}>
            Welcome back{user?.name ? `, ${user.name}` : ''}!
          </Heading>
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
            boxShadow="0 2px 4px rgba(0, 0, 0, 0.04)"
            overflow="hidden"
          >
            {(() => {
              const activities: Array<{
                type: string
                title: string
                time: string
                icon: any
                color: string
                link: string
              }> = []
              
              // Add recent content activities
              if (progressData.recent_contents?.length) {
                progressData.recent_contents.slice(0, 3).forEach(content => {
                  activities.push({
                    type: 'content',
                    title: `Created study material: ${content.topic}`,
                    time: content.createdAt,
                    icon: MdDescription,
                    color: 'purple',
                    link: `/content/view?id=${content.id}`
                  })
                })
              }
              
              // Add recent question set activities
              if (progressData.recent_question_sets?.length) {
                progressData.recent_question_sets.slice(0, 2).forEach(qs => {
                  activities.push({
                    type: 'questions',
                    title: `Generated ${qs.questionCount} practice questions`,
                    time: qs.createdAt,
                    icon: MdQuiz,
                    color: 'blue',
                    link: `/questions?content_id=${qs.contentId}`
                  })
                })
              }
              
              // Add recent feedback activities
              if (progressData.recent_feedback?.length) {
                progressData.recent_feedback.slice(0, 2).forEach(feedback => {
                  activities.push({
                    type: 'feedback',
                    title: `Completed quiz - Score: ${feedback.overallScore.toFixed(1)}%`,
                    time: feedback.createdAt,
                    icon: MdTrendingUp,
                    color: feedback.overallScore >= 70 ? 'green' : 'orange',
                    link: `/feedback?id=${feedback.id}`
                  })
                })
              }
              
              // Sort by most recent
              activities.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
              
              return activities.length > 0 ? (
                <Stack spacing={0}>
                  {activities.slice(0, 5).map((activity, index) => (
                    <Box key={index}>
                      <HStack
                        as={RouterLink}
                        to={activity.link}
                        p={4}
                        _hover={{ bg: 'gray.50' }}
                        transition="background 0.2s ease"
                        textDecoration="none"
                        _focus={{ outline: 'none' }}
                      >
                        <Flex
                          align="center"
                          justify="center"
                          w={10}
                          h={10}
                          borderRadius="10px"
                          bg={`${activity.color}.100`}
                        >
                          <Icon as={activity.icon} boxSize={5} color={`${activity.color}.500`} />
                        </Flex>
                        <Box flex="1">
                          <Text fontWeight="500" color="gray.800" fontSize="sm" mb={1}>
                            {activity.title}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            {new Date(activity.time).toLocaleString()}
                          </Text>
                        </Box>
                        <Icon as={MdArrowForward} boxSize={4} color="gray.400" />
                      </HStack>
                      {index < activities.slice(0, 5).length - 1 && (
                        <Box height="1px" bg="gray.100" mx={4} />
                      )}
                    </Box>
                  ))}
                </Stack>
              ) : (
                <Box p={8} textAlign="center">
                  <Icon as={MdCreate} boxSize={12} color="gray.300" mb={4} />
                  <Text color="gray.500" mb={2}>No recent activity yet</Text>
                  <Text color="gray.400" fontSize="sm">
                    Start by creating some study content or taking a quiz
                  </Text>
                </Box>
              )
            })()}
          </Box>
        </Box>
      </Stack>
    </PrivateLayout>
  )
}
