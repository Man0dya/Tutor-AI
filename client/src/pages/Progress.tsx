import { Accordion, AccordionButton, AccordionIcon, AccordionItem, AccordionPanel, Box, Button, Container, Divider, Heading, HStack, SimpleGrid, Stack, Stat, StatHelpText, StatLabel, StatNumber, Text } from '@chakra-ui/react'
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
                  <Text fontSize="sm" color="gray.500">{new Date(c.createdAt).toLocaleString()}</Text>
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

        <Box borderWidth="1px" rounded="md" p={4} mt={8}>
          <Heading size="md" mb={3}>Past Chats</Heading>
          {!(data.threads ?? []).length && <Text color="gray.500">No threads yet</Text>}
          {(data.threads ?? []).length > 0 && (
            <Accordion allowMultiple>
              {(data.threads ?? []).map((thread) => (
                <AccordionItem key={thread.content.id}>
                  <h2>
                    <AccordionButton>
                      <Box as="span" flex="1" textAlign="left">
                        <Text fontWeight="bold">Content:</Text>
                        <Text noOfLines={1}>{thread.content.topic}</Text>
                        <Text fontSize="sm" color="gray.500">{new Date(thread.content.createdAt).toLocaleString()}</Text>
                      </Box>
                      <AccordionIcon />
                    </AccordionButton>
                  </h2>
                  <AccordionPanel pb={4}>
                    <Stack spacing={4}>
                      {thread.questionSets.length === 0 && (
                        <Text color="gray.500">No question sets in this thread</Text>
                      )}
                      {thread.questionSets.map((qs) => (
                        <Box key={qs.id} borderWidth="1px" rounded="md" p={3}>
                          <HStack justify="space-between" mb={2}>
                            <Text fontWeight="semibold">Question Set</Text>
                            <Text fontSize="sm" color="gray.500">{new Date(qs.createdAt).toLocaleString()}</Text>
                          </HStack>
                          <Text mb={2}>Questions: {qs.questionCount}</Text>
                          <Divider my={2} />
                          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
                            <Box>
                              <Text fontWeight="semibold" mb={1}>Answers</Text>
                              <Stack spacing={1}>
                                {qs.answers.length === 0 && <Text color="gray.500">No answers</Text>}
                                {qs.answers.map((a) => (
                                  <HStack key={a.id} justify="space-between">
                                    <Text>Submitted</Text>
                                    <Text fontSize="sm" color="gray.500">{new Date(a.submittedAt).toLocaleString()}</Text>
                                  </HStack>
                                ))}
                              </Stack>
                            </Box>
                            <Box>
                              <Text fontWeight="semibold" mb={1}>Feedback</Text>
                              <Stack spacing={1}>
                                {qs.feedback.length === 0 && <Text color="gray.500">No feedback</Text>}
                                {qs.feedback.map((fb) => (
                                  <HStack key={fb.id} justify="space-between">
                                    <Text>Score: {(fb.overallScore ?? 0).toFixed?.(1) ?? fb.overallScore}%</Text>
                                    <HStack>
                                      <Text fontSize="sm" color="gray.500">{new Date(fb.createdAt).toLocaleString()}</Text>
                                      <Button as={RouterLink} to={`/feedback?id=${encodeURIComponent(fb.id)}`} size="xs" variant="outline">View</Button>
                                    </HStack>
                                  </HStack>
                                ))}
                              </Stack>
                            </Box>
                          </SimpleGrid>
                        </Box>
                      ))}
                    </Stack>
                  </AccordionPanel>
                </AccordionItem>
              ))}
            </Accordion>
          )}
        </Box>
      </Container>
    </Box>
  )
}
