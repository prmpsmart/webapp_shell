import shellCode from '../../app.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { openInBrowser } from '../demos/openLink'
import frontendCode from '../demos/openLink.ts?raw'

const SNIPPETS = codeFor(['src/demos/openLink.ts', frontendCode], null, ['app.py', shellCode])
const URL = 'https://github.com/prmpsmart'

export function OpenLink() {
  return (
    <FeaturePage
      title="Open a link"
      lead="Open an address in the user's own browser, not inside the app window."
      usesBackend={false}
      snippets={SNIPPETS}
      demo={
        <Demo needsShell={false}>
          {(bridge, show) => (
            <button
              className="primary"
              onClick={async () => {
                try {
                  await openInBrowser(bridge, URL)
                  show(`Opened ${URL}`)
                } catch (error) {
                  show(messageOf(error))
                }
              }}
            >
              Open {URL}
            </button>
          )}
        </Demo>
      }
    >
      <p>
        A normal link would replace the app inside its window. <code>bridge.openUrl(url)</code> hands it to
        the system, which opens the default browser.
      </p>
    </FeaturePage>
  )
}
