import { useEffect, useMemo, useState, type ChangeEvent } from 'react'
import { Box, Button, Container, FormControl, FormLabel, Heading, Input, NumberInput, NumberInputField, Select, Stack, Text, useToast } from '@chakra-ui/react'
import Navbar from '../components/Navbar'
import { generateQuestions, Question, submitAnswers, getErrorMessage } from '../api/client'
import { useLocation, useNavigate } from 'react-router-dom'

function useQuery() {
  const { search } = useLocation()
  return useMemo(() => new URLSearchParams(search), [search])
}

export default function QuestionsPage() {
  const query = useQuery()
  const navigate = useNavigate()
  const toast = useToast()
  const [contentId, setContentId] = useState('')
  const [count, setCount] = useState(5)
  const [type, setType] = useState('Multiple Choice')
  const [questions, setQuestions] = useState<Question[]>([])
  const [questionSetId, setQuestionSetId] = useState<string>('')
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const cid = query.get('content_id')
    if (cid) setContentId(cid)
  }, [query])

  const onGenerate = async () => {
    if (!contentId) {
      toast({ title: 'Missing content id', status: 'warning' })
      return
    }
    setLoading(true)
    try {
  const res = await generateQuestions({ contentId, questionCount: count, questionTypes: [type] })
  setQuestions(res.questions)
  setQuestionSetId(res.id)
      toast({ title: 'Questions ready', status: 'success' })
    } catch (err: any) {
      toast({ title: 'Failed to generate', description: getErrorMessage(err) || 'Try again', status: 'error' })
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async () => {
    if (!questions.length) return
    setLoading(true)
    try {
  const res = await submitAnswers({ questionSetId: questionSetId, answers })
    toast({ title: `Score: ${res.overallScore ?? 0}%`, status: 'info' })
      navigate('/dashboard')
    } catch (err: any) {
      toast({ title: 'Submit failed', description: getErrorMessage(err) || 'Try again', status: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Navbar />
      <Container maxW="5xl" py={10}>
        <Heading mb={6}>Question Setter</Heading>
        <Stack direction={{ base: 'column', md: 'row' }} spacing={4} mb={6}>
          <FormControl isRequired>
            <FormLabel>Content ID</FormLabel>
            <Input value={contentId} onChange={(e: ChangeEvent<HTMLInputElement>) => setContentId(e.target.value)} placeholder="Content ID from previous step" />
          </FormControl>
          <FormControl>
            <FormLabel>Count</FormLabel>
            <NumberInput min={1} max={20} value={count} onChange={(_str: string, v: number) => setCount(Number.isNaN(v) ? 1 : v)}>
              <NumberInputField />
            </NumberInput>
          </FormControl>
          <FormControl>
            <FormLabel>Type</FormLabel>
            <Select value={type} onChange={(e: ChangeEvent<HTMLSelectElement>) => setType(e.target.value)}>
              <option>Multiple Choice</option>
              <option>True/False</option>
              <option>Short Answer</option>
            </Select>
          </FormControl>
          <Button onClick={onGenerate} isLoading={loading} colorScheme="teal" alignSelf="end">Generate</Button>
        </Stack>

  {questions.map((q: Question, idx: number) => (
          <Box key={idx} p={4} borderWidth="1px" rounded="md" mb={3}>
            <Text fontWeight="bold" mb={2}>{`Q${idx + 1}. ${q.question}`}</Text>
            {q.type === 'Multiple Choice' && q.options?.map((opt: string, j: number) => (
              <Button key={j} size="sm" mr={2} mb={2} variant={answers[idx]?.toString() === opt ? 'solid' : 'outline'} onClick={() => setAnswers((a: Record<string, string>) => ({ ...a, [idx]: opt }))}>{String.fromCharCode(65 + j)}. {opt}</Button>
            ))}
            {q.type === 'True/False' && ['True', 'False'].map((opt) => (
              <Button key={opt} size="sm" mr={2} mb={2} variant={answers[idx]?.toString() === opt ? 'solid' : 'outline'} onClick={() => setAnswers((a: Record<string, string>) => ({ ...a, [idx]: opt }))}>{opt}</Button>
            ))}
            {q.type === 'Short Answer' && (
              <Input placeholder="Your answer" value={answers[idx]?.toString() || ''} onChange={(e: ChangeEvent<HTMLInputElement>) => setAnswers((a: Record<string, string>) => ({ ...a, [idx]: e.target.value }))} />
            )}
          </Box>
        ))}

        {questions.length > 0 && (
          <Button onClick={onSubmit} isLoading={loading} colorScheme="purple">Submit Answers</Button>
        )}
      </Container>
    </Box>
  )
}
