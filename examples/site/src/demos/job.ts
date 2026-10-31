export interface JobStatus {
  running: boolean
  done: number
  steps: number
}

/** Starts the job, then asks how far it is until it is done. Plain HTTP: the shell has no part in it. */
export async function runJob(onProgress: (status: JobStatus) => void): Promise<void> {
  const started = await fetch('/api/job', { method: 'POST' })
  if (!started.ok) throw new Error((await started.json()).error)
  for (;;) {
    const status: JobStatus = await (await fetch('/api/job')).json()
    onProgress(status)
    if (!status.running) return
    await new Promise((resolve) => setTimeout(resolve, 200))
  }
}
