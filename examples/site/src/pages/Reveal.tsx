import shellCode from '../../app.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { chooseAndReveal } from '../demos/reveal'
import frontendCode from '../demos/reveal.ts?raw'

const SNIPPETS = codeFor(['src/demos/reveal.ts', frontendCode], null, ['app.py', shellCode])

export function Reveal() {
  return (
    <FeaturePage
      title="Show in the file manager"
      lead="Open the system file manager with a file selected: Finder, Explorer or the default manager."
      usesBackend={false}
      snippets={SNIPPETS}
      demo={
        <Demo>
          {(bridge, show) => (
            <button
              className="primary"
              onClick={async () => {
                try {
                  const path = await chooseAndReveal(bridge)
                  show(path ? `Showing ${path}` : 'Nothing chosen.')
                } catch (error) {
                  show(messageOf(error))
                }
              }}
            >
              Choose a file and show it…
            </button>
          )}
        </Demo>
      }
    >
      <p>
        <code>bridge.reveal(path)</code> is a call from the page to the shell and nothing more.
      </p>
    </FeaturePage>
  )
}
