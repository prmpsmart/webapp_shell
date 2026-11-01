import { useState, type ReactNode } from 'react'
import { useBridge } from '../bridgeContext'
import { BridgeKind, type Bridge } from '../bridge/webapp-shell-bridge.js'

interface Props {
  /** Needs a real path from the user (a dialog), which only a shell can give. */
  needsShell?: boolean
  /** What a plain browser does in place of the shell (its own picker, a download, …). Without it the demo says it needs the shell. */
  inBrowser?: (show: (message: string) => void) => ReactNode
  children: (bridge: Bridge, show: (message: string) => void) => ReactNode
}

const BROWSER_NOTE =
  "Plain browser: this uses the browser's own feature, which never gives a path on the disk. The shell does."

/** Waits for the shell, explains a plain browser, and keeps one line of output for the demonstration. */
export function Demo({ needsShell = true, inBrowser, children }: Props) {
  const bridge = useBridge()
  const [message, setMessage] = useState('')
  if (!bridge) return <p className="demo-note">Waiting for the shell…</p>
  if (bridge.kind === BridgeKind.Browser && inBrowser)
    return (
      <div className="demo">
        <p className="demo-note">{BROWSER_NOTE}</p>
        {inBrowser(setMessage)}
        {message && <output>{message}</output>}
      </div>
    )
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
