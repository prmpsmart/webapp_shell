import { useState } from 'react'
import backendCode from '../../docs_backend/save_note.py?raw'
import shellCode from '../../app.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { chooseAndSave } from '../demos/saveAs'
import { saveInBrowser } from '../browserNative'
import frontendCode from '../demos/saveAs.ts?raw'

const SNIPPETS = codeFor(
  ['src/demos/saveAs.ts', frontendCode],
  ['docs_backend/save_note.py', backendCode],
  ['app.py', shellCode],
)

function Saver() {
  const [text, setText] = useState('Written by the backend, to a path the shell chose.')
  return (
    <Demo
      inBrowser={(show) => (
        <>
          <textarea value={text} onChange={(event) => setText(event.target.value)} rows={3} />
          <button
            className="primary"
            onClick={async () => {
              show('')
              try {
                const saved = await saveInBrowser('note.txt', text)
                show(
                  saved
                    ? `Saved ${saved.bytes} bytes as ${saved.name}: ${saved.method}. The page never learns the folder.`
                    : 'Nothing chosen.',
                )
              } catch (error) {
                show(messageOf(error))
              }
            }}
          >
            Save as…
          </button>
        </>
      )}
    >
      {(bridge, show) => (
        <>
          <textarea value={text} onChange={(event) => setText(event.target.value)} rows={3} />
          <button
            className="primary"
            onClick={async () => {
              show('')
              try {
                const saved = await chooseAndSave(bridge, text)
                show(saved ? `Saved ${saved.bytes} bytes to ${saved.path}` : 'Nothing chosen.')
              } catch (error) {
                show(messageOf(error))
              }
            }}
          >
            Save as…
          </button>
        </>
      )}
    </Demo>
  )
}

export function SaveAs() {
  return (
    <FeaturePage
      title="Save as"
      lead="The shell asks where to save; the backend writes the file."
      usesBackend
      demo={<Saver />}
      snippets={SNIPPETS}
    >
      <p>
        <code>bridge.saveAs(defaultName)</code> returns the path the user chose, or <code>null</code> if they
        cancelled. Keeping the writing in the backend keeps the shell free of your program's logic.
      </p>
    </FeaturePage>
  )
}
