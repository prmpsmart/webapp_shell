/** The route of a native feature (design doc, section 8): the page talks to the shell, then to the backend. */
export function Flow() {
  return (
    <div className="flow" aria-label="how a native feature travels">
      <div>
        <b>page</b>
        <span>calls the bridge</span>
      </div>
      <i>→</i>
      <div>
        <b>shell</b>
        <span>native dialog</span>
      </div>
      <i>→ path →</i>
      <div>
        <b>page</b>
        <span>sends the path</span>
      </div>
      <i>→</i>
      <div>
        <b>backend</b>
        <span>ordinary request data</span>
      </div>
    </div>
  )
}
