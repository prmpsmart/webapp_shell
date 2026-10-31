import type { Bridge } from '../bridge/webapp-shell-bridge.js'

export const ZOOM_STEPS = [0.8, 0.9, 1, 1.1, 1.25, 1.5]

/** The shell scales the whole page; the app remembers the factor where it keeps its own settings. */
export const applyZoom = (bridge: Bridge, factor: number): Promise<boolean> => bridge.setZoom(factor)
