import { Box, Button, Container, Grid, GridItem, Heading, Stack, Text } from '@chakra-ui/react'
import Navbar from '../components/Navbar'
import { Link as RouterLink } from 'react-router-dom'

export default function Dashboard() {
  return (
    <Box>
      <Navbar />
      <Container maxW="6xl" py={10}>
        <Heading mb={6}>Dashboard</Heading>
        <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6}>
          <GridItem borderWidth="1px" rounded="lg" p={6}>
            <Stack>
              <Heading size="md">Content Generator</Heading>
              <Text color="gray.500">Create study notes and materials.</Text>
              <Button as={RouterLink} to="#" colorScheme="teal" isDisabled>Open (coming soon)</Button>
            </Stack>
          </GridItem>
          <GridItem borderWidth="1px" rounded="lg" p={6}>
            <Stack>
              <Heading size="md">Question Setter</Heading>
              <Text color="gray.500">Generate MCQ, T/F, short answers.</Text>
              <Button as={RouterLink} to="#" colorScheme="teal" isDisabled>Open (coming soon)</Button>
            </Stack>
          </GridItem>
          <GridItem borderWidth="1px" rounded="lg" p={6}>
            <Stack>
              <Heading size="md">Progress</Heading>
              <Text color="gray.500">See your learning analytics.</Text>
              <Button as={RouterLink} to="#" colorScheme="teal" isDisabled>Open (coming soon)</Button>
            </Stack>
          </GridItem>
        </Grid>
      </Container>
    </Box>
  )
}
