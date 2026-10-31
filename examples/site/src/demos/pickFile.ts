import type { Bridge } from '../bridge/webapp-shell-bridge.js'

export interface FileInfo {
  name: string
  bytes: number
}

/** 1. the shell opens the dialog and answers the page; 2. the page gives the path to the backend. */
export async function chooseAndDescribe(bridge: Bridge): Promise<FileInfo | null> {
  const path = await bridge.pickFile()
  if (!path) return null
  const answer = await fetch('/api/describe?path=' + encodeURIComponent(path))
  if (!answer.ok) throw new Error((await answer.json()).error)
  return answer.json()
}
