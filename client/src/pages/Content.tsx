import { useState, type ChangeEvent, useMemo, useRef, useEffect } from 'react'
import { Box, Button, FormControl, FormLabel, Heading, Input, Select, Stack, Textarea, useToast, SimpleGrid, Text, Icon, HStack, Divider, Badge, Wrap, WrapItem, Spacer, Flex, VStack, Progress, Collapse, InputGroup, InputLeftElement } from '@chakra-ui/react'
import PrivateLayout from '../components/PrivateLayout'
import { generateContent, getErrorMessage, getBillingStatus } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { MdAutoAwesome, MdArrowForward, MdDownload, MdFiberManualRecord, MdRadioButtonChecked, MdExpandMore, MdChevronRight, MdSearch } from 'react-icons/md'
import Markdown from '../components/Markdown'

export default function ContentPage() {
  const { plan, refreshBilling } = useAuth()
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
  const contentRef = useRef<HTMLDivElement | null>(null)
  const [activeId, setActiveId] = useState<string>('')
  const [progress, setProgress] = useState<number>(0)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())
  const [tocQuery, setTocQuery] = useState<string>('')
  const [usageCount, setUsageCount] = useState<number>(0)
  const FREE_LIMIT = 10

  const headings = useMemo(() => {
    if (!content) return [] as Array<{ id: string; text: string; level: number }>
    const lines = content.split(/\r?\n/)
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
  }, [content])

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

  // Filtered tree by search query; includes matching nodes and their ancestors
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
    // Expand top-level sections
    for (const n of headingTree) next.add(n.id)
    // Expand active path
    activePathIds.forEach(id => next.add(id))
    setExpandedIds(next)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [headingTree, activePathIds])

  // Load billing usage for free plan
  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        // Ensure latest plan/usage
        await refreshBilling()
        const b = await getBillingStatus()
        const count = Number((b.usage as any)?.content?.count ?? 0)
        if (!cancelled) setUsageCount(Number.isFinite(count) ? count : 0)
      } catch {}
    }
    load()
    return () => { cancelled = true }
  }, [refreshBilling])

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
                <Icon as={isExpanded ? MdExpandMore : MdChevronRight} color="gray.500" />
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
            color={isActive ? 'white' : 'gray.800'}
            borderLeftWidth="3px"
            borderLeftColor={isActive ? 'purple.500' : 'gray.200'}
            borderRadius="md"
            leftIcon={<Icon as={isActive ? MdRadioButtonChecked : MdFiberManualRecord} color={isActive ? 'white' : 'gray.400'} boxSize={2.5} />}
            _hover={{ bg: isActive ? 'purple.600' : 'purple.100', borderLeftColor: 'purple.400' }}
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
      win.document.write(`<!doctype html><html><head><title>${topic || 'Content'}</title>`)
      win.document.write('<style>body{font-family:Inter,Segoe UI,Roboto,sans-serif;padding:32px;line-height:1.8;color:#1f2937} h1,h2,h3{color:#111827} .markdown-body pre{background:#111827;color:#f3f4f6;padding:12px;border-radius:8px} .markdown-body code{background:#f3f4f6;padding:2px 6px;border-radius:4px}</style>')
      win.document.write('</head><body>')
      win.document.write(`<h1 style="margin-top:0">${topic || 'Study Content'}</h1>`)
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

  // Track which heading is currently in view
  useEffect(() => {
    if (!contentRef.current) return
    const container = contentRef.current
    const headingEls = Array.from(container.querySelectorAll('h1, h2, h3, h4, h5, h6')) as HTMLElement[]
    if (headingEls.length === 0) return

    const observer = new IntersectionObserver(
      (entries) => {
        // Pick the most visible entry
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)
        if (visible[0]) {
          const id = visible[0].target.getAttribute('id') || ''
          if (id) setActiveId(id)
        } else {
          // Fallback: find the first heading above the viewport
          let current = activeId
          for (const el of headingEls) {
            const rect = el.getBoundingClientRect()
            if (rect.top >= 80) break
            current = el.id || current
          }
          if (current) setActiveId(current)
        }
      },
      {
        root: null,
        rootMargin: '-80px 0px -60% 0px',
        threshold: [0, 0.2, 0.4, 0.6, 0.8, 1]
      }
    )

    headingEls.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [contentRef.current, content])

  // Reading progress for generated content box
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
  }, [contentRef.current, content])

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
      // Optimistically bump local usage if on free plan
      if (plan === 'free') {
        setUsageCount((c) => c + 1)
      }
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
            <HStack>
              <Heading size="md" color="gray.800">Generation Settings</Heading>
              <Spacer />
              {plan === 'free' && (
                <HStack spacing={3}>
                  <Badge colorScheme={usageCount >= FREE_LIMIT ? 'red' : 'purple'} variant="subtle">
                    Free quota: {Math.min(usageCount, FREE_LIMIT)} / {FREE_LIMIT}
                  </Badge>
                </HStack>
              )}
              {!!topic && (
                <Wrap>
                  <WrapItem><Badge colorScheme="purple" variant="subtle">{subject}</Badge></WrapItem>
                  <WrapItem><Badge colorScheme="blue" variant="subtle">{difficulty}</Badge></WrapItem>
                  <WrapItem><Badge colorScheme="green" variant="subtle">{contentType}</Badge></WrapItem>
                </Wrap>
              )}
            </HStack>
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
          <Flex gap={6} align="flex-start">
            <Box flex="1 1 0%">
              <Box
                bg="white"
                borderRadius="16px"
                borderWidth="1px"
                borderColor="gray.200"
                boxShadow="0 2px 8px rgba(0, 0, 0, 0.06)"
                overflow="hidden"
              >
                <Box bg="purple.50" px={8} py={4}>
                  <HStack justify="space-between" align="center">
                    <Box>
                      <Heading size="lg" color="purple.700">Generated Study Material</Heading>
                      <Text color="purple.600">Ready for your review</Text>
                    </Box>
                    <HStack>
                      <Wrap>
                        <WrapItem><Badge colorScheme="purple" variant="solid">{subject}</Badge></WrapItem>
                        <WrapItem><Badge colorScheme="blue" variant="solid">{difficulty}</Badge></WrapItem>
                        <WrapItem><Badge colorScheme="green" variant="solid">{contentType}</Badge></WrapItem>
                      </Wrap>
                      <Button leftIcon={<Icon as={MdDownload} />} variant="outline" onClick={onDownloadPdf}>Download PDF</Button>
                    </HStack>
                  </HStack>
                </Box>
                
                <Progress value={progress} size="xs" colorScheme="purple" borderTopRadius="0" borderBottomRadius="0" />
                <Box ref={contentRef} p={12} maxW="5xl" mx="auto" lineHeight="tall" maxH="80vh" overflowY="auto">
                  <Markdown source={content} />
                </Box>

                <Divider />
                
                <Box p={8} maxW="3xl" mx="auto">
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
                      onClick={() => navigate(`/content/view?id=${encodeURIComponent(contentId)}`)}
                      variant="outline"
                      borderRadius="10px"
                      borderColor="gray.300"
                      _hover={{ bg: 'gray.50' }}
                    >
                      View Full Page
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
            </Box>
            <VStack as="aside" minW={{ base: '0', md: '220px' }} ml="auto" display={{ base: 'none', md: 'flex' }} position="sticky" top="92px" align="stretch">
              <Box borderWidth="1px" rounded="lg" p={0} bg="gray.50" borderColor="gray.200" boxShadow="md" overflow="hidden">
                <Box px={4} py={3} bg="white" borderBottomWidth="1px" position="sticky" top={0} zIndex={1}>
                  <HStack justify="space-between" align="center" mb={2}>
                    <Text fontWeight="700" color="gray.800">On this page</Text>
                    <HStack>
                      <Button size="xs" variant="ghost" onClick={() => {
                        // Expand all nodes
                        setExpandedIds(new Set(headings.map(h => h.id)))
                      }}>Expand all</Button>
                      <Button size="xs" variant="ghost" onClick={() => {
                        // Collapse to top-level only
                        setExpandedIds(new Set(headingTree.map(n => n.id)))
                      }}>Collapse all</Button>
                      <Badge colorScheme="purple" variant="subtle">{headings.length}</Badge>
                    </HStack>
                  </HStack>
                  <InputGroup size="sm">
                    <InputLeftElement pointerEvents="none">
                      <Icon as={MdSearch} color="gray.400" />
                    </InputLeftElement>
                    <Input
                      value={tocQuery}
                      onChange={(e) => setTocQuery(e.target.value)}
                      placeholder="Filter sections"
                      bg="gray.50"
                      _focus={{ bg: 'white', borderColor: 'purple.300', boxShadow: '0 0 0 1px var(--chakra-colors-purple-300)' }}
                    />
                  </InputGroup>
                </Box>
                <VStack align="stretch" spacing={0.5} maxH="70vh" overflowY="auto" px={2} py={2}>
                  {headings.length === 0 && <Text color="gray.500">No sections</Text>}
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
      </Stack>
    </PrivateLayout>
  )
}
