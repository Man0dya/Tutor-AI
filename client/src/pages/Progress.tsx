import { Box, Button, Container, Heading, HStack, SimpleGrid, Stack, Stat, StatHelpText, StatLabel, StatNumber, Text } from '@chakra-ui/react'
import Navbar from '../components/Navbar'
import { useEffect, useState } from 'react'
import { getMyProgress, ProgressOut } from '../api/client'
import { Link as RouterLink } from 'react-router-dom'

export default function ProgressPage() {
  const [data, setData] = useState<ProgressOut>({})

  useEffect(() => {
    getMyProgress().then(setData).catch(() => {})
  }, [])

  return (
    <Box>
      <Navbar />
      <Container maxW="5xl" py={10}>
        <Heading mb={6}>Progress</Heading>
        <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4}>
          <Stat>
            <StatLabel>Content</StatLabel>
            <StatNumber>{data.content_count ?? 0}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Answered</StatLabel>
            <StatNumber>{data.questions_answered ?? 0}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Average Score</StatLabel>
            <StatNumber>{(data.average_score ?? 0).toFixed(1)}%</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>Streak</StatLabel>
            <StatNumber>{data.study_streak ?? 0} days</StatNumber>
            <StatHelpText>Keep it going!</StatHelpText>
          </Stat>
        </SimpleGrid>

        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mt={8}>
          <Box borderWidth="1px" rounded="md" p={4}>
            <Heading size="md" mb={3}>Past Contents</Heading>
            <Stack spacing={2}>
              {(data.recent_contents ?? []).map((c) => (
                <HStack key={c.id} justify="space-between">
                  <Text noOfLines={1}>{c.topic}</Text>
                  <HStack>
                    <Text fontSize="sm" color="gray.500">{new Date(c.createdAt).toLocaleString()}</Text>
                    <Button as={RouterLink} to={`/content/view?id=${encodeURIComponent(c.id)}`} size="xs" variant="outline">View</Button>
                  </HStack>
                </HStack>
              ))}
              {!(data.recent_contents ?? []).length && <Text color="gray.500">No content yet</Text>}
            </Stack>
          </Box>
          <Box borderWidth="1px" rounded="md" p={4}>
            <Heading size="md" mb={3}>Past Question Sets</Heading>
            <Stack spacing={2}>
              {(data.recent_question_sets ?? []).map((q) => (
                <HStack key={q.id} justify="space-between">
                  <Text>Questions: {q.questionCount}</Text>
                  <Text fontSize="sm" color="gray.500">{new Date(q.createdAt).toLocaleString()}</Text>
                </HStack>
              ))}
              {!(data.recent_question_sets ?? []).length && <Text color="gray.500">No question sets yet</Text>}
            </Stack>
          </Box>
          <Box borderWidth="1px" rounded="md" p={4}>
            <Heading size="md" mb={3}>Past Marks</Heading>
            <Stack spacing={2}>
              {(data.recent_feedback ?? []).map((f) => (
                <HStack key={f.id} justify="space-between">
                  <Text>Score: {(f.overallScore ?? 0).toFixed(1)}%</Text>
                  <HStack>
                    <Text fontSize="sm" color="gray.500">{new Date(f.createdAt).toLocaleString()}</Text>
                    <Button as={RouterLink} to={`/feedback?id=${encodeURIComponent(f.id)}`} size="xs" variant="outline">View</Button>
                  </HStack>
                </HStack>
              ))}
              {!(data.recent_feedback ?? []).length && <Text color="gray.500">No feedback yet</Text>}
            </Stack>
          </Box>
        </SimpleGrid>

        {/* Past Chats removed per request */}
      </Container>
    </Box>
  )
}
