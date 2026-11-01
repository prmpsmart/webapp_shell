import { useState } from 'react'
import shellCode from '../../app.py?raw'
import backendCode from '../../docs_backend/messages.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { Flow, type FlowStep } from '../components/Flow'
import { shellSentences, type Sentence } from '../demos/messages'
import frontendCode from '../demos/messages.ts?raw'
import messagesCode from '../../../../src/webapp_shell/messages.py?raw'

const SNIPPETS = codeFor(
  ['src/demos/messages.ts', frontendCode],
  ['docs_backend/messages.py', backendCode],
  ['webapp_shell/messages.py (the library)', messagesCode],
)

const START: FlowStep[] = [
  { title: 'shell', note: 'opens the splash page', carries: 'the backend command' },
  { title: 'backend', note: 'starts, answers its health path', carries: 'ready' },
  { title: 'shell', note: 'opens the window on the frontend' },
]

function Sentences() {
  const [sentences, setSentences] = useState<Sentence[]>([])
  return (
    <Demo needsShell={false}>
      {(_bridge, show) => (
        <>
          <button
            className="primary"
            onClick={async () => {
              show('')
              try {
                setSentences(await shellSentences())
              } catch (error) {
                show(messageOf(error))
              }
            }}
          >
            Show the shell's sentences
          </button>
          {sentences.length > 0 && (
            <table>
              <tbody>
                {sentences.map((sentence) => (
                  <tr key={sentence.key}>
                    <td>
                      <code>{sentence.key}</code>
                    </td>
                    <td>{sentence.text}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </Demo>
  )
}

export function StartUp() {
  return (
    <FeaturePage
      title="Splash and start-up checks"
      lead="What the shell shows and checks before your frontend is on screen, and what it says when that fails."
      flow={
        <Flow
          steps={START}
          label="Start-up: the shell shows the splash, starts the backend, then opens the frontend"
        />
      }
      demo={<Sentences />}
      snippets={SNIPPETS}
    >
      <h2>The splash</h2>
      <p>
        The window opens at once on a small page of the shell's own: your icon, a spinner and your{' '}
        <code>AppIdentity.boot_colors</code>, so the first thing a person sees is already your program. It
        stays at least <code>ShellConfig.splash_seconds</code> from the start (<code>--splash-seconds N</code>{' '}
        changes it for one run), and until the backend answers its health path. The shell waits for that
        answer for at most <code>ShellConfig.startup_timeout</code> seconds; after that the splash becomes the
        error page below.
      </p>
      <h2>When start-up fails</h2>
      <p>
        If the backend stops while starting, or never answers, the splash page becomes an error page with one
        sentence: the exit code of the backend, or the health path and the seconds waited, and the advice to
        start the backend by hand to read what it says. On Windows the pywebview shell also looks for the
        WebView2 runtime before any window opens, and says where to get it in a message box when it is
        missing.
      </p>
      <h2>Checking the libraries</h2>
      <p>
        <code>program --check-libraries</code> imports every name in{' '}
        <code>ShellConfig.required_libraries</code> and runs your <code>library_checks</code>, prints the
        problems and exits with 1. A build runs it on the frozen program (see the freezing guide), so a
        missing library is found by the build and not by the person using the program. It is a command, not a
        check on every launch.
      </p>
      <h2>The sentences</h2>
      <p>
        These few sentences are the only text the shell writes. A project that translates its program gives
        its own <code>ShellMessages</code> to <code>ShellConfig.messages</code>; the table above is the
        English default, read from the library by the backend of this site.{' '}
        <code>python -m webapp_shell messages</code> prints the same catalogue as JSON for a frontend's
        translation files.
      </p>
    </FeaturePage>
  )
}
