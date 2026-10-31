import { getBridge } from './webapp-shell-bridge.js'

const root = document.getElementById('root')
root.innerHTML = `
  <main>
    <h1>Acme Notes</h1>
    <p>Running in: <strong id="kind">…</strong></p>
    <button id="pick">Choose a file…</button>
    <output id="path"></output>
    <output id="info"></output>
  </main>`

const bridge = await getBridge({ nativeGlobal: 'acmeNative' })
document.getElementById('kind').textContent = bridge.kind

document.getElementById('pick').addEventListener('click', async () => {
  const path = await bridge.pickFile()
  document.getElementById('path').textContent = path ?? 'nothing chosen'
  if (!path) return
  // the shell gave the page the path; now the page tells the backend
  const answer = await fetch('/api/describe?path=' + encodeURIComponent(path))
  const body = await answer.json()
  document.getElementById('info').textContent = answer.ok ? `${body.name}: ${body.bytes} bytes` : body.error
})

document.title = 'Acme Notes (' + bridge.kind + ')'
