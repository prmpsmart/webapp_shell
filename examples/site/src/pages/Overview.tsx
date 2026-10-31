export function Overview() {
  return (
    <>
      <h1>webapp_shell</h1>
      <p className="lead">
        A desktop shell for web apps written in Python. You write a backend and a frontend; the library starts
        the backend, waits until it is healthy, opens a window on it and gives the page the native things a
        browser cannot do.
      </p>
      <h2>The layers</h2>
      <div className="layers">
        <div>
          <b>Frontend</b>
          <span>
            a compiled folder, <code>dist</code>
          </span>
        </div>
        <div>
          <b>Backend</b>
          <span>Python, any framework, one small contract</span>
        </div>
        <div>
          <b>Shell</b>
          <span>this library: process, window, splash, watchdog</span>
        </div>
        <div>
          <b>Window</b>
          <span>pywebview (built in) or Qt (extra)</span>
        </div>
      </div>
      <h2>This site is the demonstration</h2>
      <p>
        You are reading it inside the library's own shell. Each feature page explains one capability, has a
        button that does it for real, and shows the code it needs in the frontend, the backend and the shell.
      </p>
    </>
  )
}
