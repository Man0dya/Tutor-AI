import { Box, Button, Container, Heading, Stack, Text, Flex, VStack, HStack, Divider, Icon, useToast, Badge, Wrap, WrapItem, Progress, Collapse, InputGroup, InputLeftElement, Input } from '@chakra-ui/react'
import { MdFiberManualRecord, MdRadioButtonChecked, MdExpandMore, MdChevronRight, MdSearch } from 'react-icons/md'
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
  const [progress, setProgress] = useState<number>(0)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [tocQuery, setTocQuery] = useState<string>('')

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

  type TocNode = { id: string; text: string; level: number; children: TocNode[] }

  const headingTree = useMemo(() => {
    const root: TocNode[] = []
    const stack: TocNode[] = []
    for (const h of headings) {
      const node: TocNode = { ...h, children: [] }
      while (stack.length && stack[stack.length - 1].level >= node.level) stack.pop()
      if (stack.length === 0) {
        root.push(node)
      } else {
        stack[stack.length - 1].children.push(node)
      }
      stack.push(node)
    }
    return root
  }, [headings])

  const filteredTree = useMemo(() => {
    const q = tocQuery.trim().toLowerCase()
    if (!q) return headingTree
    function filter(nodes: TocNode[]): TocNode[] {
      const out: TocNode[] = []
      for (const n of nodes) {
        const label = n.text.replace(/\*/g, '').trim().toLowerCase()
        const kids = filter(n.children)
        if (label.includes(q) || kids.length > 0) {
          out.push({ ...n, children: kids })
        }
      }
      return out
    }
    return filter(headingTree)
  }, [headingTree, tocQuery])

  const activePathIds = useMemo(() => {
    const path: string[] = []
    function dfs(nodes: TocNode[], acc: string[]): boolean {
      for (const n of nodes) {
        const next = [...acc, n.id]
        if (n.id === activeId) { path.push(...next); return true }
        if (dfs(n.children, next)) { return true }
      }
      return false
    }
    dfs(headingTree, [])
    return new Set(path)
  }, [headingTree, activeId])

  // Initialize expansion: keep top-level expanded; ensure active path expanded
  useEffect(() => {
    const next = new Set<string>([...expandedIds])
    for (const n of headingTree) next.add(n.id)
    activePathIds.forEach(id => next.add(id))
    setExpandedIds(next)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [headingTree, activePathIds])

  const toggleNode = (id: string) => {
    setExpandedIds(prev => {
      const copy = new Set(prev)
      if (copy.has(id)) copy.delete(id)
      else copy.add(id)
      return copy
    })
  }

  function renderToc(nodes: TocNode[]) {
    return nodes.map((n) => {
      const isActive = activeId === n.id
      const isExpanded = expandedIds.has(n.id)
      const label = n.text.replace(/\*/g, '').trim()
      return (
        <Box key={n.id}>
          <HStack>
            {n.children.length > 0 ? (
              <Button
                variant="ghost"
                size="xs"
                onClick={() => toggleNode(n.id)}
                aria-label={isExpanded ? 'Collapse section' : 'Expand section'}
                minW="auto"
                px={1}
              >
                <Icon as={isExpanded ? MdExpandMore : MdChevronRight} color="muted" />
              </Button>
            ) : (
              <Box w="24px" />
            )}
            <Button
            variant={isActive ? 'solid' : 'ghost'}
            colorScheme={isActive ? 'purple' : undefined}
            size="sm"
            justifyContent="flex-start"
            onClick={() => {
              const el = document.getElementById(n.id)
              if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }}
            pl={Math.min((n.level - 1) * 4, 12)}
            color={isActive ? 'white' : 'text'}
            borderLeftWidth="3px"
            borderLeftColor={isActive ? 'purple.500' : 'border'}
            borderRadius="md"
            leftIcon={<Icon as={isActive ? MdRadioButtonChecked : MdFiberManualRecord} color={isActive ? 'white' : 'muted'} boxSize={2.5} />}
            _hover={{ bg: isActive ? 'purple.600' : 'purple.100', _dark: { bg: isActive ? 'purple.500' : 'gray.700' }, borderLeftColor: 'purple.400' }}
            >
              <Text noOfLines={1}>{label}</Text>
            </Button>
          </HStack>
          <Collapse in={isExpanded} animateOpacity style={{ marginLeft: 0 }}>
            {n.children.length > 0 && (
              <Box>
                {renderToc(n.children)}
              </Box>
            )}
          </Collapse>
        </Box>
      )
    })
  }

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

  // Track active heading within content for TOC highlighting
  useEffect(() => {
    if (!contentRef.current) return
    const container = contentRef.current
    const headingEls = Array.from(container.querySelectorAll('h1, h2, h3, h4, h5, h6')) as HTMLElement[]
    if (headingEls.length === 0) return

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)
        if (visible[0]) {
          const id = visible[0].target.getAttribute('id') || ''
          if (id) setActiveId(id)
        } else {
          let current = activeId
          for (const el of headingEls) {
            const rect = el.getBoundingClientRect()
            if (rect.top >= 80) break
            current = el.id || current
          }
          if (current) setActiveId(current)
        }
      },
      { root: null, rootMargin: '-80px 0px -60% 0px', threshold: [0, 0.25, 0.5, 0.75, 1] }
    )

    headingEls.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [contentRef.current, data?.content])

  // Reading progress for full content view
  useEffect(() => {
    const el = contentRef.current
    if (!el) return
    const onScroll = () => {
      const total = el.scrollHeight - el.clientHeight
      const current = el.scrollTop
      const p = total > 0 ? Math.min(100, Math.max(0, (current / total) * 100)) : 0
      setProgress(p)
    }
    el.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => el.removeEventListener('scroll', onScroll)
  }, [contentRef.current, data?.content])

  return (
    <PrivateLayout>
      <Container maxW="7xl" py={6}>
        {loading && <Text>Loading content...</Text>}
        {!loading && !data && <Text>Content not found.</Text>}
        {data && (
          <Flex gap={6} align="flex-start">
            <Box flex="1 1 0%">
              <Stack spacing={2} mb={4}>
                <HStack justify="space-between" align="center">
                  <Heading>{data.topic || 'Study Content'}</Heading>
                  <HStack>
                    <Button leftIcon={<Icon as={MdDownload} />} variant="outline" onClick={onDownloadPdf}>Download PDF</Button>
                    <Button leftIcon={<Icon as={MdOutlineArrowBack} />} onClick={() => navigate('/progress')} variant="ghost">Back</Button>
                  </HStack>
                </HStack>
                <Wrap>
                  {!!data.subject && <WrapItem><Badge colorScheme="purple" variant="subtle">{data.subject}</Badge></WrapItem>}
                  {!!data.difficulty && <WrapItem><Badge colorScheme="blue" variant="subtle">{data.difficulty}</Badge></WrapItem>}
                  {!!data.contentType && <WrapItem><Badge colorScheme="green" variant="subtle">{data.contentType}</Badge></WrapItem>}
                </Wrap>
              </Stack>
              <Progress value={progress} size="xs" colorScheme="purple" borderTopRadius="md" borderBottomRadius="0" />
              <Box ref={contentRef} borderWidth="1px" rounded="lg" p={10} bg="surface" borderColor="border" maxH="80vh" overflowY="auto" maxW="5xl">
                <Markdown source={data.content} />
              </Box>
              <Stack direction={{ base: 'column', md: 'row' }} mt={6}>
                <Button onClick={() => navigate(`/questions?content_id=${encodeURIComponent(data.id)}`)} colorScheme="purple">Create Questions</Button>
              </Stack>
            </Box>
            <VStack as="aside" minW={{ base: '0', md: '220px' }} ml="auto" display={{ base: 'none', md: 'flex' }} position="sticky" top="92px" align="stretch">
              <Box borderWidth="1px" rounded="lg" p={0} bg="surface" borderColor="border" boxShadow="md" overflow="hidden">
                <Box px={4} py={3} bg="surface" borderBottomWidth="1px" borderColor="border" position="sticky" top={0} zIndex={1}>
                  <HStack justify="space-between" align="center" mb={2}>
                    <Text fontWeight="700" color="text">On this page</Text>
                    <HStack>
                      <Button size="xs" variant="ghost" onClick={() => {
                        setExpandedIds(new Set(headings.map(h => h.id)))
                      }}>Expand all</Button>
                      <Button size="xs" variant="ghost" onClick={() => {
                        setExpandedIds(new Set(headingTree.map(n => n.id)))
                      }}>Collapse all</Button>
                      <Badge colorScheme="purple" variant="subtle">{headings.length}</Badge>
                    </HStack>
                  </HStack>
                  <InputGroup size="sm">
                    <InputLeftElement pointerEvents="none">
                      <Icon as={MdSearch} color="muted" />
                    </InputLeftElement>
                    <Input
                      value={tocQuery}
                      onChange={(e) => setTocQuery(e.target.value)}
                      placeholder="Filter sections"
                      bg={{ base: 'gray.50', _dark: 'whiteAlpha.100' }}
                      _focus={{ bg: 'surface', borderColor: 'accent', boxShadow: '0 0 0 1px var(--chakra-colors-purple-300)' }}
                    />
                  </InputGroup>
                </Box>
                <VStack align="stretch" spacing={0.5} maxH="70vh" overflowY="auto" px={2} py={2}>
                  {headings.length === 0 && <Text color="muted">No sections</Text>}
                  {renderToc(filteredTree)}
                  {headings.length > 0 && (
                    <Button
                      mt={2}
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        if (contentRef.current) {
                          contentRef.current.scrollTo({ top: 0, behavior: 'smooth' })
                        } else {
                          window.scrollTo({ top: 0, behavior: 'smooth' })
                        }
                      }}
                    >
                      Back to top
                    </Button>
                  )}
                </VStack>
              </Box>
            </VStack>
          </Flex>
        )}
      </Container>
    </PrivateLayout>
  )
}
