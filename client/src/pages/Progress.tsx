import { Box, Container, Heading, SimpleGrid, Stat, StatHelpText, StatLabel, StatNumber } from '@chakra-ui/react'
import Navbar from '../components/Navbar'
import { useEffect, useState } from 'react'
import { getMyProgress, ProgressOut } from '../api/client'

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
      </Container>
    </Box>
  )
}
