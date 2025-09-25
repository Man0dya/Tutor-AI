import { useEffect, useMemo, useRef, useState } from 'react'
import { Box, Container, Heading, Text, Stack, Badge, Divider, HStack, Button, Icon, Progress, VStack, Tooltip, Flex, CircularProgress, CircularProgressLabel, Tag } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { useLocation } from 'react-router-dom'
import { api, type FeedbackOut, getErrorMessage } from '../api/client'
import Markdown from '../components/Markdown'
import { MdDownload, MdContentCopy } from 'react-icons/md'

function useQuery() {
  const { search } = useLocation()
  return new URLSearchParams(search)
}

export default function FeedbackPage() {
  const query = useQuery()
  const [feedback, setFeedback] = useState<FeedbackOut | null>(null)
  const [error, setError] = useState<string | null>(null)
  const contentRef = useRef<HTMLDivElement | null>(null)
  const evalRefs = useRef<Array<HTMLDivElement | null>>([])
  const [filter, setFilter] = useState<'all' | 'correct' | 'incorrect'>('all')
  const [collapseExplanations, setCollapseExplanations] = useState<boolean>(false)

  const filteredEvaluations = useMemo(() => {
    const list: any[] = feedback?.individualEvaluations || []
    if (filter === 'correct') return list.filter((e: any) => e.is_correct)
    if (filter === 'incorrect') return list.filter((e: any) => !e.is_correct)
    return list
  }, [feedback?.individualEvaluations, filter])

  useEffect(() => {
    const id = query.get('id')
    if (!id) return
    api.get<FeedbackOut>(`/answers/feedback/${id}`)
      .then(res => setFeedback(res.data))
      .catch(err => setError(getErrorMessage(err)))
  }, [query])

  return (
    <PrivateLayout>
      <Container maxW="7xl" py={4}>
        <HStack justify="space-between" align="center" mb={2}>
          <Box>
            <Heading>Feedback</Heading>
            <Text color="gray.600" fontSize="sm">Your performance summary and detailed insights</Text>
          </Box>
          {feedback && (
            <HStack>
              <Tooltip label="Copy all" placement="top">
                <Button size="sm" variant="outline" onClick={() => {
                  const all = JSON.stringify(feedback, null, 2)
                  navigator.clipboard.writeText(all).catch(() => {})
                }} leftIcon={<Icon as={MdContentCopy} />}>Copy</Button>
              </Tooltip>
              <Tooltip label="Download / Print" placement="top">
                <Button size="sm" variant="outline" leftIcon={<Icon as={MdDownload} />} onClick={() => {
                  if (!contentRef.current) return
                  const html = contentRef.current.innerHTML
                  const win = window.open('', '_blank', 'width=1000,height=800')
                  if (!win) return
                  win.document.write('<!doctype html><html><head><title>Feedback</title>')
                  win.document.write('<style>body{font-family:Inter,Segoe UI,Roboto,sans-serif;padding:32px;line-height:1.8;color:#1f2937} h1,h2,h3{color:#111827} .markdown-body pre{background:#111827;color:#f3f4f6;padding:12px;border-radius:8px} .markdown-body code{background:#f3f4f6;padding:2px 6px;border-radius:4px}</style>')
                  win.document.write('</head><body>')
                  win.document.write(`<div class="markdown-body">${html}</div>`) 
                  win.document.write('</body></html>')
                  win.document.close(); win.focus(); win.print(); win.close()
                }}>PDF</Button>
              </Tooltip>
            </HStack>
          )}
        </HStack>
        {error && <Text color="red.500" mb={2}>{error}</Text>}
        {feedback && (
          <Flex gap={8} align="flex-start">
            <Box ref={contentRef} flex="1 1 0%" maxW="3xl">
              <Stack spacing={6}>
                <Box borderWidth="1px" borderColor="gray.200" rounded="lg" p={6} bg="white" boxShadow="0 2px 8px rgba(0,0,0,0.06)">
                  <HStack align="center" spacing={6}>
                    <CircularProgress value={Math.max(0, Math.min(100, Number(feedback.overallScore) || 0))} color="purple.500" size="86px" thickness="10px">
                      <CircularProgressLabel>{feedback.overallScore?.toFixed(0)}%</CircularProgressLabel>
                    </CircularProgress>
                    <Box flex="1 1 0%">
                      <HStack justify="space-between" align="center" mb={2}>
                        <Heading size="md">Overall</Heading>
                        <Tag colorScheme="purple" variant="subtle">Score</Tag>
                      </HStack>
                      <Progress value={Math.max(0, Math.min(100, Number(feedback.overallScore) || 0))} colorScheme="purple" size="sm" rounded="md" mb={2} />
                      {feedback.individualEvaluations && (
                        <HStack spacing={3}>
                          <Badge colorScheme="green">Correct {feedback.individualEvaluations.filter((e: any) => e.is_correct).length}</Badge>
                          <Badge colorScheme="red">Incorrect {feedback.individualEvaluations.filter((e: any) => !e.is_correct).length}</Badge>
                        </HStack>
                      )}
                    </Box>
                  </HStack>
                </Box>

                <Box borderWidth="1px" borderColor="gray.200" rounded="lg" p={6} bg="white" boxShadow="0 2px 8px rgba(0,0,0,0.06)">
                  <Heading size="md" mb={3}>Detailed Feedback</Heading>
                  {feedback.detailedFeedback ? (
                    <Markdown source={feedback.detailedFeedback} />
                  ) : (
                    <Text color="gray.500">No detailed feedback provided.</Text>
                  )}
                </Box>

                {feedback.studySuggestions && (
                  <Box borderWidth="1px" borderColor="gray.200" rounded="lg" p={6} bg="white" boxShadow="0 2px 8px rgba(0,0,0,0.06)">
                    <Heading size="md" mb={3}>Study Suggestions</Heading>
                    <Markdown source={feedback.studySuggestions} />
                  </Box>
                )}

                {feedback.individualEvaluations && feedback.individualEvaluations.length > 0 && (
                  <Box borderWidth="1px" borderColor="gray.200" rounded="lg" p={6} bg="white" boxShadow="0 2px 8px rgba(0,0,0,0.06)">
                    <HStack justify="space-between" align="center" mb={3}>
                      <Heading size="md">Per-Question Marking</Heading>
                      <HStack>
                        <Button size="sm" variant={filter === 'all' ? 'solid' : 'ghost'} colorScheme="purple" onClick={() => setFilter('all')}>All</Button>
                        <Button size="sm" variant={filter === 'correct' ? 'solid' : 'ghost'} colorScheme="green" onClick={() => setFilter('correct')}>Correct</Button>
                        <Button size="sm" variant={filter === 'incorrect' ? 'solid' : 'ghost'} colorScheme="red" onClick={() => setFilter('incorrect')}>Incorrect</Button>
                        <Divider orientation="vertical" />
                        <Button size="sm" variant="outline" onClick={() => setCollapseExplanations(v => !v)}>{collapseExplanations ? 'Expand explanations' : 'Collapse explanations'}</Button>
                      </HStack>
                    </HStack>
                    <VStack align="stretch" spacing={4}>
                      {filteredEvaluations.map((ev: any, idx: number) => (
                        <Box
                          key={idx}
                          id={`ev-${idx}`}
                          ref={(el) => { evalRefs.current[idx] = el }}
                          p={4}
                          borderWidth="1px"
                          borderColor={ev.is_correct ? 'green.200' : 'red.200'}
                          rounded="md"
                          bg={ev.is_correct ? 'green.50' : 'red.50'}
                          sx={{ wordBreak: 'break-word', overflowWrap: 'anywhere' }}
                        >
                          <HStack justify="space-between" align="center" mb={1}>
                            <Text fontWeight="700">Q{idx + 1}</Text>
                            <Badge colorScheme={ev.is_correct ? 'green' : 'red'}>{ev.is_correct ? 'Correct' : 'Incorrect'}</Badge>
                          </HStack>
                          <Text fontWeight="600" color="gray.800" mb={1} whiteSpace="normal">{ev.question_text}</Text>
                          {'user_answer' in ev && (
                            <Text color="gray.700" whiteSpace="normal">
                              Your answer: <Badge ml={2} maxW="100%" whiteSpace="normal">{String(ev.user_answer)}</Badge>
                            </Text>
                          )}
                          {'correct_answer' in ev && (
                            <Text color="gray.700" whiteSpace="normal">
                              Correct answer: <Badge ml={2} colorScheme="purple" maxW="100%" whiteSpace="normal">{String(ev.correct_answer)}</Badge>
                            </Text>
                          )}
                          {'score' in ev && <Text mt={1}>Score: <Badge>{Math.round(Number(ev.score) || 0)}%</Badge></Text>}
                          {ev.feedback && !collapseExplanations && (
                            <Box mt={2}>
                              <Markdown source={String(ev.feedback)} />
                            </Box>
                          )}
                        </Box>
                      ))}
                    </VStack>
                  </Box>
                )}
              </Stack>
            </Box>

            {feedback.individualEvaluations && feedback.individualEvaluations.length > 0 && (
              <VStack as="aside" minW={{ base: '0', md: '320px' }} display={{ base: 'none', md: 'flex' }} position="sticky" top="92px" align="stretch">
                <Box borderWidth="1px" borderColor="purple.200" rounded="lg" p={4} bg="gray.50" boxShadow="sm">
                  <Text fontWeight="700" color="purple.700" mb={2}>Summary</Text>
                  <Divider borderColor="purple.200" mb={3} />
                  <HStack justify="space-between" mb={2}>
                    <Badge colorScheme="green">Correct: {feedback.individualEvaluations.filter((e: any) => e.is_correct).length}</Badge>
                    <Badge colorScheme="red">Incorrect: {feedback.individualEvaluations.filter((e: any) => !e.is_correct).length}</Badge>
                  </HStack>
                  <VStack align="stretch" spacing={1} maxH="70vh" overflowY="auto">
                    {feedback.individualEvaluations.map((ev: any, idx: number) => (
                      <Button
                        key={idx}
                        variant="ghost"
                        justifyContent="space-between"
                        onClick={() => {
                          const el = evalRefs.current[idx]
                          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
                        }}
                        size="sm"
                        bg="transparent"
                        _hover={{ bg: 'purple.100' }}
                        color={ev.is_correct ? 'green.700' : 'red.700'}
                        rounded="md"
                      >
                        <HStack>
                          <Text fontSize="sm">Q{idx + 1}</Text>
                        </HStack>
                        <Badge colorScheme={ev.is_correct ? 'green' : 'red'}>{ev.is_correct ? 'Correct' : 'Incorrect'}</Badge>
                      </Button>
                    ))}
                  </VStack>
                </Box>
              </VStack>
            )}
          </Flex>
        )}
      </Container>
    </PrivateLayout>
  )
}
