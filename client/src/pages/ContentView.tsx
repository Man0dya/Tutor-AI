import { Box, Button, Container, Heading, Stack, Text, Flex, VStack, HStack, Divider, Icon, useToast, Tooltip } from '@chakra-ui/react'
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
  const [activeId, setActiveId] = useState<string>('')

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

  useEffect(() => {
    if (!contentRef.current) return
    const container = contentRef.current
    const headingsEls = container.querySelectorAll('h1, h2, h3, h4, h5, h6')
    if (!headingsEls.length) return

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => (a.target as HTMLElement).offsetTop - (b.target as HTMLElement).offsetTop)
        if (visible.length > 0) {
          const id = (visible[0].target as HTMLElement).id
          if (id) setActiveId(id)
        } else {
          const scrollTop = window.scrollY
          let candidate = ''
          headingsEls.forEach((el) => {
            const rectTop = (el as HTMLElement).getBoundingClientRect().top + window.scrollY
            if (rectTop - 90 <= scrollTop) candidate = (el as HTMLElement).id || candidate
          })
          if (candidate) setActiveId(candidate)
        }
      },
      { root: null, rootMargin: '0px 0px -70% 0px', threshold: 0.1 }
    )

    headingsEls.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [data?.content])

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
                  <Tooltip label="Copy all" placement="top">
                    <Button variant="outline" onClick={() => {
                      navigator.clipboard.writeText(data.content)
                        .then(() => toast({ title: 'Copied to clipboard', status: 'success', duration: 2000 }))
                        .catch(() => toast({ title: 'Copy failed', status: 'error', duration: 2000 }))
                    }}>Copy</Button>
                  </Tooltip>
                  <Button leftIcon={<Icon as={MdDownload} />} variant="outline" onClick={onDownloadPdf}>Download PDF</Button>
                  <Button leftIcon={<Icon as={MdOutlineArrowBack} />} onClick={() => navigate('/progress')} variant="ghost">Back</Button>
                </HStack>
              </HStack>
              <Box ref={contentRef} borderWidth="1px" rounded="lg" p={6} bg="white" position="relative">
                <Button size="sm" position="absolute" right="12px" bottom="12px" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>Top</Button>
                <Markdown source={data.content} />
              </Box>
              <Stack direction={{ base: 'column', md: 'row' }} mt={6}>
                <Button onClick={() => navigate(`/questions?content_id=${encodeURIComponent(data.id)}`)} colorScheme="purple">Create Questions</Button>
              </Stack>
            </Box>
            <VStack as="aside" minW={{ base: '0', md: '300px' }} display={{ base: 'none', md: 'flex' }} position="sticky" top="92px" align="stretch">
              <Box borderWidth="1px" borderColor="purple.200" rounded="lg" p={4} bg="gray.50" boxShadow="sm">
                <Text fontWeight="700" color="purple.700" mb={2}>On this page</Text>
                <Divider borderColor="purple.200" mb={3} />
                <VStack align="stretch" spacing={1} maxH="70vh" overflowY="auto">
                  {headings.length === 0 && <Text color="gray.600">No sections</Text>}
                  {headings.map(h => (
                    <Button
                      key={h.id}
                      variant="ghost"
                      justifyContent="flex-start"
                      onClick={() => {
                        const el = document.getElementById(h.id)
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      }}
                      size="sm"
                      bg="transparent"
                      _hover={{ bg: 'purple.100' }}
                      color={activeId === h.id ? 'purple.800' : 'gray.800'}
                      fontWeight={activeId === h.id ? '700' : '500'}
                      bg={activeId === h.id ? 'purple.50' : 'transparent'}
                      rounded="md"
                      pl={Math.min((h.level - 1) * 6, 16)}
                      aria-current={activeId === h.id ? 'true' : undefined}
                    >
                      <HStack>
                        <Box w="6px" h="6px" rounded="full" bg={activeId === h.id ? 'purple.600' : 'purple.400'} />
                        <Text noOfLines={1} fontSize="sm">{h.text}</Text>
                      </HStack>
                    </Button>
                  ))}
                  <Divider borderColor="purple.200" my={2} />
                  <Button size="xs" variant="outline" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>Back to top</Button>
                </VStack>
              </Box>
            </VStack>
          </Flex>
        )}
      </Container>
    </PrivateLayout>
  )
}
