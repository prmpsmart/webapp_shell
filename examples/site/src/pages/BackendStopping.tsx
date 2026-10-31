import { useState } from 'react'
import backendCode from '../../docs_backend/crash.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { crashAndWait } from '../demos/stopping'
import frontendCode from '../demos/stopping.ts?raw'
import watchdogCode from '../../../../src/webapp_shell/watchdog.py?raw'

const SNIPPETS = codeFor(
  ['src/demos/stopping.ts', frontendCode],
  ['docs_backend/crash.py', backendCode],
  ['webapp_shell/watchdog.py (the library)', watchdogCode],
)

function Crasher() {
  const [state, setState] = useState('')
  return (
    <Demo needsShell={false}>
      {(_bridge, show) => (
        <>
          <button
            className="primary"
            onClick={async () => {
              show('')
              try {
                await crashAndWait((up) => setState(up ? 'backend up' : 'backend down…'))
                show('The backend stopped and the shell started it again, on the same address and token.')
              } catch (error) {
                show(messageOf(error))
              }
              setState('')
            }}
          >
            Stop the backend
          </button>
          {state && <output>{state}</output>}
        </>
      )}
    </Demo>
  )
}

export function BackendStopping() {
  return (
    <FeaturePage
      title="When the backend stops"
      lead="The shell notices and starts the backend again; the page does not have to do anything."
      usesBackend={false}
      demo={<Crasher />}
      snippets={SNIPPETS}
    >
      <p>
        The watchdog looks once a second. A dead backend is started again on the same address and with the
        same token, so the open page reconnects by itself. After three restarts within two minutes it gives up
        and the shell shows a message that names your program. In a plain browser there is no shell to restart
        it, so this demonstration only works here.
      </p>
      <p>
        The button above really ends the backend's process. Pressing it more than three times within two
        minutes shows the give-up message, which is the point of the limit.
      </p>
    </FeaturePage>
  )
}
