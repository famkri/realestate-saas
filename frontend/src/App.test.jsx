import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders login form when not authenticated', () => {
    render(<App />)
    expect(screen.getByText('Login')).toBeInTheDocument()
  })
})
