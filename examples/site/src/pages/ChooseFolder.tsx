import { useState } from 'react'
import backendCode from '../../docs_backend/list_folder.py?raw'
import shellCode from '../../app.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { chooseAndList, type FolderInfo } from '../demos/pickFolder'
import { pathNote, pickFolderInBrowser, type PickedFolder } from '../browserNative'
import frontendCode from '../demos/pickFolder.ts?raw'

const SNIPPETS = codeFor(
  ['src/demos/pickFolder.ts', frontendCode],
  ['docs_backend/list_folder.py', backendCode],
  ['app.py', shellCode],
)

function BrowserChooser({ show }: { show: (message: string) => void }) {
  const [folder, setFolder] = useState<PickedFolder | null>(null)
  return (
    <>
      <button
        className="primary"
        onClick={async () => {
          show('')
          try {
            const chosen = await pickFolderInBrowser()
            setFolder(chosen)
            if (!chosen) show('Nothing chosen.')
          } catch (error) {
            setFolder(null)
            show(messageOf(error))
          }
        }}
      >
        Choose a folder…
      </button>
      {folder && (
        <output>
          <b>{folder.name}</b> · {folder.count} entries (listed by the page): {folder.first.join(', ')}
          {folder.count > folder.first.length ? ', …' : ''} · {pathNote(folder.path)}
        </output>
      )}
    </>
  )
}

function Chooser() {
  const [info, setInfo] = useState<FolderInfo | null>(null)
  return (
    <Demo inBrowser={(show) => <BrowserChooser show={show} />}>
      {(bridge, show) => (
        <>
          <button
            className="primary"
            onClick={async () => {
              show('')
              try {
                const chosen = await chooseAndList(bridge)
                setInfo(chosen)
                if (!chosen) show('Nothing chosen.')
              } catch (error) {
                setInfo(null)
                show(messageOf(error))
              }
            }}
          >
            Choose a folder…
          </button>
          {info && (
            <output>
              {info.count} entries (counted by the backend): {info.first.join(', ')}
              {info.count > info.first.length ? ', …' : ''}
            </output>
          )}
        </>
      )}
    </Demo>
  )
}

export function ChooseFolder() {
  return (
    <FeaturePage
      title="Choose a folder"
      lead="The same route as a file: the shell opens the dialog, the page passes the path on."
      usesBackend
      demo={<Chooser />}
      snippets={SNIPPETS}
    >
      <p>
        <code>bridge.pickFolder(start)</code> opens at <code>start</code>, or at the nearest folder that
        exists, so a field that already holds a path can reopen where the person left off.
      </p>
    </FeaturePage>
  )
}
