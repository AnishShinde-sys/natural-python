import { useState, useEffect } from 'react'
import { EditorView } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
import { basicSetup } from 'codemirror'

export default function NaturalPythonIDE() {
  const [code, setCode] = useState(`# Hi Johan!
# Welcome to Natural Python IDE
# Type your commands here in natural language
# Example: Make a number called x equal to 10

`)

  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)

  useEffect(() => {
    const state = EditorState.create({
      doc: code,
      extensions: [
        basicSetup,
        python(),
        EditorView.updateListener.of((v) => {
          if (v.docChanged) {
            setCode(v.state.doc.toString())
          }
        }),
      ],
    })

    const view = new EditorView({
      state,
      parent: document.getElementById('editor-container') || undefined,
    })

    return () => view.destroy()
  }, [])

  return (
    <main className="min-h-screen p-4">
      <h1>Natural Python IDE</h1>
      <div id="editor-container"></div>
    </main>
  )
}
