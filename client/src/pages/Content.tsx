import { useState, type ChangeEvent } from 'react'
import { Box, Button, Container, FormControl, FormLabel, Heading, Input, Select, Stack, Textarea, useToast } from '@chakra-ui/react'
import Navbar from '../components/Navbar'
import { generateContent, getErrorMessage } from '../api/client'
import { useNavigate } from 'react-router-dom'

export default function ContentPage() {
  const [topic, setTopic] = useState('')
  const [subject, setSubject] = useState('General')
  const [difficulty, setDifficulty] = useState('Beginner')
  const [contentType, setContentType] = useState('Study Notes')
  const [objectives, setObjectives] = useState('')
  const [loading, setLoading] = useState(false)
  const [content, setContent] = useState<string>('')
  const [contentId, setContentId] = useState<string>('')
  const toast = useToast()
  const navigate = useNavigate()

  const onGenerate = async () => {
    if (!topic.trim()) {
      toast({ title: 'Enter a topic', status: 'warning' })
      return
    }
    setLoading(true)
    try {
      const learning_objectives = objectives
        .split('\n')
        .map((s: string) => s.trim())
        .filter(Boolean)
  const res = await generateContent({ topic, subject, difficulty, contentType, learningObjectives: learning_objectives })
  setContent(res.content)
  setContentId(res.id)
      toast({ title: 'Content generated', status: 'success' })
    } catch (err: any) {
      toast({ title: 'Failed to generate', description: getErrorMessage(err) || 'Try again', status: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Navbar />
      <Container maxW="5xl" py={10}>
        <Heading mb={6}>Content Generator</Heading>
        <Stack spacing={4} maxW="3xl">
          <FormControl isRequired>
            <FormLabel>Topic</FormLabel>
            <Input value={topic} onChange={(e: ChangeEvent<HTMLInputElement>) => setTopic(e.target.value)} placeholder="Photosynthesis, Machine Learning, ..." />
          </FormControl>
          <FormControl>
            <FormLabel>Learning Objectives (one per line)</FormLabel>
            <Textarea value={objectives} onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setObjectives(e.target.value)} rows={4} />
          </FormControl>
          <Stack direction={{ base: 'column', md: 'row' }}>
            <FormControl>
              <FormLabel>Difficulty</FormLabel>
              <Select value={difficulty} onChange={(e: ChangeEvent<HTMLSelectElement>) => setDifficulty(e.target.value)}>
                <option>Beginner</option>
                <option>Intermediate</option>
                <option>Advanced</option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel>Subject</FormLabel>
              <Select value={subject} onChange={(e: ChangeEvent<HTMLSelectElement>) => setSubject(e.target.value)}>
                <option>Science</option>
                <option>Mathematics</option>
                <option>Computer Science</option>
                <option>History</option>
                <option>Literature</option>
                <option>Languages</option>
                <option>Business</option>
                <option>Arts</option>
                <option>General</option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel>Content Type</FormLabel>
              <Select value={contentType} onChange={(e: ChangeEvent<HTMLSelectElement>) => setContentType(e.target.value)}>
                <option>Study Notes</option>
                <option>Tutorial</option>
                <option>Explanation</option>
                <option>Summary</option>
                <option>Comprehensive Guide</option>
              </Select>
            </FormControl>
          </Stack>
          <Button onClick={onGenerate} isLoading={loading} colorScheme="teal">Generate</Button>
        </Stack>
        {content && (
          <Box mt={10} p={6} borderWidth="1px" rounded="lg">
            <Heading size="md" mb={3}>Study Notes</Heading>
            <div dangerouslySetInnerHTML={{ __html: content }} />
            <Stack direction={{ base: 'column', md: 'row' }} mt={6}>
              <Button onClick={() => navigate(`/questions?content_id=${contentId}`)} colorScheme="purple">Create Questions</Button>
              <Button onClick={() => navigate('/dashboard')} variant="outline">Back to Dashboard</Button>
            </Stack>
          </Box>
        )}
      </Container>
    </Box>
  )
}
