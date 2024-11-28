let editor;
document.addEventListener('DOMContentLoaded', () => {
    // Initialize CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
        extraKeys: {
            "Tab": function(cm) {
                cm.replaceSelection("    ", "end");
            }
        }
    });

    // Set initial content
    editor.setValue(`# Try these examples:
Make a number called score equal to 10
Add 5 to score
Print score
If score is bigger than 15:
    Print "High score!"`);

    // Add event listeners for file tree
    document.querySelectorAll('.file').forEach(file => {
        file.addEventListener('click', () => {
            document.querySelectorAll('.file').forEach(f => f.classList.remove('active'));
            file.classList.add('active');
        });
    });
});

function runCode() {
    const code = editor.getValue();
    const outputDiv = document.getElementById('output');

    // Add loading indicator
    outputDiv.innerHTML = '<div class="loading">Running code...</div>';
    
    fetch('/run_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code })
    })
    .then(response => response.json())
    .then(data => {
        outputDiv.innerHTML = `<pre class="output-text">${data.output}</pre>`;
    })
    .catch(error => {
        outputDiv.innerHTML = `<pre class="error-text">Error: ${error}</pre>`;
    });
}

function clearOutput() {
    document.getElementById('output').innerHTML = '';
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        if (e.key === 'Enter') {
            e.preventDefault();
            runCode();
        }
    }
});