import { useState } from 'react'
import shellCode from '../../app.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { rememberBootColors } from '../demos/bootColors'
import { themeColorInBrowser } from '../browserNative'
import frontendCode from '../demos/bootColors.ts?raw'

const SNIPPETS = codeFor(['src/demos/bootColors.ts', frontendCode], null, ['app.py', shellCode])

function Colors() {
  const [base, setBase] = useState('#0f1420')
  const [glowA, setGlowA] = useState('#1d2b4a')
  const [glowB, setGlowB] = useState('#3b4f8a')
  return (
    <Demo
      inBrowser={(show) => (
        <>
          <label>
            base <input type="color" value={base} onChange={(event) => setBase(event.target.value)} />
          </label>
          <button
            className="primary"
            onClick={() => {
              themeColorInBrowser(base)
              show(
                "Set as the page's theme colour: the browser may paint its tab strip or address bar with it.",
              )
            }}
          >
            Use this colour
          </button>
        </>
      )}
    >
      {(bridge, show) => (
        <>
          <div className="row">
            <label>
              base <input type="color" value={base} onChange={(event) => setBase(event.target.value)} />
            </label>
            <label>
              glow A <input type="color" value={glowA} onChange={(event) => setGlowA(event.target.value)} />
            </label>
            <label>
              glow B <input type="color" value={glowB} onChange={(event) => setGlowB(event.target.value)} />
            </label>
          </div>
          <button
            className="primary"
            onClick={async () => {
              try {
                await rememberBootColors(bridge, { base, glowA, glowB })
                show('Saved. The next start opens on these colours.')
              } catch (error) {
                show(messageOf(error))
              }
            }}
          >
            Use these at the next start
          </button>
        </>
      )}
    </Demo>
  )
}

export function BootColorsPage() {
  return (
    <FeaturePage
      title="Boot colours"
      lead="The colours of the opening screen, remembered so the next start does not flash white."
      snippets={SNIPPETS}
      demo={<Colors />}
    >
      <p>
        The shell paints the window and its splash before the page exists. <code>bridge.setBootColors</code>{' '}
        stores the colours the page is using now, so the next start matches the page's theme. The first start
        uses the
        <code>boot_colors</code> given to <code>AppIdentity</code>.
      </p>
    </FeaturePage>
  )
}
