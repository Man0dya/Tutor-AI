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

    // Blockquotes: one or more lines starting with ">"
    if (/^\s*>\s?/.test(line)) {
      const quoteLines: string[] = []
      while (i < lines.length && /^\s*>\s?/.test(lines[i])) {
        quoteLines.push(lines[i].replace(/^\s*>\s?/, ''))
        i += 1
      }
      const inner = convertBasicMarkdownToHtml(quoteLines.join('\n'))
      blocks.push(`<blockquote>${inner}</blockquote>`)
      continue
    }

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
    // Images ![alt](url)
    t = t.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, '<img alt="$1" src="$2" />')
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
        '& h1': { color: 'text', marginBottom: 4, marginTop: 6, fontWeight: 700, fontSize: '2xl' },
        '& h2': { color: 'text', marginBottom: 3, marginTop: 5, fontWeight: 700, fontSize: 'xl' },
        '& h3, & h4, & h5, & h6': { color: 'text', opacity: 0.9, marginBottom: 2.5, marginTop: 4, fontWeight: 600 },
        '& h1[id]::before, & h2[id]::before, & h3[id]::before, & h4[id]::before, & h5[id]::before, & h6[id]::before': {
          content: '""',
          display: 'block',
          height: '80px',
          marginTop: '-80px',
          visibility: 'hidden'
        },
        '& p': { color: 'muted', lineHeight: '1.9', marginBottom: 3, fontSize: 'md' },
        '& ul, & ol': { color: 'muted', paddingLeft: 6, marginBottom: 3 },
        '& li': { marginBottom: 1.5 },
        '& pre': { background: 'codeBg', color: 'gray.100', padding: 3, borderRadius: '8px', overflowX: 'auto', marginY: 3 },
        '& code': { background: 'codeInlineBg', borderRadius: '4px', paddingX: 1 },
        '& a': { color: 'blue.500', textDecoration: 'underline' },
        '& blockquote': {
          borderLeft: '4px solid',
          borderColor: 'purple.300',
          background: { base: 'purple.50', _dark: 'whiteAlpha.200' },
          paddingX: 4,
          paddingY: 3,
          marginY: 4,
          borderRadius: '8px',
          color: 'text'
        },
        '& img': { maxWidth: '100%', borderRadius: '8px', marginY: 3 }
      }}
    />
  )
}

const Markdown = memo(MarkdownComponent)
export default Markdown


