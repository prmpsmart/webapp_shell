import { CodeBlock, Language } from '../components/CodeBlock'
const USE = `// copy the bridge once:  python -m webapp_shell bridge --out src/bridge
import { getBridge } from './bridge/webapp-shell-bridge.js'

// "docs" is the slug the shell was configured with: the shell's object is "docsNative"
const bridge = await getBridge({ nativeGlobal: 'docsNative' })

if (bridge.canPickPaths) {
  const path = await bridge.pickFile()     // a real absolute path, or null if cancelled
}

// the API is the page's own origin: relative addresses, no port, no token to handle
const answer = await fetch('/api/things')`

const FALLBACKS = `// in a plain browser (a dev server, a test) your own functions need a stand-in
const bridge = await getBridge({
  nativeGlobal: 'docsNative',
  fallbacks: { whereAmI: async () => ({ system: 'Browser', release: '', python: '' }) },
})`

export function ForFrontend() {
  return (
    <>
      <h1>For frontend developers</h1>
      <p className="lead">What your page may assume, and nothing else. You need no Python to work on it.</p>
      <h2>What you can rely on</h2>
      <ul>
        <li>
          The page is served by the backend, so <b>the API is on the same origin</b>. Use relative addresses;
          you never need the port.
        </li>
        <li>
          <b>The launch token is already a cookie</b> (HttpOnly). The browser sends it with every request;
          your code neither reads nor stores it. A request made with <code>credentials: 'omit'</code> is
          refused with 401.
        </li>
        <li>
          Your build is a folder of static files (<code>frontend/dist</code>). Any framework works; use{' '}
          <code>base: './'</code> style relative asset paths so the same build runs from the backend and from
          a static host.
        </li>
        <li>
          The shell offers its native functions through <b>one object per window</b>,{' '}
          <code>&lt;slug&gt;Native</code>, announced by the event <code>&lt;slug&gt;nativeready</code>. You do
          not touch either: the bridge file does.
        </li>
      </ul>
      <h2>Using the bridge</h2>
      <CodeBlock code={USE} language={Language.TypeScript} />
      <p>
        <code>bridge.kind</code> is <code>qt</code>, <code>pywebview</code> or <code>browser</code>. Every
        function returns a promise. A shell error rejects with <code>NativeCallError</code>, whose message is
        safe to show. Results are JSON.
      </p>
      <h2>In a plain browser</h2>
      <p>
        If no shell announces itself within 1.5 seconds, <code>getBridge</code> settles on{' '}
        <code>browser</code>: dialogs answer <code>null</code>, <code>openUrl</code> opens a new tab, zoom and
        boot colours do nothing, and <code>canPickPaths</code> is false. Your own functions have no stand-in
        unless you give one:
      </p>
      <CodeBlock code={FALLBACKS} language={Language.TypeScript} />
      <h2>What you must not assume</h2>
      <ul>
        <li>A file chosen in a dialog is a path on the user's disk. Only the backend can read it.</li>
        <li>The backend address or port; they change at every launch.</li>
        <li>
          That the native object exists at start-up: always await <code>getBridge</code>.
        </li>
      </ul>
    </>
  )
}
