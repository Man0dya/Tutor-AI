import { Box, Button, Container, Flex, Heading, HStack, Stack, Text } from '@chakra-ui/react'
import { Link as RouterLink } from 'react-router-dom'
import Navbar from '../components/Navbar'

export default function Landing() {
  return (
    <Box>
      <Navbar />
      <Container maxW="6xl" py={16}>
        <Stack spacing={8} textAlign="center">
          <Heading size="2xl">Your AI‑Powered Learning Companion</Heading>
          <Text fontSize="lg" color="gray.500">
            Generate personalized study notes, practice questions, and get instant feedback.
          </Text>
          <HStack spacing={4} justify="center">
            <Button as={RouterLink} to="/signup" colorScheme="teal" size="lg">Get Started</Button>
            <Button as={RouterLink} to="/login" size="lg" variant="outline">I already have an account</Button>
          </HStack>
        </Stack>
        <Flex mt={16} gap={6} wrap="wrap" justify="center">
          {[
            { title: 'Content Generator', desc: 'Create concise, structured learning materials.' },
            { title: 'Question Setter', desc: 'MCQ, T/F, short answers with difficulty control.' },
            { title: 'Feedback & Progress', desc: 'Personalized feedback with analytics.' },
          ].map((c) => (
            <Box key={c.title} p={6} borderWidth="1px" rounded="lg" maxW="sm" flex="1 1 260px">
              <Heading size="md" mb={2}>{c.title}</Heading>
              <Text color="gray.500">{c.desc}</Text>
            </Box>
          ))}
        </Flex>
      </Container>
    </Box>
  )
}
