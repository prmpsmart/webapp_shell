import { useState } from 'react'
import backendCode from '../../docs_backend/job.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { runJob, type JobStatus } from '../demos/job'
import frontendCode from '../demos/job.ts?raw'

const SNIPPETS = codeFor(['src/demos/job.ts', frontendCode], ['docs_backend/job.py', backendCode], null)

function Runner() {
  const [status, setStatus] = useState<JobStatus | null>(null)
  return (
    <Demo needsShell={false}>
      {(_bridge, show) => (
        <>
          <button
            className="primary"
            disabled={status?.running}
            onClick={async () => {
              show('')
              try {
                await runJob(setStatus)
                show('Done.')
              } catch (error) {
                show(messageOf(error))
              }
            }}
          >
            Start a job
          </button>
          {status && <progress value={status.done} max={status.steps} />}
        </>
      )}
    </Demo>
  )
}

export function BackendJob() {
  return (
    <FeaturePage
      title="A long task in the backend"
      lead="Real work belongs in the backend. The page starts it and shows how far it is."
      usesBackend={false}
      demo={<Runner />}
      snippets={SNIPPETS}
    >
      <p>
        The shell has nothing to do with this: it started the backend and keeps it alive, nothing more. The
        job runs in the backend's own event loop; the page asks the status. Use a WebSocket instead when you
        want the backend to push each step; the token rules are the same (see Security).
      </p>
    </FeaturePage>
  )
}
