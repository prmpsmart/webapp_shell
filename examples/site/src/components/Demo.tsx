import { useState, type ReactNode } from 'react'
import { useBridge } from '../bridgeContext'
import type { Bridge } from '../bridge/webapp-shell-bridge.js'

interface Props {
  /** Needs a real path from the user (a dialog), which only a shell can give. */
  needsShell?: boolean
  children: (bridge: Bridge, show: (message: string) => void) => ReactNode
}

/** Waits for the shell, explains a plain browser, and keeps one line of output for the demonstration. */
export function Demo({ needsShell = true, children }: Props) {
  const bridge = useBridge()
  const [message, setMessage] = useState('')
  if (!bridge) return <p className="demo-note">Waiting for the shell…</p>
  if (needsShell && !bridge.canPickPaths)
    return (
      <p className="demo-note">A plain browser has no such native feature. Run this site in the shell.</p>
    )
  return (
    <div className="demo">
      {children(bridge, setMessage)}
      {message && <output>{message}</output>}
    </div>
  )
}

export const messageOf = (error: unknown): string => (error instanceof Error ? error.message : String(error))
