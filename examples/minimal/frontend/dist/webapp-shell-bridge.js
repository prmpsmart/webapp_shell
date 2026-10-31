/**
 * webapp-shell bridge: how a page calls the native functions of its desktop shell.
 *
 *   import { getBridge } from './webapp-shell-bridge.js'
 *   const bridge = await getBridge({ nativeGlobal: 'acmeNative' })
 *   const path = await bridge.pickFile([{ name: 'Excel', extensions: ['xlsx'] }])
 *
 * One file, no dependencies. Copy it into the frontend with `python -m webapp_shell bridge --out src/`.
 */

/** The standard native functions, by their names on the wire (a test keeps this list equal to the Python one). */
export const STANDARD_METHODS = [
  'pickFolder',
  'pickFile',
  'saveAs',
  'reveal',
  'openUrl',
  'setBootColors',
  'setZoom',
]

export const BridgeKind = Object.freeze({ Qt: 'qt', Pywebview: 'pywebview', Browser: 'browser' })

const DEFAULT_WAIT_MS = 1500

/** An error answered by the shell (`{ ok: false, error }`). */
export class NativeCallError extends Error {}

/** Runs one call on a shell's raw api object and unwraps the envelope. */
async function callApi(api, name, args) {
  if (typeof api[name] !== 'function') throw new NativeCallError(`the shell has no native function "${name}"`)
  const answer = await api[name](...args)
  if (!answer || typeof answer !== 'object' || !('ok' in answer)) return answer
  if (!answer.ok) throw new NativeCallError(answer.error)
  return answer.value
}

const pathOrNull = (value) => (value ? value : null)

class Bridge {
  /**
   * @param kind one of BridgeKind
   * @param api the shell's raw object, or null in a plain browser
   * @param fallbacks functions used instead of a missing shell, by name
   */
  constructor(kind, api, fallbacks = {}) {
    this.kind = kind
    this.canPickPaths = kind !== BridgeKind.Browser
    this.canZoom = kind !== BridgeKind.Browser
    this._api = api
    this._fallbacks = fallbacks
  }

  /** Calls any native function, standard or the project's own. */
  call(name, ...args) {
    if (this._api) return callApi(this._api, name, args)
    const fallback = this._fallbacks[name]
    if (fallback) return Promise.resolve(fallback(...args))
    return Promise.reject(new NativeCallError(`"${name}" is not available in a plain browser`))
  }

  pickFolder(start = '') {
    return this.call('pickFolder', start).then(pathOrNull)
  }
  pickFile(filters = [], start = '') {
    return this.call('pickFile', filters, start).then(pathOrNull)
  }
  saveAs(defaultName = '', start = '') {
    return this.call('saveAs', defaultName, start).then(pathOrNull)
  }
  reveal(path) {
    return this.call('reveal', path)
  }
  openUrl(url) {
    return this.call('openUrl', url)
  }
  setBootColors(colors) {
    return this.call('setBootColors', colors)
  }
  setZoom(factor) {
    return this.call('setZoom', factor)
  }
}

/** What a plain browser does instead of the shell: nothing for paths, a new tab for links. */
const BROWSER_FALLBACKS = {
  pickFolder: async () => null,
  pickFile: async () => null,
  saveAs: async () => null,
  reveal: async () => false,
  setBootColors: async () => false,
  setZoom: async () => false,
  openUrl: async (url) => {
    window.open(url, '_blank', 'noopener')
    return true
  },
}

function found(nativeGlobal) {
  if (window[nativeGlobal]) return new Bridge(BridgeKind.Qt, window[nativeGlobal])
  if (window.pywebview && window.pywebview.api) return new Bridge(BridgeKind.Pywebview, window.pywebview.api)
  return null
}

/** The shells inject their object after the page starts, so wait for their ready events before giving up. */
function waitForShell(nativeGlobal, readyEvent, waitMs, fallbacks) {
  return new Promise((resolve) => {
    const events = ['pywebviewready', readyEvent]
    const settle = () => {
      const bridge = found(nativeGlobal)
      if (!bridge) return
      cleanup()
      resolve(bridge)
    }
    const timer = setTimeout(() => {
      cleanup()
      resolve(new Bridge(BridgeKind.Browser, null, fallbacks))
    }, waitMs)
    const cleanup = () => {
      clearTimeout(timer)
      events.forEach((event) => window.removeEventListener(event, settle))
    }
    events.forEach((event) => window.addEventListener(event, settle))
  })
}

let cached = null

/**
 * The bridge of the shell that hosts the page, resolved once and shared.
 * @param options.nativeGlobal the Qt shell's object: `<slug>Native` (the slug of the project's AppIdentity)
 * @param options.waitMs how long to wait for a shell before assuming a plain browser
 * @param options.fallbacks the project's own functions for a plain browser, by name
 */
export function getBridge({ nativeGlobal, waitMs = DEFAULT_WAIT_MS, fallbacks = {} }) {
  cached ??= Promise.resolve(
    found(nativeGlobal) ??
      waitForShell(nativeGlobal, nativeGlobal.toLowerCase() + 'ready', waitMs, { ...BROWSER_FALLBACKS, ...fallbacks }),
  )
  return cached
}

/** For tests: forget the shared bridge. */
export function resetBridge() {
  cached = null
}
