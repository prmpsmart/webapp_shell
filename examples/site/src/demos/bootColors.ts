import type { BootColors } from '../bridge/webapp-shell-bridge.js'
import type { Bridge } from '../bridge/webapp-shell-bridge.js'

/** The colours the window paints before the page has loaded, so the next start has no white flash. */
export const rememberBootColors = (bridge: Bridge, colors: BootColors): Promise<boolean> =>
  bridge.setBootColors(colors)
