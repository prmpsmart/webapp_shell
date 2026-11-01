import { useEffect, useState } from 'react'
import hljs from 'highlight.js/lib/core'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import python from 'highlight.js/lib/languages/python'
import typescript from 'highlight.js/lib/languages/typescript'

enum CopyState {
  Idle = 'Copy',
  Copied = 'Copied',
  Failed = 'Could not copy',
}

export enum Language {
  Python = 'python',
  TypeScript = 'typescript',
  Shell = 'bash',
  Json = 'json',
  /** No highlighting: a diagram or output, whose fence names no language. */
  Plain = 'text',
}

hljs.registerLanguage(Language.Python, python)
hljs.registerLanguage(Language.TypeScript, typescript)
hljs.registerLanguage(Language.Shell, bash)
hljs.registerLanguage(Language.Json, json)

/** The language of a Markdown fence (```python, ```sh); a fence without one is shown as it is. */
const BY_FENCE: Record<string, Language> = {
  python: Language.Python,
  py: Language.Python,
  typescript: Language.TypeScript,
  ts: Language.TypeScript,
  tsx: Language.TypeScript,
  js: Language.TypeScript,
  json: Language.Json,
  sh: Language.Shell,
  bash: Language.Shell,
  shell: Language.Shell,
}

export const languageOfFence = (fence: string | undefined): Language =>
  BY_FENCE[(fence ?? '').replace('language-', '')] ?? Language.Plain

const BY_EXTENSION: Record<string, Language> = {
  py: Language.Python,
  ts: Language.TypeScript,
  tsx: Language.TypeScript,
  js: Language.TypeScript,
  json: Language.Json,
  sh: Language.Shell,
}

/** The language of a file shown in a snippet, from its extension; a "(none)" tab holds Python comments. */
export function languageOf(file: string): Language {
  return BY_EXTENSION[file.split('.').pop() ?? ''] ?? Language.Python
}

const COPIED_MS = 1500

/** Puts text on the clipboard. The clipboard API needs a secure page; a window that is not one falls back to a hidden field. */
async function copyText(text: string): Promise<void> {
  if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text)
  const field = document.createElement('textarea')
  field.value = text
  field.style.position = 'fixed'
  field.style.opacity = '0'
  document.body.append(field)
  field.select()
  const copied = document.execCommand('copy')
  field.remove()
  if (!copied) throw new Error('the browser refused to copy')
}

function CopyButton({ code }: { code: string }) {
  const [state, setState] = useState(CopyState.Idle)
  useEffect(() => {
    if (state === CopyState.Idle) return
    const timer = setTimeout(() => setState(CopyState.Idle), COPIED_MS)
    return () => clearTimeout(timer)
  }, [state])
  return (
    <button
      type="button"
      className="copy"
      aria-label="Copy the code"
      onClick={() =>
        copyText(code).then(
          () => setState(CopyState.Copied),
          () => setState(CopyState.Failed),
        )
      }
    >
      {state}
    </button>
  )
}

/** A highlighted block of code, with a button that copies it. The text is ours (never the visitor's) and `highlight` escapes it. */
export function CodeBlock({ code, language }: { code: string; language: Language }) {
  const plain = language === Language.Plain
  const html = plain ? '' : hljs.highlight(code, { language, ignoreIllegals: true }).value
  return (
    <div className="code-body">
      <CopyButton code={code} />
      <pre>
        {plain ? (
          <code className="hljs">{code}</code>
        ) : (
          <code className={`hljs language-${language}`} dangerouslySetInnerHTML={{ __html: html }} />
        )}
      </pre>
    </div>
  )
}
