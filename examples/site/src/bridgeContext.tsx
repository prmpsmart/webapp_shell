import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { getBridge, type Bridge } from './bridge/webapp-shell-bridge.js'

/** The slug of the docs site is "docs", so its shell object is `docsNative`. */
export const NATIVE_GLOBAL = 'docsNative'

const BridgeContext = createContext<Bridge | null>(null)

export function BridgeProvider({ children }: { children: ReactNode }) {
  const [bridge, setBridge] = useState<Bridge | null>(null)
  useEffect(() => {
    void getBridge({ nativeGlobal: NATIVE_GLOBAL }).then(setBridge)
  }, [])
  return <BridgeContext.Provider value={bridge}>{children}</BridgeContext.Provider>
}

/** Null until the shell has answered (or the wait ended and the page is in a plain browser). */
export const useBridge = (): Bridge | null => useContext(BridgeContext)
