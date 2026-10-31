import { useEffect, useMemo, useRef, useState } from 'react'
import { BridgeProvider } from './bridgeContext'
import { PAGES, Section, pageFor, search } from './pages'
import { Theme, applyTheme, initialTheme } from './theme'

function useHash(): string {
  const [hash, setHash] = useState(location.hash)
  useEffect(() => {
    const listener = () => setHash(location.hash)
    addEventListener('hashchange', listener)
    return () => removeEventListener('hashchange', listener)
  }, [])
  return hash
}

export function App() {
  const hash = useHash()
  const page = pageFor(hash)
  const [theme, setTheme] = useState(initialTheme)
  const [query, setQuery] = useState('')
  const searchBox = useRef<HTMLInputElement>(null)
  const shown = useMemo(() => search(query), [query])

  useEffect(() => applyTheme(theme), [theme])
  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        searchBox.current?.focus()
      }
    }
    addEventListener('keydown', listener)
    return () => removeEventListener('keydown', listener)
  }, [])
  useEffect(() => {
    document.title = `${page.title} · webapp_shell`
  }, [page])

  const Content = page.component
  return (
    <BridgeProvider>
      <aside className="side">
        <div className="brand">webapp_shell</div>
        <input
          ref={searchBox}
          className="search"
          type="search"
          placeholder="Search  (Ctrl/⌘ K)"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <nav>
          {Object.values(Section).map((section) => {
            const pages = shown.filter((item) => item.section === section)
            if (!pages.length) return null
            return (
              <div key={section}>
                <h3>{section}</h3>
                {pages.map((item) => (
                  <a key={item.id} href={`#/${item.id}`} className={item.id === page.id ? 'on' : ''}>
                    {item.title}
                  </a>
                ))}
              </div>
            )
          })}
          {!shown.length && <p className="none">Nothing matches “{query}”.</p>}
        </nav>
        <button className="theme" onClick={() => setTheme(theme === Theme.Dark ? Theme.Light : Theme.Dark)}>
          {theme === Theme.Dark ? 'Light' : 'Dark'} theme
        </button>
      </aside>
      <main className="main">
        <article>
          <Content />
        </article>
        <footer>
          {PAGES.length} pages · MIT · by Miracle Apata (<a href="https://github.com/prmpsmart">prmpsmart</a>)
        </footer>
      </main>
    </BridgeProvider>
  )
}
