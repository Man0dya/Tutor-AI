import { useEffect, useMemo, useRef, useState, type ChangeEvent } from 'react'
import { Box, Button, Container, Divider, FormControl, FormLabel, Heading, HStack, Icon, Input, NumberInput, NumberInputField, Radio, RadioGroup, Select, Stack, Text, Textarea, VStack, useToast, Badge, Alert, AlertIcon } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { generateQuestions, Question, submitAnswers, getErrorMessage } from '../api/client'
import { useLocation, useNavigate } from 'react-router-dom'
import { MdQuiz, MdBolt } from 'react-icons/md'
// PII checks are enforced on the backend; no client-side PII detection

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
  const [generating, setGenerating] = useState(false)
  const questionRefs = useRef<Array<HTMLDivElement | null>>([])

  const answeredCount = useMemo(() => questions.reduce((acc, _q, i) => acc + (answers[i] ? 1 : 0), 0), [questions, answers])

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
    setGenerating(true)
    try {
  const res = await generateQuestions({ contentId, questionCount: count, questionTypes: [type] })
  setQuestions(res.questions)
  setQuestionSetId(res.id)
      toast({ title: 'Questions ready', status: 'success' })
    } catch (err: any) {
      toast({ title: 'Failed to generate', description: getErrorMessage(err) || 'Try again', status: 'error' })
    } finally {
      setLoading(false)
      setGenerating(false)
    }
  }

  const onSubmit = async () => {
    if (!questions.length) return
    // Backend enforces PII rules; proceed to submit
    setLoading(true)
    try {
  const res = await submitAnswers({ questionSetId: questionSetId, answers })
    toast({ title: `Score: ${res.overallScore ?? 0}%`, status: 'info' })
      navigate(`/feedback?id=${encodeURIComponent(res.id)}`)
    } catch (err: any) {
      toast({ title: 'Submit failed', description: getErrorMessage(err) || 'Try again', status: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <PrivateLayout>
      <Container maxW="5xl" py={2}>
        <HStack mb={2} spacing={2} align="center">
          <Icon as={MdQuiz} boxSize={7} color="purple.500" />
          <Heading size="lg">Practice Questions</Heading>
        </HStack>
        <Text color="gray.600" mb={4}>Generate questions from your content and answer them below.</Text>

        {generating && (
          <Alert status="info" variant="subtle" mb={4} borderRadius="12px">
            <AlertIcon /> Generating questions… this may take a little while.
          </Alert>
        )}

        <Box
          bg="white"
          borderWidth="1px"
          borderColor="gray.200"
          borderRadius="12px"
          boxShadow="0 2px 8px rgba(0,0,0,0.06)"
          p={6}
          mb={6}
        >
          <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
            <FormControl isRequired>
              <FormLabel>Content ID</FormLabel>
              <Input value={contentId} onChange={(e: ChangeEvent<HTMLInputElement>) => setContentId(e.target.value)} placeholder="Paste content id from previous step" />
            </FormControl>
            <FormControl maxW={{ md: '160px' }}>
              <FormLabel>Count</FormLabel>
              <NumberInput min={1} max={20} value={count} onChange={(_str: string, v: number) => setCount(Number.isNaN(v) ? 1 : v)}>
                <NumberInputField />
              </NumberInput>
            </FormControl>
            <FormControl maxW={{ md: '220px' }}>
              <FormLabel>Type</FormLabel>
              <Select value={type} onChange={(e: ChangeEvent<HTMLSelectElement>) => setType(e.target.value)}>
                <option>Multiple Choice</option>
                <option>True/False</option>
                <option>Short Answer</option>
              </Select>
            </FormControl>
            <Button 
              onClick={onGenerate}
              isLoading={loading}
              leftIcon={<Icon as={MdBolt} />}
              colorScheme="purple"
              alignSelf={{ base: 'stretch', md: 'end' }}
              height={{ base: '48px', md: '40px' }}
              mt={{ base: 2, md: 6 }}
              px={6}
              borderRadius="10px"
            >
              Generate
            </Button>
          </Stack>
        </Box>

        {questions.length === 0 && (
          <Box borderWidth="1px" borderColor="gray.200" borderRadius="12px" p={8} bg="gray.50" textAlign="center" color="gray.600">
            No questions yet. Enter a valid content id and click Generate.
          </Box>
        )}

        {questions.length > 0 && (
          <Box
            bg="white"
            borderWidth="1px"
            borderColor="gray.200"
            borderRadius="12px"
            boxShadow="0 2px 8px rgba(0,0,0,0.06)"
            p={4}
            mb={4}
          >
            <HStack justify="space-between" align="center">
              <HStack spacing={3}>
                <Badge colorScheme="purple">Total: {questions.length}</Badge>
                <Badge colorScheme="green">Answered: {answeredCount}</Badge>
                <Badge colorScheme="gray">Remaining: {Math.max(0, questions.length - answeredCount)}</Badge>
              </HStack>
              <Text color="gray.600" fontSize="sm">Answer all questions, then submit.</Text>
            </HStack>
            <HStack spacing={2} overflowX="auto" mt={3} py={1}>
              {questions.map((_q, i) => {
                const answered = !!answers[i]
                const scheme: any = answered ? 'green' : 'gray'
                return (
                  <Button key={i} size="sm" variant={answered ? 'solid' : 'outline'} colorScheme={scheme} onClick={() => {
                    const ref = questionRefs.current[i]
                    if (ref) ref.scrollIntoView({ behavior: 'smooth', block: 'start' })
                  }}>
                    Q{i + 1}
                  </Button>
                )
              })}
            </HStack>
          </Box>
        )}

        <VStack spacing={4} align="stretch">
          {questions.map((q: Question, idx: number) => {
            const isAnswered = !!answers[idx]
            return (
            <Box key={idx} ref={(el) => (questionRefs.current[idx] = el)} p={6} bg="white" borderWidth="1px" borderColor={isAnswered ? 'green.200' : 'gray.200'} borderRadius="12px" boxShadow="0 2px 6px rgba(0,0,0,0.04)">
              <HStack justify="space-between" align="center" mb={2}>
                <HStack spacing={3}>
                  <Badge colorScheme={isAnswered ? 'green' : 'gray'}>Q{idx + 1}</Badge>
                  <Text fontWeight="700">{q.question}</Text>
                </HStack>
                <Badge variant="subtle" colorScheme="purple">{q.type}</Badge>
              </HStack>
              <Text fontSize="sm" color="gray.500" mb={3}>Choose one:</Text>
              {q.type === 'Multiple Choice' && (
                <RadioGroup value={answers[idx]?.toString() || ''} onChange={(val: string) => setAnswers((a: Record<string, string>) => ({ ...a, [idx]: val }))}>
                  <VStack align="stretch" spacing={2}>
                    {q.options?.map((opt: string, j: number) => (
                      <Radio key={j} value={opt}>{String.fromCharCode(65 + j)}. {opt}</Radio>
                    ))}
                  </VStack>
                </RadioGroup>
              )}
              {q.type === 'True/False' && (
                <RadioGroup value={answers[idx]?.toString() || ''} onChange={(val: string) => setAnswers((a: Record<string, string>) => ({ ...a, [idx]: val }))}>
                  <HStack spacing={6}>
                    {['True', 'False'].map((opt) => (
                      <Radio key={opt} value={opt}>{opt}</Radio>
                    ))}
                  </HStack>
                </RadioGroup>
              )}
              {q.type === 'Short Answer' && (
                <Textarea placeholder="Your answer" value={answers[idx]?.toString() || ''} onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setAnswers((a: Record<string, string>) => ({ ...a, [idx]: e.target.value }))} />
              )}
            </Box>
          )})}
        </VStack>

        {questions.length > 0 && (
          <>
            <Divider my={6} />
            <HStack justify="flex-end">
              <Button onClick={onSubmit} isLoading={loading} colorScheme="purple">Submit Answers</Button>
            </HStack>
          </>
        )}
      </Container>
    </PrivateLayout>
  )
}
