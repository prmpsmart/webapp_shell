import type { Bridge } from '../bridge/webapp-shell-bridge.js'

/** A link inside the window would navigate the app away; the shell opens it in the user's own browser instead. */
export const openInBrowser = (bridge: Bridge, url: string): Promise<boolean> => bridge.openUrl(url)
