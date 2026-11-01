/**
 * What a plain browser can do in place of each native function. The shell gives the page real paths on the user's disk;
 * a browser never does (it hands over the file, or a handle with a name), so none of these answers a path.
 */

export interface PickedFile {
  name: string
  bytes: number
  /** What the browser says the path is: nothing, in every browser. Read from the `File`, not assumed. */
  path: string | null
}

export interface PickedFolder {
  name: string
  count: number
  first: string[]
  path: string | null
}

export enum SaveMethod {
  Picker = 'the browser asked where to save',
  Download = 'the browser downloaded it to its downloads folder',
}

export interface SavedFile {
  name: string
  bytes: number
  method: SaveMethod
}

const PREVIEW = 6

/** The parts of the File System Access API the demos use (TypeScript's DOM library does not include them yet). */
interface FileHandle {
  name: string
  getFile(): Promise<File>
  createWritable(): Promise<{ write(data: Blob): Promise<void>; close(): Promise<void> }>
}
interface DirectoryHandle {
  name: string
  values(): AsyncIterable<{ name: string }>
}
interface PickerWindow {
  showOpenFilePicker?: () => Promise<FileHandle[]>
  showDirectoryPicker?: () => Promise<DirectoryHandle>
  showSaveFilePicker?: (options: { suggestedName: string }) => Promise<FileHandle>
}
const pickers = (): PickerWindow => window as unknown as PickerWindow

/** The user closing a picker is not an error. */
async function unlessCancelled<T>(work: Promise<T>): Promise<T | null> {
  try {
    return await work
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') return null
    throw error
  }
}

/** The classic route: an `<input type="file">`, which every browser has. */
function chooseWithInput(directory: boolean): Promise<File[]> {
  return new Promise((resolve) => {
    const input = document.createElement('input')
    input.type = 'file'
    if (directory) input.webkitdirectory = true
    input.addEventListener('change', () => resolve([...(input.files ?? [])]))
    input.addEventListener('cancel', () => resolve([]))
    input.click()
  })
}

const pathOf = (file: File): string | null => (file as File & { path?: string }).path ?? null

export async function pickFileInBrowser(): Promise<PickedFile | null> {
  const open = pickers().showOpenFilePicker
  const file = open
    ? await unlessCancelled(open().then(([handle]) => handle.getFile()))
    : ((await chooseWithInput(false))[0] ?? null)
  return file && { name: file.name, bytes: file.size, path: pathOf(file) }
}

export async function pickFolderInBrowser(): Promise<PickedFolder | null> {
  const open = pickers().showDirectoryPicker
  if (open) {
    const handle = await unlessCancelled(open())
    if (!handle) return null
    const names: string[] = []
    for await (const entry of handle.values()) names.push(entry.name)
    return { name: handle.name, count: names.length, first: names.slice(0, PREVIEW), path: null }
  }
  const files = await chooseWithInput(true)
  if (files.length === 0) return null
  const [folder] = files[0].webkitRelativePath.split('/')
  const names = [...new Set(files.map((file) => file.webkitRelativePath.split('/')[1]))]
  return { name: folder, count: names.length, first: names.slice(0, PREVIEW), path: pathOf(files[0]) }
}

export async function saveInBrowser(suggestedName: string, text: string): Promise<SavedFile | null> {
  const blob = new Blob([text], { type: 'text/plain' })
  const open = pickers().showSaveFilePicker
  if (open) {
    const handle = await unlessCancelled(open({ suggestedName }))
    if (!handle) return null
    const writable = await handle.createWritable()
    await writable.write(blob)
    await writable.close()
    return { name: handle.name, bytes: blob.size, method: SaveMethod.Picker }
  }
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = suggestedName
  link.click()
  URL.revokeObjectURL(link.href)
  return { name: suggestedName, bytes: blob.size, method: SaveMethod.Download }
}

/** `zoom` scales the page in Chrome, Safari and Firefox 126 and later. */
export function zoomInBrowser(factor: number): void {
  document.documentElement.style.setProperty('zoom', String(factor))
}

/** The colour a browser paints its own tab strip and address bar with (on phones and in Chrome). */
export function themeColorInBrowser(colour: string): void {
  let meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]')
  if (!meta) {
    meta = document.createElement('meta')
    meta.name = 'theme-color'
    document.head.append(meta)
  }
  meta.content = colour
}

export const pathNote = (path: string | null): string =>
  path ? `path: ${path}` : 'path on disk: not given by the browser'
