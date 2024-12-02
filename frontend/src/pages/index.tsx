import { useState, useEffect } from 'react'
import { EditorView } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
import { basicSetup } from 'codemirror'

export default function Home() {
  return (
    <main className="min-h-screen p-4">
      <h1>Natural Python IDE</h1>
      {/* Add your editor component here */}
    </main>
  )
}
