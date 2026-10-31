export interface Reply {
  status: number
  body: unknown
}

async function read(path: string, init?: RequestInit): Promise<Reply> {
  const answer = await fetch(path, init)
  return { status: answer.status, body: await answer.json() }
}

/** The health path answers anyone: the shell uses it to know the backend is up. */
export const health = (): Promise<Reply> => read('/api/health')

/** Same-origin requests carry the launch token (a cookie the shell planted), so this one is allowed. */
export const versionWithToken = (): Promise<Reply> => read('/api/version')

/** Leaving the cookie out is what any other program on this computer would do: it gets 401. */
export const versionWithoutToken = (): Promise<Reply> => read('/api/version', { credentials: 'omit' })
