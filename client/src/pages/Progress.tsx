import { Box, Button, Heading, HStack, SimpleGrid, Stack, Text, Icon } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { useEffect, useState } from 'react'
import { getMyProgress, ProgressOut } from '../api/client'
import { Link as RouterLink } from 'react-router-dom'
import { MdTrendingUp } from 'react-icons/md'

export default function ProgressPage() {
  const [data, setData] = useState<ProgressOut>({})

  useEffect(() => {
    getMyProgress().then(setData).catch(() => {})
  }, [])

  return (
    <PrivateLayout>
      <Stack spacing={8}>
        <Box>
          <HStack mb={2}>
            <Icon as={MdTrendingUp} boxSize={8} color="teal.500" />
            <Heading size="xl" color="gray.800">Learning Progress</Heading>
          </HStack>
          <Text color="gray.600" fontSize="lg">
            Track your learning journey and achievements
          </Text>
        </Box>
        {/* Overview Stats */}
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6} mb={8}>
          <Box
            bg="white"
            p={6}
            borderRadius="12px"
            borderWidth="1px"
            borderColor="gray.200"
            boxShadow="0 2px 4px rgba(0, 0, 0, 0.04)"
            textAlign="center"
          >
            <Text fontSize="2xl" fontWeight="bold" color="purple.500" mb={1}>
              {data.content_count ?? 0}
            </Text>
            <Text fontSize="sm" color="gray.600" fontWeight="500">Content Created</Text>
          </Box>
          <Box
            bg="white"
            p={6}
            borderRadius="12px"
            borderWidth="1px"
            borderColor="gray.200"
            boxShadow="0 2px 4px rgba(0, 0, 0, 0.04)"
            textAlign="center"
          >
            <Text fontSize="2xl" fontWeight="bold" color="blue.500" mb={1}>
              {data.questions_answered ?? 0}
            </Text>
            <Text fontSize="sm" color="gray.600" fontWeight="500">Questions Answered</Text>
          </Box>
          <Box
            bg="white"
            p={6}
            borderRadius="12px"
            borderWidth="1px"
            borderColor="gray.200"
            boxShadow="0 2px 4px rgba(0, 0, 0, 0.04)"
            textAlign="center"
          >
            <Text fontSize="2xl" fontWeight="bold" color="teal.500" mb={1}>
              {(data.average_score ?? 0).toFixed(1)}%
            </Text>
            <Text fontSize="sm" color="gray.600" fontWeight="500">Average Score</Text>
          </Box>
          <Box
            bg="white"
            p={6}
            borderRadius="12px"
            borderWidth="1px"
            borderColor="gray.200"
            boxShadow="0 2px 4px rgba(0, 0, 0, 0.04)"
            textAlign="center"
          >
            <Text fontSize="2xl" fontWeight="bold" color="orange.500" mb={1}>
              {data.study_streak ?? 0}
            </Text>
            <Text fontSize="sm" color="gray.600" fontWeight="500">Day Streak 🔥</Text>
          </Box>
        </SimpleGrid>

        {/* Recent Activity */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          <Box
            bg="white"
            borderRadius="16px"
            borderWidth="1px"
            borderColor="gray.200"
            boxShadow="0 2px 8px rgba(0, 0, 0, 0.06)"
            overflow="hidden"
          >
            <Box bg="purple.50" px={6} py={4}>
              <Heading size="md" color="purple.700">Past Contents</Heading>
              <Text fontSize="sm" color="purple.600">Study materials you've created</Text>
            </Box>
            <Box p={6}>
              <Stack spacing={3}>
                {(data.recent_contents ?? []).map((c) => (
                  <Box key={c.id} p={3} bg="gray.50" borderRadius="8px">
                    <HStack justify="space-between" align="start">
                      <Box flex="1">
                        <Text fontWeight="500" color="gray.800" noOfLines={1} mb={1}>
                          {c.topic}
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {new Date(c.createdAt).toLocaleDateString()}
                        </Text>
                      </Box>
                      <Button 
                        as={RouterLink} 
                        to={`/content/view?id=${encodeURIComponent(c.id)}`} 
                        size="xs" 
                        colorScheme="purple"
                        variant="outline"
                        borderRadius="6px"
                      >
                        View
                      </Button>
                    </HStack>
                  </Box>
                ))}
                {!(data.recent_contents ?? []).length && (
                  <Text color="gray.500" textAlign="center" py={4} fontSize="sm">
                    No content created yet
                  </Text>
                )}
              </Stack>
            </Box>
          </Box>

          <Box
            bg="white"
            borderRadius="16px"
            borderWidth="1px"
            borderColor="gray.200"
            boxShadow="0 2px 8px rgba(0, 0, 0, 0.06)"
            overflow="hidden"
          >
            <Box bg="blue.50" px={6} py={4}>
              <Heading size="md" color="blue.700">Question Sets</Heading>
              <Text fontSize="sm" color="blue.600">Practice questions generated</Text>
            </Box>
            <Box p={6}>
              <Stack spacing={3}>
                {(data.recent_question_sets ?? []).map((q) => (
                  <Box key={q.id} p={3} bg="gray.50" borderRadius="8px">
                    <HStack justify="space-between">
                      <Box>
                        <Text fontWeight="500" color="gray.800" mb={1}>
                          {q.questionCount} Questions
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {new Date(q.createdAt).toLocaleDateString()}
                        </Text>
                      </Box>
                    </HStack>
                  </Box>
                ))}
                {!(data.recent_question_sets ?? []).length && (
                  <Text color="gray.500" textAlign="center" py={4} fontSize="sm">
                    No question sets yet
                  </Text>
                )}
              </Stack>
            </Box>
          </Box>

          <Box
            bg="white"
            borderRadius="16px"
            borderWidth="1px"
            borderColor="gray.200"
            boxShadow="0 2px 8px rgba(0, 0, 0, 0.06)"
            overflow="hidden"
          >
            <Box bg="teal.50" px={6} py={4}>
              <Heading size="md" color="teal.700">Recent Scores</Heading>
              <Text fontSize="sm" color="teal.600">Your latest performance</Text>
            </Box>
            <Box p={6}>
              <Stack spacing={3}>
                {(data.recent_feedback ?? []).map((f) => (
                  <Box key={f.id} p={3} bg="gray.50" borderRadius="8px">
                    <HStack justify="space-between" align="start">
                      <Box>
                        <Text fontWeight="500" color="gray.800" mb={1}>
                          Score: {(f.overallScore ?? 0).toFixed(1)}%
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {new Date(f.createdAt).toLocaleDateString()}
                        </Text>
                      </Box>
                      <Button 
                        as={RouterLink} 
                        to={`/feedback?id=${encodeURIComponent(f.id)}`} 
                        size="xs" 
                        colorScheme="teal"
                        variant="outline"
                        borderRadius="6px"
                      >
                        View
                      </Button>
                    </HStack>
                  </Box>
                ))}
                {!(data.recent_feedback ?? []).length && (
                  <Text color="gray.500" textAlign="center" py={4} fontSize="sm">
                    No feedback yet
                  </Text>
                )}
              </Stack>
            </Box>
          </Box>
        </SimpleGrid>

        {/* Past Chats removed per request */}
      </Stack>
    </PrivateLayout>
  )
}
