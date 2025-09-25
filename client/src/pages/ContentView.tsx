import { Box, Button, Container, Heading, Stack, Text } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { useEffect, useState } from 'react'
import { getContentById, type ContentOut } from '../api/client'
import { useLocation, useNavigate } from 'react-router-dom'

function useQuery() {
  const { search } = useLocation()
  return new URLSearchParams(search)
}

export default function ContentViewPage() {
  const query = useQuery()
  const id = query.get('id') || ''
  const [data, setData] = useState<ContentOut | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    let cancelled = false
    if (!id) { setLoading(false); return }
    getContentById(id)
      .then((d) => { if (!cancelled) setData(d) })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id])

  return (
    <PrivateLayout>
      <Container maxW="5xl" py={2}>
        {loading && <Text>Loading content...</Text>}
        {!loading && !data && <Text>Content not found.</Text>}
        {data && (
          <Box>
            <Heading mb={4}>{data.topic || 'Study Content'}</Heading>
            <Box borderWidth="1px" rounded="md" p={4}>
              <div dangerouslySetInnerHTML={{ __html: data.content }} />
            </Box>
            <Stack direction={{ base: 'column', md: 'row' }} mt={6}>
              <Button onClick={() => navigate(`/questions?content_id=${encodeURIComponent(data.id)}`)} colorScheme="purple">Create Questions</Button>
              <Button onClick={() => navigate('/progress')} variant="outline">Back to Progress</Button>
            </Stack>
          </Box>
        )}
      </Container>
    </PrivateLayout>
  )
}
