import { useState } from 'react'
import shellCode from '../../app.py?raw'
import { Demo, messageOf } from '../components/Demo'
import { FeaturePage, codeFor } from '../components/FeaturePage'
import { ZOOM_STEPS, applyZoom } from '../demos/zoom'
import { zoomInBrowser } from '../browserNative'
import frontendCode from '../demos/zoom.ts?raw'

const SNIPPETS = codeFor(['src/demos/zoom.ts', frontendCode], null, ['app.py', shellCode])

function Zoomer() {
  const [factor, setFactor] = useState(1)
  return (
    <Demo
      inBrowser={() => (
        <div className="row">
          {ZOOM_STEPS.map((step) => (
            <button
              key={step}
              className={step === factor ? 'primary' : ''}
              onClick={() => {
                zoomInBrowser(step)
                setFactor(step)
              }}
            >
              {Math.round(step * 100)}%
            </button>
          ))}
        </div>
      )}
    >
      {(bridge, show) =>
        bridge.canZoom ? (
          <div className="row">
            {ZOOM_STEPS.map((step) => (
              <button
                key={step}
                className={step === factor ? 'primary' : ''}
                onClick={async () => {
                  try {
                    await applyZoom(bridge, step)
                    setFactor(step)
                  } catch (error) {
                    show(messageOf(error))
                  }
                }}
              >
                {Math.round(step * 100)}%
              </button>
            ))}
          </div>
        ) : (
          <output>This shell cannot zoom the page.</output>
        )
      }
    </Demo>
  )
}

export function Zoom() {
  return (
    <FeaturePage
      title="Zoom"
      lead="Scale the whole page, as a browser does with Ctrl and +."
      snippets={SNIPPETS}
      demo={<Zoomer />}
    >
      <p>
        <code>bridge.setZoom(factor)</code> asks the shell. <code>bridge.canZoom</code> tells whether the
        window can. Remembering the factor is the app's job: keep it with the other settings, in the backend.
      </p>
    </FeaturePage>
  )
}
