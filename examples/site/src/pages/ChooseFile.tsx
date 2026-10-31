import { useState } from 'react'
import { useBridge } from '../bridgeContext'
import { CodeTabs, Layer } from '../components/CodeTabs'
import { Flow } from '../components/Flow'
import { chooseAndDescribe, type FileInfo } from '../demos/pickFile'
import frontendCode from '../demos/pickFile.ts?raw'
import backendCode from '../../docs_backend/describe.py?raw'
import shellCode from '../../app.py?raw'

const SNIPPETS = [
  { layer: Layer.Frontend, file: 'src/demos/pickFile.ts', code: frontendCode },
  { layer: Layer.Backend, file: 'docs_backend/describe.py', code: backendCode },
  { layer: Layer.Shell, file: 'app.py', code: shellCode },
]

function Demo() {
  const bridge = useBridge()
  const [info, setInfo] = useState<FileInfo | null>(null)
  const [message, setMessage] = useState('')

  async function choose() {
    if (!bridge) return
    setMessage('')
    try {
      const chosen = await chooseAndDescribe(bridge)
      setInfo(chosen)
      if (!chosen) setMessage('Nothing chosen.')
    } catch (error) {
      setInfo(null)
      setMessage(error instanceof Error ? error.message : String(error))
    }
  }

  if (!bridge) return <p className="demo-note">Waiting for the shell…</p>
  if (!bridge.canPickPaths)
    return (
      <p className="demo-note">A plain browser cannot hand a page a real path. Run this site in the shell.</p>
    )
  return (
    <div className="demo">
      <button className="primary" onClick={choose}>
        Choose a file…
      </button>
      {info && (
        <output>
          <b>{info.name}</b> · {info.bytes.toLocaleString()} bytes (measured by the backend)
        </output>
      )}
      {message && <output>{message}</output>}
    </div>
  )
}

export function ChooseFile() {
  return (
    <>
      <h1>Choose a file</h1>
      <p className="lead">
        A browser hides the path of a file the user picks. The shell can open the system dialog and give the
        page the real path.
      </p>
      <Flow />
      <p>
        The page asks the shell with <code>bridge.pickFile()</code>. The backend never talks to the shell: the
        page passes the chosen path to it as ordinary request data.
      </p>
      <h2>Try it</h2>
      <Demo />
      <h2>The code</h2>
      <CodeTabs snippets={SNIPPETS} />
      <p>
        The shell tab is the whole launcher: the standard native functions are on by default, so there is
        nothing to enable.
      </p>
    </>
  )
}
