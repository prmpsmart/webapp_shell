export function Security() {
  return (
    <>
      <h1>Security</h1>
      <p className="lead">
        The backend is a web server on the user's own computer. These are the rules that keep it theirs.
      </p>
      <h2>Who can reach the backend</h2>
      <ul>
        <li>
          <b>Loopback only.</b> The backend listens on <code>127.0.0.1</code> on a free port chosen at each
          launch. Nothing on the network can connect.
        </li>
        <li>
          <b>A token for every launch.</b> The shell makes a random token and gives it to the backend through
          an <b>environment variable</b>, not the command line (a command line is visible to other users on
          the machine). It is compared in constant time.
        </li>
        <li>
          <b>The page gets it as a cookie.</b> The launch address carries the token once; the backend turns it
          into an <code>HttpOnly</code>, <code>SameSite=Strict</code> cookie and redirects to the clean
          address. Scripts in the page cannot read it.
        </li>
        <li>
          <b>Origin check.</b> Cookies are shared by every port of a host, so another program's page on{' '}
          <code>127.0.0.1</code> could otherwise call this backend. A request that names a different origin
          than the host it calls is refused with 403.
        </li>
        <li>
          <b>Only the health path is open.</b> It tells the shell the backend is ready and says nothing else.
        </li>
        <li>
          <b>WebSockets</b> follow the same rule: <code>TokenValidator.is_valid_connection</code> checks
          header, cookie or query, and the connection is closed with code 4401 otherwise.
        </li>
      </ul>
      <h2>What the page may ask of the shell</h2>
      <p>
        The page is treated as untrusted. It can call a native function only by a <b>registered name</b>;
        anything else is refused. A handler's unexpected error never reaches the page: it gets “the native
        function failed” and the details stay in the shell's log. The standard functions validate what they
        receive: <code>openUrl</code> accepts only <code>http</code>, <code>https</code> and{' '}
        <code>mailto</code> (no <code>file:</code> or <code>javascript:</code>), and <code>reveal</code> shows
        only paths that exist. Dialogs return a path the
        <i> person</i> chose; the page cannot pick one silently.
      </p>
      <h2>What stays your job</h2>
      <ul>
        <li>
          <b>Validate paths in your backend.</b> The demonstrations on this site read and write whatever path
          the page sends, which is fine for a demonstration and not for a program. Check that a path is inside
          the folders your program works with.
        </li>
        <li>
          <b>Keep native functions few and narrow.</b> Every function you register is something the page can
          ask for.
        </li>
        <li>
          <b>Do not log the token</b>, and do not put it in an address you show.
        </li>
      </ul>
    </>
  )
}
