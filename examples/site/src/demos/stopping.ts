import { health } from './health'

/** Asks the backend to die, then watches its health path until the shell's watchdog has started it again. */
export async function crashAndWait(onTick: (up: boolean) => void): Promise<void> {
  await fetch('/api/crash', { method: 'POST' })
  let seenDown = false
  for (let attempt = 0; attempt < 60; attempt++) {
    await new Promise((resolve) => setTimeout(resolve, 500))
    const up = await health().then(
      () => true,
      () => false,
    )
    onTick(up)
    if (!up) seenDown = true
    else if (seenDown) return
  }
  throw new Error('the backend did not come back')
}
