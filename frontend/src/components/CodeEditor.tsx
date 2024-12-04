import { useState } from 'react';
import PythonExecutor from './PythonExecutor';

export default function CodeEditor() {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');

  return (
    <div className="code-editor">
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        className="code-input"
        placeholder="Enter Python code here..."
      />
      <PythonExecutor 
        code={code}
        onResult={(result) => setOutput(result)}
      />
      <pre className="code-output">
        {output}
      </pre>
    </div>
  );
} 