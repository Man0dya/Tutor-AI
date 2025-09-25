import { useState, type ChangeEvent } from 'react'
import { Box, Button, FormControl, FormLabel, Heading, Input, Select, Stack, Textarea, useToast, SimpleGrid, Text, Icon, HStack, Divider } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { generateContent, getErrorMessage } from '../api/client'
import { useNavigate } from 'react-router-dom'
import { MdAutoAwesome, MdArrowForward } from 'react-icons/md'
import Markdown from '../components/Markdown'

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
      toast({ 
        title: 'Topic Required', 
        description: 'Please enter a topic to generate content',
        status: 'warning',
        duration: 3000,
        isClosable: true
      })
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
      toast({ 
        title: 'Content Generated Successfully!', 
        description: 'Your personalized study material is ready',
        status: 'success',
        duration: 4000,
        isClosable: true
      })
    } catch (err: any) {
      toast({ 
        title: 'Generation Failed', 
        description: getErrorMessage(err) || 'Please try again', 
        status: 'error',
        duration: 5000,
        isClosable: true
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <PrivateLayout>
      <Stack spacing={8}>
        <Box>
          <HStack mb={2}>
            <Icon as={MdAutoAwesome} boxSize={8} color="purple.500" />
            <Heading size="xl" color="gray.800">Content Generator</Heading>
          </HStack>
          <Text color="gray.600" fontSize="lg">
            Create personalized study materials tailored to your learning needs
          </Text>
        </Box>

        <Box
          bg="white"
          p={8}
          borderRadius="16px"
          borderWidth="1px"
          borderColor="gray.200"
          boxShadow="0 2px 8px rgba(0, 0, 0, 0.06)"
        >
          <Stack spacing={6}>
            <FormControl isRequired>
              <FormLabel fontWeight="600" color="gray.700" mb={3}>
                What would you like to learn about?
              </FormLabel>
              <Input 
                value={topic} 
                onChange={(e: ChangeEvent<HTMLInputElement>) => setTopic(e.target.value)} 
                placeholder="e.g., Photosynthesis, Machine Learning, World War II..."
                size="lg"
                borderRadius="10px"
                borderColor="gray.300"
                _focus={{ borderColor: 'purple.400', boxShadow: '0 0 0 1px purple.400' }}
                bg="gray.50"
              />
            </FormControl>

            <FormControl>
              <FormLabel fontWeight="600" color="gray.700" mb={3}>
                Learning Objectives (Optional)
              </FormLabel>
              <Textarea 
                value={objectives} 
                onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setObjectives(e.target.value)} 
                placeholder="Enter specific learning goals, one per line&#10;e.g., Understand the basic process&#10;Learn key terminology&#10;Identify real-world applications"
                rows={4}
                borderRadius="10px"
                borderColor="gray.300"
                _focus={{ borderColor: 'purple.400', boxShadow: '0 0 0 1px purple.400' }}
                bg="gray.50"
              />
            </FormControl>

            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
              <FormControl>
                <FormLabel fontWeight="600" color="gray.700" mb={3}>Difficulty Level</FormLabel>
                <Select 
                  value={difficulty} 
                  onChange={(e: ChangeEvent<HTMLSelectElement>) => setDifficulty(e.target.value)}
                  borderRadius="10px"
                  borderColor="gray.300"
                  _focus={{ borderColor: 'purple.400', boxShadow: '0 0 0 1px purple.400' }}
                  bg="gray.50"
                >
                  <option>Beginner</option>
                  <option>Intermediate</option>
                  <option>Advanced</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel fontWeight="600" color="gray.700" mb={3}>Subject Area</FormLabel>
                <Select 
                  value={subject} 
                  onChange={(e: ChangeEvent<HTMLSelectElement>) => setSubject(e.target.value)}
                  borderRadius="10px"
                  borderColor="gray.300"
                  _focus={{ borderColor: 'purple.400', boxShadow: '0 0 0 1px purple.400' }}
                  bg="gray.50"
                >
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
                <FormLabel fontWeight="600" color="gray.700" mb={3}>Content Type</FormLabel>
                <Select 
                  value={contentType} 
                  onChange={(e: ChangeEvent<HTMLSelectElement>) => setContentType(e.target.value)}
                  borderRadius="10px"
                  borderColor="gray.300"
                  _focus={{ borderColor: 'purple.400', boxShadow: '0 0 0 1px purple.400' }}
                  bg="gray.50"
                >
                  <option>Study Notes</option>
                  <option>Tutorial</option>
                  <option>Explanation</option>
                  <option>Summary</option>
                  <option>Comprehensive Guide</option>
                </Select>
              </FormControl>
            </SimpleGrid>

            <Button 
              onClick={onGenerate} 
              isLoading={loading}
              loadingText="Generating content..."
              size="lg"
              bgGradient="linear(to-r, purple.500, blue.500)"
              color="white"
              borderRadius="12px"
              leftIcon={<Icon as={MdAutoAwesome} />}
              _hover={{
                bgGradient: "linear(to-r, purple.600, blue.600)",
                transform: "translateY(-1px)",
              }}
              _active={{
                transform: "translateY(0)",
              }}
              transition="all 0.2s ease"
              py={6}
            >
              Generate Content
            </Button>
          </Stack>
        </Box>

        {content && (
          <Box
            bg="white"
            borderRadius="16px"
            borderWidth="1px"
            borderColor="gray.200"
            boxShadow="0 2px 8px rgba(0, 0, 0, 0.06)"
            overflow="hidden"
          >
            <Box bg="purple.50" px={8} py={4}>
              <Heading size="lg" color="purple.700">Generated Study Material</Heading>
              <Text color="purple.600">Ready for your review</Text>
            </Box>
            
            <Box p={8}>
              <Markdown source={content} />
            </Box>

            <Divider />
            
            <Box p={8}>
              <Text fontSize="sm" color="gray.600" mb={4}>
                What would you like to do next?
              </Text>
              <HStack spacing={4}>
                <Button 
                  onClick={() => navigate(`/questions?content_id=${contentId}`)} 
                  bgGradient="linear(to-r, blue.500, teal.500)"
                  color="white"
                  borderRadius="10px"
                  rightIcon={<Icon as={MdArrowForward} />}
                  _hover={{
                    bgGradient: "linear(to-r, blue.600, teal.600)",
                    transform: "translateY(-1px)",
                  }}
                >
                  Create Questions
                </Button>
                <Button 
                  onClick={() => navigate('/dashboard')} 
                  variant="outline"
                  borderRadius="10px"
                  borderColor="gray.300"
                  _hover={{ bg: 'gray.50' }}
                >
                  Back to Dashboard
                </Button>
              </HStack>
            </Box>
          </Box>
        )}
      </Stack>
    </PrivateLayout>
  )
}
