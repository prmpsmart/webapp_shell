import { Children, isValidElement, type ReactElement, type ReactNode } from 'react'
import Markdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CodeBlock, languageOfFence } from './CodeBlock'

const REPOSITORY = 'https://github.com/prmpsmart/webapp_shell/blob/main/docs/'

/** The guides the site shows as pages, by file name: a link between two guides stays inside the site. */
export enum GuideFile {
  Contract = 'CONTRACT.md',
  Configuration = 'CONFIGURATION.md',
  NativeFunctions = 'NATIVE_FUNCTIONS.md',
  Freezing = 'FREEZING.md',
  Translating = 'TRANSLATING.md',
  Troubleshooting = 'TROUBLESHOOTING.md',
}

export const GUIDE_ROUTES: Record<GuideFile, string> = {
  [GuideFile.Contract]: '#/guide-contract',
  [GuideFile.Configuration]: '#/guide-configuration',
  [GuideFile.NativeFunctions]: '#/guide-native-functions',
  [GuideFile.Freezing]: '#/guide-freezing',
  [GuideFile.Translating]: '#/guide-translating',
  [GuideFile.Troubleshooting]: '#/guide-troubleshooting',
}

const isGuide = (name: string): name is GuideFile => name in GUIDE_ROUTES

/** Where a link of a guide goes: another guide stays in the site, another file of `docs/` is read on GitHub. */
export function resolveLink(href: string | undefined): string | undefined {
  if (!href || /^([a-z]+:|#|\/)/i.test(href)) return href
  const [file, anchor] = href.split('#')
  if (isGuide(file)) return GUIDE_ROUTES[file]
  return `${REPOSITORY}${file}${anchor ? `#${anchor}` : ''}`
}

type CodeElement = ReactElement<{ className?: string; children?: ReactNode }>

const COMPONENTS: Components = {
  pre({ children }) {
    const code = Children.toArray(children).find((child): child is CodeElement => isValidElement(child))
    const text = String(code?.props.children ?? '').replace(/\n$/, '')
    return <CodeBlock code={text} language={languageOfFence(code?.props.className)} />
  },
  a({ href, children }) {
    const target = resolveLink(href)
    const outside = target?.startsWith('http')
    return (
      <a href={target} {...(outside ? { target: '_blank', rel: 'noreferrer' } : {})}>
        {children}
      </a>
    )
  },
}

/** A Markdown guide of `docs/`, shown as a page: the same file that is read on GitHub, so the two cannot differ. */
export function Guide({ source }: { source: string }) {
  return (
    <div className="guide">
      <Markdown remarkPlugins={[remarkGfm]} components={COMPONENTS}>
        {source}
      </Markdown>
    </div>
  )
}
