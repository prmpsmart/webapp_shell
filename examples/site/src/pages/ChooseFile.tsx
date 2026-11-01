import { useState } from 'react'
import backendCode from '../../docs_backend/describe.py?raw'
import shellCode from '../../app.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { chooseAndDescribe, type FileInfo } from '../demos/pickFile'
import frontendCode from '../demos/pickFile.ts?raw'
import { pathNote, pickFileInBrowser, type PickedFile } from '../browserNative'

const SNIPPETS = codeFor(
  ['src/demos/pickFile.ts', frontendCode],
  ['docs_backend/describe.py', backendCode],
  ['app.py', shellCode],
)

function BrowserChooser({ show }: { show: (message: string) => void }) {
  const [file, setFile] = useState<PickedFile | null>(null)
  return (
    <>
      <button
        className="primary"
        onClick={async () => {
          show('')
          try {
            const chosen = await pickFileInBrowser()
            setFile(chosen)
            if (!chosen) show('Nothing chosen.')
          } catch (error) {
            setFile(null)
            show(messageOf(error))
          }
        }}
      >
        Choose a file…
      </button>
      {file && (
        <output>
          <b>{file.name}</b> · {file.bytes.toLocaleString()} bytes (read by the page) · {pathNote(file.path)}
        </output>
      )}
    </>
  )
}

function Chooser() {
  const [info, setInfo] = useState<FileInfo | null>(null)
  return (
    <Demo inBrowser={(show) => <BrowserChooser show={show} />}>
      {(bridge, show) => (
        <>
          <button
            className="primary"
            onClick={async () => {
              show('')
              try {
                const chosen = await chooseAndDescribe(bridge)
                setInfo(chosen)
                if (!chosen) show('Nothing chosen.')
              } catch (error) {
                setInfo(null)
                show(messageOf(error))
              }
            }}
          >
            Choose a file…
          </button>
          {info && (
            <output>
              <b>{info.name}</b> · {info.bytes.toLocaleString()} bytes (measured by the backend)
            </output>
          )}
        </>
      )}
    </Demo>
  )
}

export function ChooseFile() {
  return (
    <FeaturePage
      title="Choose a file"
      lead="A browser hides the path of a file the user picks. The shell can open the system dialog and give the page the real path."
      usesBackend
      demo={<Chooser />}
      snippets={SNIPPETS}
    >
      <p>
        The page asks the shell with <code>bridge.pickFile()</code>. The backend never talks to the shell: the
        page passes the chosen path to it as ordinary request data. The shell tab is the whole launcher: the
        standard native functions are on by default, so there is nothing to enable.
      </p>
    </FeaturePage>
  )
}
