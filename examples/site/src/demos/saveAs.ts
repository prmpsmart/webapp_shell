import type { Bridge } from '../bridge/webapp-shell-bridge.js'

/** 1. the shell opens the "save as" dialog and answers the page; 2. the page sends the path and the text to the backend. */
export async function chooseAndSave(
  bridge: Bridge,
  text: string,
): Promise<{ path: string; bytes: number } | null> {
  const path = await bridge.saveAs('note.txt')
  if (!path) return null
  const answer = await fetch('/api/save', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ path, text }),
  })
  const body = await answer.json()
  if (!answer.ok) throw new Error(body.error)
  return { path, bytes: body.bytes }
}
