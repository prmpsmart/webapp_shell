import type { ReactNode } from 'react'
import { CodeTabs, Layer, type Snippet } from './CodeTabs'

/** The backend tab of a feature whose whole job is in the page and the shell. */
export const NO_BACKEND_CODE = `# Nothing to write here.
#
# This feature is a call from the page to the shell. The backend never
# talks to the shell, and it is not involved at all.
`

/** The shell tab of a feature the shell takes no part in. */
export const NO_SHELL_CODE = `# Nothing to write here.
#
# The shell only starts and watches the backend. This feature runs between
# the page and the backend.
`

type Source = [file: string, code: string]

export function codeFor(frontend: Source, backend: Source | null, shell: Source | null): Snippet[] {
  return [
    { layer: Layer.Frontend, file: frontend[0], code: frontend[1] },
    {
      layer: Layer.Backend,
      file: backend ? backend[0] : '(none)',
      code: backend ? backend[1] : NO_BACKEND_CODE,
    },
    { layer: Layer.Shell, file: shell ? shell[0] : '(none)', code: shell ? shell[1] : NO_SHELL_CODE },
  ]
}

interface Props {
  title: string
  lead: string
  /** The route the feature travels, as a diagram; none when it is a single call to the shell. */
  flow?: ReactNode
  demo: ReactNode
  snippets: Snippet[]
  children?: ReactNode
}

/** Every native-function page has the same shape: what it is, the route, a live demonstration, the three snippets. */
export function FeaturePage({ title, lead, flow, demo, snippets, children }: Props) {
  return (
    <>
      <h1>{title}</h1>
      <p className="lead">{lead}</p>
      {flow}
      {children}
      <h2>Try it</h2>
      {demo}
      <h2>The code</h2>
      <CodeTabs snippets={snippets} />
    </>
  )
}
