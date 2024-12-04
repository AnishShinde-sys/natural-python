import { useState, useEffect } from 'react'
import { EditorView } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
import { basicSetup } from 'codemirror'

export default function NaturalPythonIDE() {
  const [code, setCode] = useState(`# Welcome to Python IDE
# Type your Python code here
# Example:
print("Hello, World!")
for i in range(5):
    print(f"Number: {i}")
`)
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const runCode = async () => {
    try {
      setIsRunning(true)
      const response = await fetch(`${API_URL}/api/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      })

      const data = await response.json()
      
      if (!response.ok) {
        setOutput(`Error: ${data.detail || 'Failed to execute code'}`)
        return
      }

      setOutput(data.output)
    } catch (err) {
      setOutput(`Error: ${err instanceof Error ? err.message : 'An error occurred'}`)
    } finally {
      setIsRunning(false)
    }
  }

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
      <h1 className="text-2xl font-bold mb-4">Python IDE</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-4">
          <div id="editor-container" className="border rounded-lg p-4 bg-white"></div>
          <button
            onClick={runCode}
            disabled={isRunning}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {isRunning ? 'Running...' : 'Run Code'}
          </button>
        </div>
        <div className="border rounded-lg p-4 bg-gray-100">
          <h2 className="text-lg font-semibold mb-2">Output:</h2>
          <pre className="whitespace-pre-wrap font-mono">{output}</pre>
        </div>
      </div>
    </main>
  )
}
