import type { ComponentType } from 'react'
import { ChooseFile } from './pages/ChooseFile'
import { GettingStarted } from './pages/GettingStarted'
import { Overview } from './pages/Overview'

export enum PageId {
  Overview = 'overview',
  GettingStarted = 'getting-started',
  ChooseFile = 'choose-file',
}

export enum Section {
  Introduction = 'Introduction',
  NativeFunctions = 'Native functions',
}

export interface Page {
  id: PageId
  title: string
  section: Section
  keywords: string
  component: ComponentType
}

export const PAGES: Page[] = [
  {
    id: PageId.Overview,
    title: 'Overview',
    section: Section.Introduction,
    keywords: 'layers frontend backend shell window',
    component: Overview,
  },
  {
    id: PageId.GettingStarted,
    title: 'Getting started',
    section: Section.Introduction,
    keywords: 'install pip launcher run config',
    component: GettingStarted,
  },
  {
    id: PageId.ChooseFile,
    title: 'Choose a file',
    section: Section.NativeFunctions,
    keywords: 'pickFile dialog path open',
    component: ChooseFile,
  },
]

export const pageFor = (hash: string): Page => PAGES.find((page) => `#/${page.id}` === hash) ?? PAGES[0]

export function search(query: string): Page[] {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean)
  return PAGES.filter((page) =>
    words.every((word) => `${page.title} ${page.keywords}`.toLowerCase().includes(word)),
  )
}
