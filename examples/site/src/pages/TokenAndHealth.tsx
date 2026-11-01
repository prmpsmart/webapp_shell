import backendCode from '../../docs_backend/__init__.py?raw'
import shellCode from '../../app.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { Flow, type FlowStep } from '../components/Flow'
import { health, versionWithToken, versionWithoutToken, type Reply } from '../demos/health'
import frontendCode from '../demos/health.ts?raw'

/** The token travels twice: to the backend in the environment, to the page in the launch URL. */
const HAND_OVER: FlowStep[] = [
  { title: 'shell', note: 'makes the token', carries: 'environment variable' },
  { title: 'backend', note: 'keeps it; the health path stays open' },
]
const USE: FlowStep[] = [
  { title: 'shell', note: 'opens the window', carries: 'launch URL, once' },
  { title: 'page', note: 'receives a cookie', carries: 'cookie on every call' },
  { title: 'backend', note: 'checks it, or answers 401' },
]

const SNIPPETS = codeFor(
  ['src/demos/health.ts', frontendCode],
  ['docs_backend/__init__.py', backendCode],
  ['app.py', shellCode],
)

const ASKS: [string, () => Promise<Reply>][] = [
  ['Health (open to anyone)', health],
  ['Version, with the token', versionWithToken],
  ['Version, without the token', versionWithoutToken],
]

export function TokenAndHealth() {
  return (
    <FeaturePage
      title="Token and health"
      lead="How the shell and the backend find each other, and why no other program can use your backend."
      flow={
        <>
          <Flow steps={HAND_OVER} label="how the token is handed over" />
          <Flow steps={USE} label="how the page uses it" />
        </>
      }
      snippets={SNIPPETS}
      demo={
        <Demo needsShell={false}>
          {(_bridge, show) => (
            <div className="row">
              {ASKS.map(([label, ask]) => (
                <button
                  key={label}
                  onClick={async () => {
                    try {
                      const reply = await ask()
                      show(`${label}: ${reply.status} ${JSON.stringify(reply.body)}`)
                    } catch (error) {
                      show(messageOf(error))
                    }
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </Demo>
      }
    >
      <p>
        The shell picks a free port on <code>127.0.0.1</code> and makes a random token for each launch. The
        backend reads the token from its environment and the shell hands it to the page as a cookie. The shell
        waits for the health path to answer before it shows the window. Every other path wants the token, from
        the header or the cookie.
      </p>
      <p>
        The backend tab is the whole backend of this site: <code>TokenGuard</code> is one line, and the health
        and version paths come from the <code>WireProtocol</code> both sides read.
      </p>
    </FeaturePage>
  )
}
