import { Box } from '@chakra-ui/react'
import { memo, useMemo } from 'react'

type MarkdownProps = {
  source: string
}

function escapeHtml(input: string): string {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function convertBasicMarkdownToHtml(markdown: string): string {
  // Normalize line endings
  const text = markdown.replace(/\r\n?/g, '\n').trim()

  // Quick heuristic: many models emit markdown-like text. We'll convert a useful subset.
  // 1) Protect code fences by converting them to pre blocks first
  let html = text

  // Handle fenced code blocks ```
  html = html.replace(/```([\s\S]*?)```/g, (_match, p1: string) => {
    const escaped = escapeHtml(String(p1).replace(/^\n|\n$/g, ''))
    return `<pre><code>${escaped}</code></pre>`
  })

  // Split into lines for block-level parsing
  const lines = html.split('\n')

  const blocks: string[] = []
  let i = 0
  while (i < lines.length) {
    const line = lines[i]

    // Headings
    const hMatch = /^(#{1,6})\s+(.*)$/.exec(line)
    if (hMatch) {
      const level = hMatch[1].length
      const content = hMatch[2].trim()
      const id = slugify(content)
      blocks.push(`<h${level} id="${id}">${inline(content)}</h${level}>`)
      i += 1
      continue
    }

    // Unordered list
    if (/^\s*([-*•])\s+/.test(line)) {
      const items: string[] = []
      while (i < lines.length && /^\s*([-*•])\s+/.test(lines[i])) {
        items.push(`<li>${inline(lines[i].replace(/^\s*([-*•])\s+/, ''))}</li>`) 
        i += 1
      }
      blocks.push(`<ul>${items.join('')}</ul>`) 
      continue
    }

    // Ordered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const items: string[] = []
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(`<li>${inline(lines[i].replace(/^\s*\d+\.\s+/, ''))}</li>`) 
        i += 1
      }
      blocks.push(`<ol>${items.join('')}</ol>`) 
      continue
    }

    // Horizontal rule
    if (/^\s*([-*_])\1{2,}\s*$/.test(line)) {
      blocks.push('<hr/>')
      i += 1
      continue
    }

    // Collect paragraph lines until blank
    if (line.trim().length > 0) {
      const para: string[] = []
      while (i < lines.length && lines[i].trim().length > 0) {
        para.push(lines[i])
        i += 1
      }
      const joined = para.join(' ').trim()
      blocks.push(`<p>${inline(joined)}</p>`) 
      continue
    }

    // Blank line
    i += 1
  }

  return blocks.join('\n')

  function inline(s: string): string {
    let t = s
    // Inline code `code`
    t = t.replace(/`([^`]+)`/g, (_m, p1: string) => `<code>${escapeHtml(p1)}</code>`)
    // Bold **text**
    t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Italic *text* or _text_
    t = t.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>')
    t = t.replace(/_([^_]+)_/g, '<em>$1</em>')
    // Links [text](url)
    t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    return t
  }

  function slugify(s: string): string {
    return s
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-')
  }
}

function MarkdownComponent({ source }: MarkdownProps) {
  const html = useMemo(() => convertBasicMarkdownToHtml(source || ''), [source])
  return (
    <Box
      className="markdown-body"
      dangerouslySetInnerHTML={{ __html: html }}
      sx={{
        '& h1, & h2, & h3, & h4, & h5, & h6': {
          color: 'gray.800',
          marginBottom: 3,
          marginTop: 6,
          fontWeight: 700,
          letterSpacing: '-0.02em'
        },
        '& h1': { fontSize: { base: '2xl', md: '3xl' }, borderBottom: '1px solid', borderColor: 'gray.200', paddingBottom: 2 },
        '& h2': { fontSize: { base: 'xl', md: '2xl' }, marginTop: 6 },
        '& h3': { fontSize: { base: 'lg', md: 'xl' }, marginTop: 5 },
        '& h1[id]::before, & h2[id]::before, & h3[id]::before, & h4[id]::before, & h5[id]::before, & h6[id]::before': {
          content: '""',
          display: 'block',
          height: '80px',
          marginTop: '-80px',
          visibility: 'hidden'
        },
        '& p': { color: 'gray.700', lineHeight: '1.9', marginBottom: 4, fontSize: { base: 'md', md: 'lg' } },
        '& ul, & ol': { color: 'gray.800', paddingLeft: 6, marginBottom: 4 },
        '& li': { marginBottom: 1.5 },
        '& pre': { background: 'gray.900', color: 'gray.100', padding: 4, borderRadius: '10px', overflowX: 'auto', marginY: 4, fontSize: 'sm' },
        '& code': { background: 'gray.100', borderRadius: '6px', paddingX: 2, paddingY: 0.5, fontSize: '0.95em' },
        '& a': { color: 'purple.600', textDecoration: 'underline', fontWeight: 500 },
        '& blockquote': {
          borderLeft: '4px solid',
          borderColor: 'purple.200',
          background: 'purple.50',
          color: 'gray.700',
          padding: '12px 16px',
          borderRadius: '8px',
          marginY: 4
        },
        '& hr': { borderColor: 'gray.200', marginY: 6 }
      }}
    />
  )
}

const Markdown = memo(MarkdownComponent)
export default Markdown


