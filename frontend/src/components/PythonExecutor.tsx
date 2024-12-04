import { useEffect, useState } from 'react';

interface PythonExecutorProps {
  code: string;
  onResult: (result: string) => void;
}

export default function PythonExecutor({ code, onResult }: PythonExecutorProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const executePython = async (code: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to execute code');
      }

      onResult(data.output);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      onResult('Error executing code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="python-executor">
      {loading ? (
        <div>Executing code...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <div className="output-area">
          <button 
            onClick={() => executePython(code)}
            className="run-button"
            disabled={loading}
          >
            Run Code
          </button>
        </div>
      )}
    </div>
  );
} 