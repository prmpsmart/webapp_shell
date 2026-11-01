export interface Sentence {
  key: string
  text: string
}

/** The sentences the shell shows itself, from the backend (which reads the library's catalogue). */
export async function shellSentences(): Promise<Sentence[]> {
  const answer = await fetch('/api/messages')
  if (!answer.ok) throw new Error(`the backend answered ${answer.status}`)
  const catalogue: Record<string, string> = await answer.json()
  return Object.entries(catalogue).map(([key, text]) => ({ key, text }))
}
