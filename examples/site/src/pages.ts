import type { ComponentType } from 'react'
import { BackendJob } from './pages/BackendJob'
import { BackendStopping } from './pages/BackendStopping'
import { BootColorsPage } from './pages/BootColors'
import { ChooseFolder } from './pages/ChooseFolder'
import { ChooseFile } from './pages/ChooseFile'
import { ForFrontend } from './pages/ForFrontend'
import { GettingStarted } from './pages/GettingStarted'
import { OpenLink } from './pages/OpenLink'
import { OwnFunction } from './pages/OwnFunction'
import { Overview } from './pages/Overview'
import { Reveal } from './pages/Reveal'
import { SaveAs } from './pages/SaveAs'
import { Security } from './pages/Security'
import { TokenAndHealth } from './pages/TokenAndHealth'
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
  ChooseFolder = 'choose-folder',
  OwnFunction = 'own-function',
  TokenAndHealth = 'token-and-health',
  BackendStopping = 'backend-stopping',
  BackendJob = 'backend-job',
  ForFrontend = 'for-frontend',
  Security = 'security',
}

export enum Section {
  Introduction = 'Introduction',
  NativeFunctions = 'Native functions',
  Contract = 'Shell and backend',
  Guides = 'Guides',
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
  {
    id: PageId.ChooseFolder,
    title: 'Choose a folder',
    section: Section.NativeFunctions,
    keywords: 'pickFolder directory dialog path',
    component: ChooseFolder,
  },
  {
    id: PageId.OwnFunction,
    title: 'Your own function',
    section: Section.NativeFunctions,
    keywords: 'NativeFunction call register custom python',
    component: OwnFunction,
  },
  {
    id: PageId.TokenAndHealth,
    title: 'Token and health',
    section: Section.Contract,
    keywords: 'token cookie header 401 health security launch',
    component: TokenAndHealth,
  },
  {
    id: PageId.BackendStopping,
    title: 'When the backend stops',
    section: Section.Contract,
    keywords: 'watchdog restart crash exit',
    component: BackendStopping,
  },
  {
    id: PageId.BackendJob,
    title: 'A long task',
    section: Section.Contract,
    keywords: 'job progress background polling websocket',
    component: BackendJob,
  },
  {
    id: PageId.ForFrontend,
    title: 'For frontend developers',
    section: Section.Guides,
    keywords: 'react vue assume cookie origin bridge browser fallback',
    component: ForFrontend,
  },
  {
    id: PageId.Security,
    title: 'Security',
    section: Section.Guides,
    keywords: 'token loopback origin cookie validate trust threat',
    component: Security,
  },
]

export const pageFor = (hash: string): Page => PAGES.find((page) => `#/${page.id}` === hash) ?? PAGES[0]

export function search(query: string): Page[] {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean)
  return PAGES.filter((page) =>
    words.every((word) => `${page.title} ${page.keywords}`.toLowerCase().includes(word)),
  )
}
