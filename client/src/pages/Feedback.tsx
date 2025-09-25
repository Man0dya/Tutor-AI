import { useEffect, useState } from 'react'
import { Box, Container, Heading, Text, Stack, Badge, Divider } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { useLocation } from 'react-router-dom'
import { api, type FeedbackOut, getErrorMessage } from '../api/client'

function useQuery() {
  const { search } = useLocation()
  return new URLSearchParams(search)
}

export default function FeedbackPage() {
  const query = useQuery()
  const [feedback, setFeedback] = useState<FeedbackOut | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const id = query.get('id')
    if (!id) return
    api.get<FeedbackOut>(`/answers/feedback/${id}`)
      .then(res => setFeedback(res.data))
      .catch(err => setError(getErrorMessage(err)))
  }, [query])

  return (
    <PrivateLayout>
      <Container maxW="5xl" py={2}>
        <Heading mb={6}>Feedback</Heading>
        {error && <Text color="red.500">{error}</Text>}
        {feedback && (
          <Stack spacing={6}>
            <Box borderWidth="1px" rounded="md" p={4}>
              <Heading size="md" mb={2}>Overall</Heading>
              <Text>Score: <Badge colorScheme="purple">{feedback.overallScore?.toFixed(1)}%</Badge></Text>
            </Box>
            <Box borderWidth="1px" rounded="md" p={4}>
              <Heading size="md" mb={3}>Detailed Feedback</Heading>
              <Text whiteSpace="pre-wrap">{feedback.detailedFeedback}</Text>
            </Box>
            {feedback.studySuggestions && (
              <Box borderWidth="1px" rounded="md" p={4}>
                <Heading size="md" mb={3}>Study Suggestions</Heading>
                <Text whiteSpace="pre-wrap">{feedback.studySuggestions}</Text>
              </Box>
            )}
            {feedback.individualEvaluations && feedback.individualEvaluations.length > 0 && (
              <Box borderWidth="1px" rounded="md" p={4}>
                <Heading size="md" mb={3}>Per-Question Marking</Heading>
                <Stack spacing={4}>
                  {feedback.individualEvaluations.map((ev: any, idx: number) => (
                    <Box key={idx}>
                      <Text fontWeight="bold">Q{idx + 1}: {ev.question_text}</Text>
                      <Text>Answered: {ev.user_answer}</Text>
                      {'correct_answer' in ev && <Text>Correct: {ev.correct_answer}</Text>}
                      <Text>Score: <Badge colorScheme={ev.is_correct ? 'green' : 'red'}>{Math.round(ev.score)}%</Badge></Text>
                      {ev.feedback && <Text color="gray.600" mt={1}>{ev.feedback}</Text>}
                      <Divider mt={3} />
                    </Box>
                  ))}
                </Stack>
              </Box>
            )}
          </Stack>
        )}
      </Container>
    </PrivateLayout>
  )
}
