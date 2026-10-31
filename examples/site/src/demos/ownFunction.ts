import type { Bridge } from '../bridge/webapp-shell-bridge.js'

export interface Place {
  system: string
  release: string
  python: string
}

/** Your own functions are called by name, like the standard ones. Arguments and results are JSON. */
export const whereAmI = (bridge: Bridge): Promise<Place> => bridge.call<Place>('whereAmI')
export const greet = (bridge: Bridge, who: string): Promise<string> => bridge.call<string>('greet', who)
