let editor;
let isDark = true;
let isMenuOpen = true;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'python',
        theme: 'dracula',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
        extraKeys: {
            "Tab": function(cm) {
                cm.replaceSelection("    ", "end");
            },
            "Ctrl-Enter": runCode,
            "Cmd-Enter": runCode
        },
        gutters: ["CodeMirror-linenumbers"],
        lint: true,
        styleActiveLine: true,
        styleActiveSelected: true,
        scrollbarStyle: "overlay"
    });

    // Set initial content
    editor.setValue(`# Welcome to Natural Python IDE!
# Try these examples:

Make a number called score equal to 10
Add 5 to score
Print score

# Try an if statement:
If score is bigger than 12:
    Print "High score!"

# More operations:
Multiply 2 by score
Print score`);

    // Setup event listeners
    setupEventListeners();
    
    // Initial UI state
    updateTheme();
    updateMenuState();
});

function setupEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', () => {
        isDark = !isDark;
        updateTheme();
    });

    // Menu toggle
    document.getElementById('menuToggle').addEventListener('click', () => {
        isMenuOpen = !isMenuOpen;
        updateMenuState();
    });

    // File tree interactions
    document.querySelectorAll('.file').forEach(file => {
        file.addEventListener('click', () => {
            document.querySelectorAll('.file').forEach(f => f.classList.remove('active'));
            file.classList.add('active');
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function updateTheme() {
    document.body.classList.toggle('theme-dark', isDark);
    editor.setOption('theme', isDark ? 'dracula' : 'default');
    
    // Update theme toggle icon
    const themeIcon = document.querySelector('#themeToggle svg');
    themeIcon.innerHTML = isDark ? 
        '<path d="M12 3a6 6 0 0 0 0 12h6a6 6 0 0 0 0-12h-6z" fill="currentColor"/>' :
        '<circle cx="12" cy="12" r="4" fill="currentColor"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41" stroke="currentColor" stroke-width="2"/>';
}

function updateMenuState() {
    const sidebar = document.getElementById('sidebar');
    sidebar.style.width = isMenuOpen ? '240px' : '0';
    sidebar.style.minWidth = isMenuOpen ? '240px' : '0';
}

function runCode() {
    const code = editor.getValue();
    const outputDiv = document.getElementById('output');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    // Reset output and show loading
    outputDiv.innerHTML = '<div class="loading">Running code...</div>';
    progressBar.style.width = '0%';
    progressText.textContent = '0%';

    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;
        if (progress >= 100) clearInterval(progressInterval);
    }, 50);

    // Send code to server
    fetch('/run_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code })
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
        
        if (data.error) {
            outputDiv.innerHTML = `<pre class="error">${data.error}</pre>`;
        } else {
            outputDiv.innerHTML = `<pre class="success">${data.output}</pre>`;
        }
    })
    .catch(error => {
        clearInterval(progressInterval);
        outputDiv.innerHTML = `<pre class="error">Error: ${error.message}</pre>`;
    });
}

function clearOutput() {
    const outputDiv = document.getElementById('output');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    outputDiv.innerHTML = '';
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
}

function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + Enter to run code
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        runCode();
    }
    
    // Ctrl/Cmd + B to toggle sidebar
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        isMenuOpen = !isMenuOpen;
        updateMenuState();
    }
}

// Add some helper functions for the editor
function insertExample(code) {
    const doc = editor.getDoc();
    const cursor = doc.getCursor();
    doc.replaceRange(code + '\n', cursor);
    editor.focus();
}

// Export functions for global use
window.runCode = runCode;
window.clearOutput = clearOutput;
window.insertExample = insertExample;