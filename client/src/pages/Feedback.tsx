import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Box,
  Container,
  Heading,
  Text,
  Stack,
  Badge,
  Divider,
  HStack,
  VStack,
  Button,
  IconButton,
  Tooltip,
  CircularProgress,
  CircularProgressLabel,
  Tag,
  TagLabel,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionIcon,
  AccordionPanel,
  Alert,
  AlertIcon,
  Skeleton,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  FormControl,
  FormLabel,
  Switch,
  useToast,
  useColorModeValue,
} from '@chakra-ui/react'
import { IoShareSocial, IoCopy, IoDownload } from 'react-icons/io5'
import PrivateLayout from '../components/PrivateLayout'
import Markdown from '../components/Markdown'
import { useLocation } from 'react-router-dom'
import { api, type FeedbackOut, getErrorMessage } from '../api/client'

export default function FeedbackPage() {
  const { search } = useLocation()
  const id = useMemo(() => new URLSearchParams(search).get('id'), [search])
  const [feedback, setFeedback] = useState<FeedbackOut | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [compactView, setCompactView] = useState<boolean>(false)
  const toast = useToast()

  useEffect(() => {
    if (!id) return
    setIsLoading(true)
    api.get<FeedbackOut>(`/answers/feedback/${id}`)
      .then(res => setFeedback(res.data))
      .catch(err => setError(getErrorMessage(err)))
      .finally(() => setIsLoading(false))
  }, [id])

  const overallScore = useMemo(() => {
    const score = feedback?.overallScore
    if (typeof score !== 'number' || Number.isNaN(score)) return null
    return Math.max(0, Math.min(100, Number(score)))
  }, [feedback])

  const evaluationStats = useMemo(() => {
    const evals: any[] = Array.isArray(feedback?.individualEvaluations) ? feedback!.individualEvaluations as any[] : []
    const total = evals.length
    const correct = evals.reduce((acc, ev) => acc + (ev?.is_correct ? 1 : 0), 0)
    const accuracy = total > 0 ? Math.round((correct / total) * 100) : null
    return { total, correct, accuracy }
  }, [feedback])

  const cardBg = useColorModeValue('white', 'gray.800')
  const cardBorder = useColorModeValue('gray.200', 'gray.700')
  const subdued = useColorModeValue('gray.600', 'gray.300')
  const printRef = useRef<HTMLDivElement | null>(null)

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text || '')
      ;(toast as any)?.({ title: 'Copied', status: 'success', duration: 2000, isClosable: true })
    } catch {
      ;(toast as any)?.({ title: 'Copy failed', status: 'error', duration: 2000, isClosable: true })
    }
  }

  const handleShare = async () => {
    const url = window.location.href
    try {
      if (navigator.share) {
        await navigator.share({ title: 'Tutor AI Feedback', url })
      } else {
        await navigator.clipboard.writeText(url)
        ;(toast as any)?.({ title: 'Link copied', status: 'success', duration: 2000, isClosable: true })
      }
    } catch {
      // user canceled or unsupported
    }
  }

  const onDownloadPdf = () => {
    if (!feedback) return
    try {
      const safe = (v: any) => String(v ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      const evals: any[] = Array.isArray(feedback.individualEvaluations) ? feedback.individualEvaluations as any[] : []
      const statsHtml = `
        <div class="card">
          <h2 style="margin:0 0 8px">Summary</h2>
          <div style="display:flex;gap:16px;flex-wrap:wrap">
            <div><div class="muted">Overall Score</div><div class="score">${overallScore?.toFixed(1) ?? '--'}%</div></div>
            <div><div class="muted">Accuracy</div><div class="score">${evaluationStats.accuracy !== null ? evaluationStats.accuracy + '%' : '--'}</div></div>
            <div><div class="muted">Correct Answers</div><div class="score">${evaluationStats.correct}/${evaluationStats.total}</div></div>
          </div>
        </div>`
      const detailsHtml = `
        <div class="card">
          <h2 class="section-title">Detailed Feedback</h2>
          <div style="white-space:pre-wrap" class="muted">${safe(feedback.detailedFeedback)}</div>
        </div>`
      const suggestionsHtml = feedback.studySuggestions ? `
        <div class="card">
          <h2 class="section-title">Study Suggestions</h2>
          <div style="white-space:pre-wrap" class="muted">${safe(feedback.studySuggestions)}</div>
        </div>` : ''
      const questionsHtml = evals.length > 0 ? `
        <div class="card">
          <h2 class="section-title">Per-Question Marking</h2>
          ${evals.map((ev: any, idx: number) => {
            const isCorrect = ev?.is_correct
            const scorePct = Math.round(Number(ev?.score) || 0)
            return `<div style="border-top:1px solid #e5e7eb;padding-top:12px;margin-top:12px">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                <span class="tag" style="background:${isCorrect ? '#dcfce7' : '#ffedd5'};color:${isCorrect ? '#065f46' : '#9a3412'}">${isCorrect ? 'Correct' : 'Review'}</span>
                <strong>Q${idx + 1}</strong>
                <span class="muted" style="margin-left:auto">${scorePct}%</span>
              </div>
              <div class="muted"><strong>Question:</strong> ${safe(ev?.question_text)}</div>
              <div class="muted"><strong>Your Answer:</strong> ${safe(ev?.user_answer)}</div>
              ${'correct_answer' in ev ? `<div class="muted"><strong>Correct Answer:</strong> ${safe(ev?.correct_answer)}</div>` : ''}
              ${ev?.feedback ? `<div class="muted"><strong>Notes:</strong> ${safe(ev?.feedback)}</div>` : ''}
            </div>`
          }).join('')}
        </div>` : ''

      const html = `<!doctype html><html><head><title>Assessment Feedback</title>
        <style>
          *{box-sizing:border-box}
          body{font-family:Inter,Segoe UI,Roboto,sans-serif;padding:32px;line-height:1.75;color:#1f2937}
          h1,h2,h3{color:#111827}
          .card{border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin:12px 0;background:#ffffff}
          .muted{color:#374151}
          .tag{display:inline-block;padding:2px 8px;border-radius:9999px;background:#f3f4f6;color:#374151;margin-right:8px;font-size:12px}
          img{max-width:100%;height:auto}
          svg{display:none}
          button,a{display:none}
        </style>
      </head><body>
        <h1 style="margin-top:0">Assessment Feedback</h1>
        ${statsHtml}
        ${detailsHtml}
        ${suggestionsHtml}
        ${questionsHtml}
      </body></html>`

      const win = window.open('', '_blank', 'width=1000,height=800')
      if (!win) return
      win.document.write(html)
      win.document.close()
      win.focus()
      win.print()
      win.close()
    } catch (e) {
      toast({ title: 'Download failed', status: 'error' })
    }
  }

  return (
    <PrivateLayout>
      <Container maxW="5xl" py={6}>
        <Box
          bgGradient="linear(to-r, purple.500, blue.500)"
          color="white"
          borderRadius="xl"
          p={6}
          mb={6}
          position="relative"
          overflow="hidden"
        >
          <HStack align="start" spacing={6}>
            <VStack align="start" spacing={2} flex={1}>
              <Heading size="lg">Your Feedback</Heading>
              <Text opacity={0.9}>Personalized insights and next steps to improve faster.</Text>
              <HStack spacing={2} pt={2}>
                <Button as="a" href="/dashboard" size="sm" borderRadius="lg">Back</Button>
                <Button as="a" href="/content" size="sm" variant="outline" borderRadius="lg" color="white" borderColor="whiteAlpha.700">Review Content</Button>
                <Tooltip label="Share" hasArrow>
                  <IconButton aria-label="Share" icon={<IoShareSocial />} size="sm" variant="outline" borderRadius="lg" color="white" borderColor="whiteAlpha.700" onClick={handleShare} />
                </Tooltip>
                <Tooltip label="Copy Link" hasArrow>
                  <IconButton aria-label="Copy link" icon={<IoCopy />} size="sm" variant="outline" borderRadius="lg" color="white" borderColor="whiteAlpha.700" onClick={() => handleCopy(window.location.href)} />
                </Tooltip>
                <Tooltip label="Download / Print" hasArrow>
                  <IconButton aria-label="Download or print" icon={<IoDownload />} size="sm" variant="outline" borderRadius="lg" color="white" borderColor="whiteAlpha.700" onClick={onDownloadPdf} />
                </Tooltip>
              </HStack>
            </VStack>
            <VStack align="center" justify="center" minW="104px">
              <CircularProgress value={overallScore ?? 0} size="96px" color="white" trackColor="whiteAlpha.400" thickness="10px">
                <CircularProgressLabel fontWeight="bold">{overallScore?.toFixed(0) ?? '--'}%</CircularProgressLabel>
              </CircularProgress>
              <Text fontSize="sm" opacity={0.9} mt={1}>Overall</Text>
            </VStack>
          </HStack>
        </Box>

        {!id && (
          <Alert status="info" mb={6} borderRadius="md">
            <AlertIcon />
            Missing feedback id. Please access this page from your results.
          </Alert>
        )}

        {error && (
          <Alert status="error" mb={6} borderRadius="md">
            <AlertIcon />{error}
          </Alert>
        )}

        {isLoading && (
          <Stack spacing={6}>
            <Skeleton height="120px" borderRadius="md" />
            <Skeleton height="200px" borderRadius="md" />
            <Skeleton height="320px" borderRadius="md" />
          </Stack>
        )}

        {!isLoading && feedback && (
          <Stack spacing={6} ref={printRef}>
            <Box bg={cardBg} borderWidth="1px" borderColor={cardBorder} rounded="lg" p={6} className="professional-card">
              <HStack justify="space-between" mb={3}>
                <Heading size="md">Quick Stats</Heading>
                <FormControl display="flex" alignItems="center" width="auto">
                  <FormLabel htmlFor="compact-view" mb="0" fontSize="sm" color={subdued}>
                    Compact view
                  </FormLabel>
                  <Switch id="compact-view" isChecked={compactView} onChange={(e) => setCompactView(e.target.checked)} colorScheme="purple" />
                </FormControl>
              </HStack>
              <SimpleGrid columns={{ base: 1, sm: 3 }} spacing={4}>
                <Stat p={3} borderWidth="1px" borderColor={cardBorder} rounded="md">
                  <StatLabel>Score</StatLabel>
                  <StatNumber>{overallScore?.toFixed(1) ?? '--'}%</StatNumber>
                </Stat>
                <Stat p={3} borderWidth="1px" borderColor={cardBorder} rounded="md">
                  <StatLabel>Accuracy</StatLabel>
                  <StatNumber>{evaluationStats.accuracy !== null ? `${evaluationStats.accuracy}%` : '--'}</StatNumber>
                </Stat>
                <Stat p={3} borderWidth="1px" borderColor={cardBorder} rounded="md">
                  <StatLabel>Correct Answers</StatLabel>
                  <StatNumber>{evaluationStats.correct}/{evaluationStats.total}</StatNumber>
                </Stat>
              </SimpleGrid>
            </Box>

            <Box bg={cardBg} borderWidth="1px" borderColor={cardBorder} rounded="lg" p={6} className="professional-card">
              <Heading size="md" mb={3}>Detailed Feedback</Heading>
              <Box color={subdued}>
                <Markdown source={String(feedback.detailedFeedback || '')} />
              </Box>
              <HStack mt={4} spacing={3}>
                <Button size="sm" variant="outline" borderRadius="lg" onClick={() => navigator.clipboard?.writeText(String(feedback.detailedFeedback || ''))}>Copy</Button>
              </HStack>
            </Box>

            {feedback.studySuggestions && (
              <Box bg={cardBg} borderWidth="1px" borderColor={cardBorder} rounded="lg" p={6} className="professional-card">
                <Heading size="md" mb={3}>Study Suggestions</Heading>
                <Box color={subdued}>
                  <Markdown source={String(feedback.studySuggestions || '')} />
                </Box>
                <HStack mt={4} spacing={3}>
                  <Button size="sm" variant="outline" borderRadius="lg" as="a" href="/content">
                    Explore Suggested Topics
                  </Button>
                  <Button size="sm" borderRadius="lg" colorScheme="purple" as="a" href="/questions">Try Another Quiz</Button>
                </HStack>
              </Box>
            )}

            {feedback.individualEvaluations && feedback.individualEvaluations.length > 0 && (
              <Box bg={cardBg} borderWidth="1px" borderColor={cardBorder} rounded="lg" p={2} className="professional-card">
                <Heading size="md" mb={3} px={4} pt={4}>Per-Question Marking</Heading>
                <Accordion allowMultiple defaultIndex={compactView ? [] : [0]}>
                  {feedback.individualEvaluations.map((ev: any, idx: number) => {
                    const isCorrect = Boolean(ev.is_correct)
                    const scorePct = Math.round(Number(ev.score) || 0)
                    return (
                      <AccordionItem key={idx} borderTopWidth={idx === 0 ? '0' : '1px'} borderColor={cardBorder}>
                        <h2>
                          <AccordionButton _expanded={{ bg: isCorrect ? 'green.50' : 'orange.50' }}>
                            <HStack flex="1" textAlign="left" spacing={3} align="center">
                              <Tag size="sm" colorScheme={isCorrect ? 'green' : 'orange'} borderRadius="full">
                                <TagLabel>{isCorrect ? 'Correct' : 'Review'}</TagLabel>
                              </Tag>
                              <Text fontWeight="semibold">Q{idx + 1}</Text>
                              <Text noOfLines={compactView ? 1 : 2} color={subdued}> {ev.question_text} </Text>
                            </HStack>
                            <Badge colorScheme={isCorrect ? 'green' : 'red'} mr={2}>{scorePct}%</Badge>
                            <AccordionIcon />
                          </AccordionButton>
                        </h2>
                        <AccordionPanel pb={4}>
                          <VStack align="start" spacing={2}>
                            <Text noOfLines={compactView ? 2 : undefined}><Text as="span" fontWeight="semibold">Your Answer:</Text> {ev.user_answer}</Text>
                            {'correct_answer' in ev && (
                              <Text noOfLines={compactView ? 2 : undefined}><Text as="span" fontWeight="semibold">Correct Answer:</Text> {ev.correct_answer}</Text>
                            )}
                            {ev.feedback && (
                              <Box color={subdued}>
                                <Text as="span" fontWeight="semibold">Notes:</Text>
                                <Markdown source={String(ev.feedback || '')} />
                              </Box>
                            )}
                          </VStack>
                        </AccordionPanel>
                      </AccordionItem>
                    )
                  })}
                </Accordion>
              </Box>
            )}

            {!feedback.individualEvaluations?.length && (
              <Box bg={cardBg} borderWidth="1px" borderColor={cardBorder} rounded="lg" p={6} className="professional-card" textAlign="center">
                <Heading size="sm" mb={2}>No question-level feedback available</Heading>
                <Text color={subdued}>Complete a quiz to see detailed per-question insights.</Text>
              </Box>
            )}
          </Stack>
        )}
      </Container>
    </PrivateLayout>
  )
}
