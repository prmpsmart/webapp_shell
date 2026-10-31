import type { Bridge } from '../bridge/webapp-shell-bridge.js'

/** Pick a file, then ask the shell to show it in the system file manager. No backend is involved. */
export async function chooseAndReveal(bridge: Bridge): Promise<string | null> {
  const path = await bridge.pickFile()
  if (!path) return null
  await bridge.reveal(path)
  return path
}
