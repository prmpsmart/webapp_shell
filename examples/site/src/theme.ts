export enum Theme {
  Light = 'light',
  Dark = 'dark',
}

const KEY = 'webapp-shell-docs-theme'

function stored(): Theme | null {
  try {
    const value = localStorage.getItem(KEY)
    return value === Theme.Light || value === Theme.Dark ? value : null
  } catch {
    return null
  }
}

export function initialTheme(): Theme {
  return stored() ?? (matchMedia('(prefers-color-scheme: dark)').matches ? Theme.Dark : Theme.Light)
}

export function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme
  try {
    localStorage.setItem(KEY, theme)
  } catch {
    /* private window: the choice just is not remembered */
  }
}
