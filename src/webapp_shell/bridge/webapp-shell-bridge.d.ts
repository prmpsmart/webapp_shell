export declare const STANDARD_METHODS: readonly string[]

export declare const BridgeKind: Readonly<{ Qt: 'qt'; Pywebview: 'pywebview'; Browser: 'browser' }>
export type BridgeKind = (typeof BridgeKind)[keyof typeof BridgeKind]

export interface FileFilter {
  name: string
  extensions: string[]
}

/** The colours of the opening screen, `#rrggbb` each. */
export interface BootColors {
  base: string
  glowA: string
  glowB: string
}

/** An error answered by the shell. */
export declare class NativeCallError extends Error {}

export interface Bridge {
  readonly kind: BridgeKind
  /** True inside a desktop shell, where the user can pick real absolute paths. */
  readonly canPickPaths: boolean
  readonly canZoom: boolean
  /** Calls any native function, standard or the project's own. Rejects with NativeCallError. */
  call<T = unknown>(name: string, ...args: unknown[]): Promise<T>
  /** `start` is the path the field holds now: the dialog opens there, or at the nearest folder that exists. */
  pickFolder(start?: string): Promise<string | null>
  pickFile(filters?: FileFilter[], start?: string): Promise<string | null>
  saveAs(defaultName?: string, start?: string): Promise<string | null>
  reveal(path: string): Promise<boolean>
  openUrl(url: string): Promise<boolean>
  setBootColors(colors: BootColors): Promise<boolean>
  setZoom(factor: number): Promise<boolean>
}

export interface BridgeOptions {
  /** The Qt shell's object on the window: `<slug>Native`. */
  nativeGlobal: string
  /** How long to wait for a shell before assuming a plain browser (default 1500). */
  waitMs?: number
  /** The project's own functions for a plain browser, by name. */
  fallbacks?: Record<string, (...args: unknown[]) => unknown>
}

export declare function getBridge(options: BridgeOptions): Promise<Bridge>
export declare function resetBridge(): void
