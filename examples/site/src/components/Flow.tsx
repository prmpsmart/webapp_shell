export interface FlowStep {
  title: string
  note: string
  /** What travels from this step to the next one. */
  carries?: string
}

interface Props {
  steps: FlowStep[]
  label: string
}

/** A route drawn as boxes and arrows: who does what, and what travels between them. */
export function Flow({ steps, label }: Props) {
  return (
    <div className="flow" aria-label={label}>
      {steps.map((step, index) => (
        <FlowBox key={step.title + index} step={step} last={index === steps.length - 1} />
      ))}
    </div>
  )
}

function FlowBox({ step, last }: { step: FlowStep; last: boolean }) {
  return (
    <>
      <div>
        <b>{step.title}</b>
        <span>{step.note}</span>
      </div>
      {last ? null : <i>{step.carries ? `→ ${step.carries} →` : '→'}</i>}
    </>
  )
}

/** The route of a native feature (design doc, section 8): the page talks to the shell, then to the backend. */
export const NATIVE_PATH_FLOW: FlowStep[] = [
  { title: 'page', note: 'calls the bridge' },
  { title: 'shell', note: 'native dialog', carries: 'path' },
  { title: 'page', note: 'sends the path' },
  { title: 'backend', note: 'ordinary request data' },
]
