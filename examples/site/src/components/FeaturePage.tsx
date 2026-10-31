import type { ReactNode } from 'react'
import { CodeTabs, Layer, type Snippet } from './CodeTabs'
import { Flow } from './Flow'

/** The backend tab of a feature whose whole job is in the page and the shell. */
export const NO_BACKEND_CODE = `# Nothing to write here.
#
# This feature is a call from the page to the shell. The backend never
# talks to the shell, and it is not involved at all.
`

export function codeFor(
  frontend: [string, string],
  backend: [string, string] | null,
  shell: [string, string],
): Snippet[] {
  return [
    { layer: Layer.Frontend, file: frontend[0], code: frontend[1] },
    {
      layer: Layer.Backend,
      file: backend ? backend[0] : '(none)',
      code: backend ? backend[1] : NO_BACKEND_CODE,
    },
    { layer: Layer.Shell, file: shell[0], code: shell[1] },
  ]
}

interface Props {
  title: string
  lead: string
  usesBackend: boolean
  demo: ReactNode
  snippets: Snippet[]
  children?: ReactNode
}

/** Every native-function page has the same shape: what it is, the route, a live demonstration, the three snippets. */
export function FeaturePage({ title, lead, usesBackend, demo, snippets, children }: Props) {
  return (
    <>
      <h1>{title}</h1>
      <p className="lead">{lead}</p>
      {usesBackend ? <Flow /> : null}
      {children}
      <h2>Try it</h2>
      {demo}
      <h2>The code</h2>
      <CodeTabs snippets={snippets} />
    </>
  )
}
