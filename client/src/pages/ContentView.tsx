import { Box, Button, Container, Heading, Stack, Text, Flex, VStack, HStack, Divider, Icon, useToast } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { useEffect, useMemo, useRef, useState } from 'react'
import { getContentById, type ContentOut } from '../api/client'
import { useLocation, useNavigate } from 'react-router-dom'
import Markdown from '../components/Markdown'
import { MdDownload, MdOutlineArrowBack } from 'react-icons/md'

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
  const toast = useToast()
  const contentRef = useRef<HTMLDivElement | null>(null)

  const headings = useMemo(() => {
    if (!data?.content) return [] as Array<{ id: string; text: string; level: number }>
    const lines = data.content.split(/\r?\n/)
    const hs: Array<{ id: string; text: string; level: number }> = []
    for (const line of lines) {
      const m = /^(#{1,6})\s+(.*)$/.exec(line)
      if (m) {
        const level = m[1].length
        const text = m[2].trim()
        const id = text.toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim().replace(/\s+/g, '-')
        hs.push({ id, text, level })
      }
    }
    return hs
  }, [data?.content])

  const onDownloadPdf = () => {
    if (!contentRef.current) return
    try {
      const printContents = contentRef.current.innerHTML
      const win = window.open('', '_blank', 'width=1000,height=800')
      if (!win) return
      win.document.write(`<!doctype html><html><head><title>${data?.topic || 'Content'}</title>`)
      win.document.write('<style>body{font-family:Inter,Segoe UI,Roboto,sans-serif;padding:32px;line-height:1.8;color:#1f2937} h1,h2,h3{color:#111827} .markdown-body pre{background:#111827;color:#f3f4f6;padding:12px;border-radius:8px} .markdown-body code{background:#f3f4f6;padding:2px 6px;border-radius:4px}</style>')
      win.document.write('</head><body>')
      win.document.write(`<h1 style="margin-top:0">${data?.topic || 'Study Content'}</h1>`)
      win.document.write(`<div class="markdown-body">${printContents}</div>`)
      win.document.write('</body></html>')
      win.document.close()
      win.focus()
      win.print()
      win.close()
    } catch (e) {
      toast({ title: 'Download failed', status: 'error' })
    }
  }

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
      <Container maxW="7xl" py={6}>
        {loading && <Text>Loading content...</Text>}
        {!loading && !data && <Text>Content not found.</Text>}
        {data && (
          <Flex gap={8} align="flex-start">
            <Box flex="1 1 0%">
              <HStack justify="space-between" mb={4}>
                <Heading>{data.topic || 'Study Content'}</Heading>
                <HStack>
                  <Button leftIcon={<Icon as={MdDownload} />} variant="outline" onClick={onDownloadPdf}>Download PDF</Button>
                  <Button leftIcon={<Icon as={MdOutlineArrowBack} />} onClick={() => navigate('/progress')} variant="ghost">Back</Button>
                </HStack>
              </HStack>
              <Box ref={contentRef} borderWidth="1px" rounded="lg" p={6} bg="white">
                <Markdown source={data.content} />
              </Box>
              <Stack direction={{ base: 'column', md: 'row' }} mt={6}>
                <Button onClick={() => navigate(`/questions?content_id=${encodeURIComponent(data.id)}`)} colorScheme="purple">Create Questions</Button>
              </Stack>
            </Box>
            <VStack as="aside" minW={{ base: '0', md: '300px' }} display={{ base: 'none', md: 'flex' }} position="sticky" top="92px" align="stretch">
              <Box borderWidth="1px" rounded="lg" p={4} bg="white">
                <Text fontWeight="600" color="gray.700" mb={2}>On this page</Text>
                <Divider mb={3} />
                <VStack align="stretch" spacing={2} maxH="70vh" overflowY="auto">
                  {headings.length === 0 && <Text color="gray.500">No sections</Text>}
                  {headings.map(h => (
                    <Button key={h.id} variant="link" justifyContent="flex-start" onClick={() => {
                      const el = document.getElementById(h.id)
                      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
                    }} pl={Math.min((h.level - 1) * 4, 12)} colorScheme="blackAlpha">
                      <Text noOfLines={1}>{h.text}</Text>
                    </Button>
                  ))}
                </VStack>
              </Box>
            </VStack>
          </Flex>
        )}
      </Container>
    </PrivateLayout>
  )
}
