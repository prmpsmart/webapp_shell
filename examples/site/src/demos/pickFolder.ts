import type { Bridge } from '../bridge/webapp-shell-bridge.js'

export interface FolderInfo {
  count: number
  first: string[]
}

/** The shell chooses the folder; the backend, which can read the disk, tells the page what is inside. */
export async function chooseAndList(bridge: Bridge): Promise<FolderInfo | null> {
  const path = await bridge.pickFolder()
  if (!path) return null
  const answer = await fetch('/api/folder?path=' + encodeURIComponent(path))
  if (!answer.ok) throw new Error((await answer.json()).error)
  return answer.json()
}
