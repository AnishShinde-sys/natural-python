function runCode() {
    const code = document.getElementById('code-editor').value;
    const outputDiv = document.getElementById('output');
    
    fetch('/run_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: code })
    })
    .then(response => response.json())
    .then(data => {
        outputDiv.textContent = data.output;
    })
    .catch(error => {
        outputDiv.textContent = `Error: ${error}`;
    });
}

function clearCode() {
    if (confirm('Are you sure you want to clear everything?')) {
        document.getElementById('code-editor').value = '';
        document.getElementById('output').textContent = '';
    }
}

function insertExample(code) {
    const editor = document.getElementById('code-editor');
    editor.value += code + '\n';
    editor.focus();
}