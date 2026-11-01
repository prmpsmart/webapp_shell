import { useState } from 'react'
import { CodeBlock, languageOf } from './CodeBlock'

export enum Layer {
  Frontend = 'Frontend',
  Backend = 'Backend',
  Shell = 'Shell',
}

export interface Snippet {
  layer: Layer
  file: string
  code: string
}

/** The three snippets of a feature: where each part of it lives. */
export function CodeTabs({ snippets }: { snippets: Snippet[] }) {
  const [active, setActive] = useState(0)
  const snippet = snippets[active]
  return (
    <div className="code">
      <div className="code-tabs" role="tablist">
        {snippets.map((item, index) => (
          <button
            key={item.layer}
            role="tab"
            aria-selected={index === active}
            className={index === active ? 'on' : ''}
            onClick={() => setActive(index)}
          >
            {item.layer}
          </button>
        ))}
        <span className="code-file">{snippet.file}</span>
      </div>
      <CodeBlock code={snippet.code} language={languageOf(snippet.file)} />
    </div>
  )
}
