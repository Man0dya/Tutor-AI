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
  Icon,
} from '@chakra-ui/react'
import { IoShareSocial, IoCopy, IoDownload, IoCheckmarkCircle, IoSchool } from 'react-icons/io5'
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
        {/* Modern Header with gradient and score */}
        <Box
          bg="surface"
          borderWidth="1px"
          borderColor="border"
          borderRadius="16px"
          boxShadow={{ base: 'lg', _dark: 'none' }}
          p={6}
          mb={6}
          position="relative"
          overflow="hidden"
        >
          <HStack align="start" spacing={6} justify="space-between">
            <VStack align="start" spacing={3} flex={1}>
              <HStack spacing={2}>
                <Icon as={IoCheckmarkCircle} boxSize={7} color="purple.500" />
                <Heading size="lg" color="text">Your Feedback</Heading>
              </HStack>
              <Text color="muted">Personalized insights and next steps to improve faster.</Text>
              <HStack spacing={2} pt={2} flexWrap="wrap">
                <Button 
                  as="a" 
                  href="/dashboard" 
                  size="sm" 
                  borderRadius="10px"
                  variant="outline"
                  borderColor="border"
                  _hover={{ bg: 'surface', borderColor: 'purple.400' }}
                >
                  Back
                </Button>
                <Button 
                  as="a" 
                  href="/content" 
                  size="sm" 
                  variant="outline" 
                  borderRadius="10px"
                  borderColor="border"
                  _hover={{ bg: 'surface', borderColor: 'purple.400' }}
                >
                  Review Content
                </Button>
                <Tooltip label="Share" hasArrow>
                  <IconButton 
                    aria-label="Share" 
                    icon={<IoShareSocial />} 
                    size="sm" 
                    variant="outline" 
                    borderRadius="10px"
                    borderColor="border"
                    _hover={{ bg: 'surface', borderColor: 'purple.400' }}
                    onClick={handleShare} 
                  />
                </Tooltip>
                <Tooltip label="Copy Link" hasArrow>
                  <IconButton 
                    aria-label="Copy link" 
                    icon={<IoCopy />} 
                    size="sm" 
                    variant="outline" 
                    borderRadius="10px"
                    borderColor="border"
                    _hover={{ bg: 'surface', borderColor: 'purple.400' }}
                    onClick={() => handleCopy(window.location.href)} 
                  />
                </Tooltip>
                <Tooltip label="Download / Print" hasArrow>
                  <IconButton 
                    aria-label="Download or print" 
                    icon={<IoDownload />} 
                    size="sm" 
                    variant="outline" 
                    borderRadius="10px"
                    borderColor="border"
                    _hover={{ bg: 'surface', borderColor: 'purple.400' }}
                    onClick={onDownloadPdf} 
                  />
                </Tooltip>
              </HStack>
            </VStack>
            <VStack align="center" justify="center" minW="120px" spacing={2}>
              <Box position="relative">
                <CircularProgress 
                  value={overallScore ?? 0} 
                  size="110px" 
                  color="purple.500" 
                  trackColor="border"
                  thickness="8px"
                >
                  <CircularProgressLabel 
                    fontWeight="bold" 
                    fontSize="2xl"
                    color="text"
                  >
                    {overallScore?.toFixed(0) ?? '--'}%
                  </CircularProgressLabel>
                </CircularProgress>
              </Box>
              <Text fontSize="sm" color="muted" fontWeight="500">Overall Score</Text>
            </VStack>
          </HStack>
        </Box>

        {!id && (
          <Alert status="info" mb={6} borderRadius="12px" variant="subtle">
            <AlertIcon />
            Missing feedback id. Please access this page from your results.
          </Alert>
        )}

        {error && (
          <Alert status="error" mb={6} borderRadius="12px" variant="subtle">
            <AlertIcon />{error}
          </Alert>
        )}

        {isLoading && (
          <Stack spacing={6}>
            <Skeleton height="120px" borderRadius="12px" />
            <Skeleton height="200px" borderRadius="12px" />
            <Skeleton height="320px" borderRadius="12px" />
          </Stack>
        )}

        {!isLoading && feedback && (
          <Stack spacing={6} ref={printRef}>
            <Box 
              bg="surface" 
              borderWidth="1px" 
              borderColor="border" 
              borderRadius="12px" 
              boxShadow={{ base: 'md', _dark: 'none' }}
              p={6}
            >
              <HStack justify="space-between" mb={4}>
                <Heading size="md" color="text">Quick Stats</Heading>
                <FormControl display="flex" alignItems="center" width="auto">
                  <FormLabel htmlFor="compact-view" mb="0" fontSize="sm" color="muted">
                    Compact view
                  </FormLabel>
                  <Switch 
                    id="compact-view" 
                    isChecked={compactView} 
                    onChange={(e) => setCompactView(e.target.checked)} 
                    colorScheme="purple" 
                  />
                </FormControl>
              </HStack>
              <SimpleGrid columns={{ base: 1, sm: 3 }} spacing={4}>
                <Stat 
                  p={4} 
                  borderWidth="1px" 
                  borderColor="border" 
                  borderRadius="10px"
                  bg="bg"
                >
                  <StatLabel color="muted">Score</StatLabel>
                  <StatNumber color="text">{overallScore?.toFixed(1) ?? '--'}%</StatNumber>
                </Stat>
                <Stat 
                  p={4} 
                  borderWidth="1px" 
                  borderColor="border" 
                  borderRadius="10px"
                  bg="bg"
                >
                  <StatLabel color="muted">Accuracy</StatLabel>
                  <StatNumber color="text">{evaluationStats.accuracy !== null ? `${evaluationStats.accuracy}%` : '--'}</StatNumber>
                </Stat>
                <Stat 
                  p={4} 
                  borderWidth="1px" 
                  borderColor="border" 
                  borderRadius="10px"
                  bg="bg"
                >
                  <StatLabel color="muted">Correct Answers</StatLabel>
                  <StatNumber color="text">{evaluationStats.correct}/{evaluationStats.total}</StatNumber>
                </Stat>
              </SimpleGrid>
            </Box>

            <Box 
              bg="surface" 
              borderWidth="1px" 
              borderColor="border" 
              borderRadius="12px" 
              boxShadow={{ base: 'md', _dark: 'none' }}
              p={6}
            >
              <Heading size="md" mb={4} color="text">Detailed Feedback</Heading>
              <Box color="muted">
                <Markdown source={String(feedback.detailedFeedback || '')} />
              </Box>
              <HStack mt={4} spacing={3}>
                <Button 
                  size="sm" 
                  variant="outline" 
                  borderRadius="10px"
                  borderColor="border"
                  _hover={{ bg: 'surface', borderColor: 'purple.400' }}
                  onClick={() => navigator.clipboard?.writeText(String(feedback.detailedFeedback || ''))}
                >
                  Copy
                </Button>
              </HStack>
            </Box>

            {feedback.studySuggestions && (
              <Box 
                bg="surface" 
                borderWidth="1px" 
                borderColor="border" 
                borderRadius="12px" 
                boxShadow={{ base: 'md', _dark: 'none' }}
                p={6}
              >
                <HStack spacing={2} mb={4}>
                  <Icon as={IoSchool} boxSize={5} color="purple.500" />
                  <Heading size="md" color="text">Study Suggestions</Heading>
                </HStack>
                <Box color="muted">
                  <Markdown source={String(feedback.studySuggestions || '')} />
                </Box>
                <HStack mt={4} spacing={3} flexWrap="wrap">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    borderRadius="10px"
                    borderColor="border"
                    _hover={{ bg: 'surface', borderColor: 'purple.400' }}
                    as="a" 
                    href="/content"
                  >
                    Explore Suggested Topics
                  </Button>
                  <Button 
                    size="sm" 
                    borderRadius="10px" 
                    bgGradient={{ base: 'linear(to-r, purple.500, blue.500)', _dark: 'linear(to-r, purple.400, blue.400)' }}
                    color="white"
                    _hover={{
                      bgGradient: "linear(to-r, purple.600, blue.600)",
                      transform: "translateY(-1px)",
                    }}
                    _active={{
                      transform: "translateY(0)",
                    }}
                    transition="all 0.2s ease"
                    as="a" 
                    href="/questions"
                  >
                    Try Another Quiz
                  </Button>
                </HStack>
              </Box>
            )}

            {feedback.individualEvaluations && feedback.individualEvaluations.length > 0 && (
              <Box 
                bg="surface" 
                borderWidth="1px" 
                borderColor="border" 
                borderRadius="12px" 
                boxShadow={{ base: 'md', _dark: 'none' }}
                overflow="hidden"
              >
                <Box px={6} pt={5} pb={3}>
                  <Heading size="md" color="text">Per-Question Marking</Heading>
                </Box>
                <Accordion allowMultiple defaultIndex={compactView ? [] : [0]}>
                  {feedback.individualEvaluations.map((ev: any, idx: number) => {
                    const isCorrect = Boolean(ev.is_correct)
                    const scorePct = Math.round(Number(ev.score) || 0)
                    return (
                      <AccordionItem 
                        key={idx} 
                        borderTopWidth={idx === 0 ? '0' : '1px'} 
                        borderColor="border"
                        _last={{ borderBottomWidth: 0 }}
                      >
                        <h2>
                          <AccordionButton 
                            _hover={{ bg: 'bg' }}
                            _expanded={{ 
                              bg: isCorrect 
                                ? { base: 'green.50', _dark: 'whiteAlpha.50' } 
                                : { base: 'orange.50', _dark: 'whiteAlpha.50' }
                            }}
                            py={4}
                          >
                            <HStack flex="1" textAlign="left" spacing={3} align="center">
                              <Tag 
                                size="sm" 
                                colorScheme={isCorrect ? 'green' : 'orange'} 
                                borderRadius="full"
                              >
                                <TagLabel>{isCorrect ? 'Correct' : 'Review'}</TagLabel>
                              </Tag>
                              <Text fontWeight="semibold" color="text">Q{idx + 1}</Text>
                              <Text 
                                noOfLines={compactView ? 1 : 2} 
                                color="muted"
                                flex={1}
                              > 
                                {ev.question_text} 
                              </Text>
                            </HStack>
                            <Badge 
                              colorScheme={isCorrect ? 'green' : 'red'} 
                              mr={2}
                              fontSize="sm"
                            >
                              {scorePct}%
                            </Badge>
                            <AccordionIcon color="muted" />
                          </AccordionButton>
                        </h2>
                        <AccordionPanel pb={4} bg="bg">
                          <VStack align="start" spacing={3}>
                            <Box>
                              <Text 
                                as="span" 
                                fontWeight="semibold" 
                                color="text"
                              >
                                Your Answer:
                              </Text>
                              <Text 
                                color="muted" 
                                mt={1}
                                noOfLines={compactView ? 2 : undefined}
                              >
                                {ev.user_answer}
                              </Text>
                            </Box>
                            {'correct_answer' in ev && (
                              <Box>
                                <Text 
                                  as="span" 
                                  fontWeight="semibold" 
                                  color="text"
                                >
                                  Correct Answer:
                                </Text>
                                <Text 
                                  color="muted" 
                                  mt={1}
                                  noOfLines={compactView ? 2 : undefined}
                                >
                                  {ev.correct_answer}
                                </Text>
                              </Box>
                            )}
                            {ev.feedback && (
                              <Box width="100%">
                                <Text 
                                  as="span" 
                                  fontWeight="semibold" 
                                  color="text"
                                >
                                  Notes:
                                </Text>
                                <Box color="muted" mt={1}>
                                  <Markdown source={String(ev.feedback || '')} />
                                </Box>
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
              <Box 
                bg="surface" 
                borderWidth="1px" 
                borderColor="border" 
                borderRadius="12px" 
                boxShadow={{ base: 'md', _dark: 'none' }}
                p={8} 
                textAlign="center"
              >
                <Heading size="sm" mb={2} color="text">No question-level feedback available</Heading>
                <Text color="muted">Complete a quiz to see detailed per-question insights.</Text>
              </Box>
            )}
          </Stack>
        )}
      </Container>
    </PrivateLayout>
  )
}
