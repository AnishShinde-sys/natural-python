let editor;
let isRunning = false;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById('codeEditor'), {
        mode: 'python',
        theme: 'dracula',
        lineNumbers: true,
        lineWrapping: true,
        indentUnit: 4,
        tabSize: 4,
        autofocus: true,
        styleActiveLine: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        extraKeys: {
            'Ctrl-Enter': runCode,
            'Cmd-Enter': runCode,
            'Tab': (cm) => cm.replaceSelection('    ')
        }
    });

    // Set initial content with comprehensive examples
    editor.setValue(`# Natural Python Test Examples

# 1. Variable Creation and Math
Make a number called score equal to 10
Add 5 to score
Print score
Multiply score by 2
Divide score by 3

# 2. String Operations
Create a string called greeting with "Hello World"
Convert greeting to uppercase
Join greeting with "!"
Print greeting

# 3. List Operations
Make a list numbers equal to [1, 2, 3, 4, 5]
Add 6 to numbers
Remove 3 from numbers
Sort numbers
Print numbers

# 4. Conditional Logic
If score is bigger than 12:
    Print "High score!"
    Double score
    Print "New score is:"
    Print score

# 5. Advanced Operations
Calculate square root of 16
Find maximum of numbers
Generate random number between 1 and 10
Format string "Hello {}" with "Alice"`);

    // Setup event listeners
    setupEventListeners();
    
    // Update cursor position initially
    updateCursorPosition();
});

function setupEventListeners() {
    // Run button
    document.getElementById('runCode').addEventListener('click', runCode);

    // Clear output button
    document.getElementById('clearOutput').addEventListener('click', clearOutput);

    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Cursor position updates
    editor.on('cursorActivity', updateCursorPosition);
}

async function runCode() {
    if (isRunning) return;
    isRunning = true;

    const code = editor.getValue();
    const outputDiv = document.getElementById('output');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const runButton = document.getElementById('runCode');

    // Update UI for running state
    runButton.classList.add('running');
    outputDiv.innerHTML = '<div class="loading">Running code...</div>';
    progressBar.style.width = '0%';
    progressText.textContent = '0%';

    try {
        // Start progress animation
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + 5, 90);
            progressBar.style.width = `${progress}%`;
            progressText.textContent = `${progress}%`;
        }, 50);

        // Send code to server
        const response = await fetch('/run_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        // Complete progress
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressText.textContent = '100%';

        // Show output
        if (data.error) {
            outputDiv.innerHTML = `<pre class="error">${data.error}</pre>`;
        } else {
            outputDiv.innerHTML = `<pre class="success">${data.output}</pre>`;
        }
    } catch (error) {
        outputDiv.innerHTML = `<pre class="error">Error: ${error.message}</pre>`;
    } finally {
        isRunning = false;
        runButton.classList.remove('running');
    }
}

function clearOutput() {
    document.getElementById('output').innerHTML = '';
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('progressText').textContent = '0%';
}

function toggleTheme() {
    const isDark = document.body.classList.toggle('theme-dark');
    editor.setOption('theme', isDark ? 'dracula' : 'default');
}

function updateCursorPosition() {
    const pos = editor.getCursor();
    const cursorPosElem = document.getElementById('cursorPos');
    cursorPosElem.textContent = `Ln ${pos.line + 1}, Col ${pos.ch + 1}`;
}

// Export functions for global use
window.runCode = runCode;
window.clearOutput = clearOutput;