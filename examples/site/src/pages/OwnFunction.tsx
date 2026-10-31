import { useState } from 'react'
import nativeCode from '../../native_functions.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { greet, whereAmI, type Place } from '../demos/ownFunction'
import frontendCode from '../demos/ownFunction.ts?raw'

const SNIPPETS = codeFor(['src/demos/ownFunction.ts', frontendCode], null, [
  'native_functions.py',
  nativeCode,
])

function Caller() {
  const [place, setPlace] = useState<Place | null>(null)
  const [who, setWho] = useState('Ada')
  return (
    <Demo needsShell={false}>
      {(bridge, show) => (
        <>
          <div className="row">
            <button
              onClick={async () => {
                try {
                  setPlace(await whereAmI(bridge))
                } catch (error) {
                  show(messageOf(error))
                }
              }}
            >
              whereAmI()
            </button>
            <input value={who} onChange={(event) => setWho(event.target.value)} />
            <button
              onClick={async () => {
                try {
                  show(await greet(bridge, who))
                } catch (error) {
                  show(messageOf(error))
                }
              }}
            >
              greet("{who}")
            </button>
          </div>
          {place && (
            <output>
              {place.system} {place.release} · Python {place.python}
            </output>
          )}
        </>
      )}
    </Demo>
  )
}

export function OwnFunction() {
  return (
    <FeaturePage
      title="Your own native function"
      lead="Add a Python function to the shell and call it from the page by name."
      usesBackend={false}
      demo={<Caller />}
      snippets={SNIPPETS}
    >
      <p>
        A handler receives the context first (the window, the shell's preferences, the OS actions) and then
        its arguments, a dataclass you declare: the page's values fill its fields in order and each is checked
        against the field's type before your code runs (a number where text is expected is refused; nothing is
        converted). It returns anything JSON can carry (<code>JsonValue</code>). To refuse a call in words the
        page may show, raise <code>NativeError</code>; any other error becomes a plain “the native function
        failed”, and the details stay in the shell's log.
      </p>
      <p>
        The names are camelCase. The page is untrusted, so a name that was not registered is refused. Register
        the function in <code>ShellConfig(native_functions=…)</code>, as the shell tab shows in{' '}
        <code>app.py</code>.
      </p>
    </FeaturePage>
  )
}
