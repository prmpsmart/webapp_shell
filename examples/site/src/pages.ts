import type { ComponentType } from 'react'
import { BootColorsPage } from './pages/BootColors'
import { ChooseFile } from './pages/ChooseFile'
import { GettingStarted } from './pages/GettingStarted'
import { OpenLink } from './pages/OpenLink'
import { Overview } from './pages/Overview'
import { Reveal } from './pages/Reveal'
import { SaveAs } from './pages/SaveAs'
import { Zoom } from './pages/Zoom'

export enum PageId {
  Overview = 'overview',
  GettingStarted = 'getting-started',
  ChooseFile = 'choose-file',
  SaveAs = 'save-as',
  Reveal = 'reveal',
  OpenLink = 'open-link',
  Zoom = 'zoom',
  BootColors = 'boot-colors',
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
  {
    id: PageId.SaveAs,
    title: 'Save as',
    section: Section.NativeFunctions,
    keywords: 'saveAs write file dialog',
    component: SaveAs,
  },
  {
    id: PageId.Reveal,
    title: 'Show in the file manager',
    section: Section.NativeFunctions,
    keywords: 'reveal finder explorer folder',
    component: Reveal,
  },
  {
    id: PageId.OpenLink,
    title: 'Open a link',
    section: Section.NativeFunctions,
    keywords: 'openUrl browser url',
    component: OpenLink,
  },
  {
    id: PageId.Zoom,
    title: 'Zoom',
    section: Section.NativeFunctions,
    keywords: 'setZoom scale size',
    component: Zoom,
  },
  {
    id: PageId.BootColors,
    title: 'Boot colours',
    section: Section.NativeFunctions,
    keywords: 'setBootColors splash theme flash',
    component: BootColorsPage,
  },
]

export const pageFor = (hash: string): Page => PAGES.find((page) => `#/${page.id}` === hash) ?? PAGES[0]

export function search(query: string): Page[] {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean)
  return PAGES.filter((page) =>
    words.every((word) => `${page.title} ${page.keywords}`.toLowerCase().includes(word)),
  )
}
