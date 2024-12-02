import { useState, useEffect } from 'react'
import { EditorView } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
import { basicSetup } from 'codemirror'

export default function NaturalPythonIDE() {
  const [code, setCode] = useState(`"Hi Johan my nigga"`)
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

  const runCode = async () => {
    setIsRunning(true)
    try {
      const response = await fetch('/api/run_code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      })
      const data = await response.json()
      setOutput(data.output || data.error)
    } catch (error) {
      setOutput(`Error: ${error.message}`)
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100">
      <div className="container mx-auto p-4">
        <h1 className="text-4xl font-bold text-center text-purple-600 mb-6">
          Natural Python
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Editor Section */}
          <div className="bg-white rounded-xl shadow-lg p-4">
            <h2 className="text-2xl font-semibold text-blue-600 mb-4">
              Write your code here:
            </h2>
            <div 
              id="editor-container" 
              className="border rounded-lg h-[500px] overflow-auto"
            />
          </div>

          {/* Output Section */}
          <div className="bg-white rounded-xl shadow-lg p-4">
            <h2 className="text-2xl font-semibold text-green-600 mb-4">
              See what happens:
            </h2>
            <div className="h-[500px] bg-gray-50 rounded-lg p-4 overflow-auto">
              <pre className="font-mono text-gray-700 whitespace-pre-wrap">
                {output}
              </pre>
            </div>
          </div>
        </div>

        {/* Run Button */}
        <div className="text-center mt-8">
          <button
            onClick={runCode}
            disabled={isRunning}
            className={`
              px-8 py-3 text-xl font-bold text-white rounded-full
              ${isRunning 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-green-500 hover:bg-green-600 transform hover:scale-105'}
              transition-all duration-200
            `}
          >
            {isRunning ? 'Running...' : 'Run Code!'}
          </button>
        </div>
      </div>
    </div>
  )
} 