import hljs from 'highlight.js/lib/core'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import python from 'highlight.js/lib/languages/python'
import typescript from 'highlight.js/lib/languages/typescript'

export enum Language {
  Python = 'python',
  TypeScript = 'typescript',
  Shell = 'bash',
  Json = 'json',
}

hljs.registerLanguage(Language.Python, python)
hljs.registerLanguage(Language.TypeScript, typescript)
hljs.registerLanguage(Language.Shell, bash)
hljs.registerLanguage(Language.Json, json)

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

/** A highlighted block of code. The text is ours (never the visitor's) and `highlight` escapes it. */
export function CodeBlock({ code, language }: { code: string; language: Language }) {
  const html = hljs.highlight(code, { language, ignoreIllegals: true }).value
  return (
    <pre>
      <code className={`hljs language-${language}`} dangerouslySetInnerHTML={{ __html: html }} />
    </pre>
  )
}
