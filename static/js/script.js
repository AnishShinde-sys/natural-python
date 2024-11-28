document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();

    // Elements
    const codeEditor = document.getElementById('codeEditor');
    const outputText = document.getElementById('outputText');
    const runButton = document.getElementById('runCode');
    const toggleTheme = document.getElementById('toggleTheme');
    const toggleSidebar = document.getElementById('toggleSidebar');
    const toggleOutput = document.getElementById('toggleOutput');
    const explorer = document.getElementById('explorer');
    const output = document.getElementById('output');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const lineNumbers = document.getElementById('lineNumbers');

    // Theme handling
    let isDarkMode = localStorage.getItem('darkMode') === 'true';
    updateTheme();

    toggleTheme.addEventListener('click', () => {
        isDarkMode = !isDarkMode;
        localStorage.setItem('darkMode', isDarkMode);
        updateTheme();
    });

    function updateTheme() {
        document.documentElement.classList.toggle('dark', isDarkMode);
    }

    // Line numbers
    function updateLineNumbers() {
        const lines = codeEditor.value.split('\n');
        lineNumbers.innerHTML = lines.map((_, i) => 
            `<div class="line-number">${i + 1}</div>`
        ).join('');
    }

    codeEditor.addEventListener('input', updateLineNumbers);
    updateLineNumbers();

    // Code execution
    runButton.addEventListener('click', async function() {
        runButton.disabled = true;
        progressBar.style.width = '0%';
        
        try {
            const response = await fetch('/run_code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: codeEditor.value })
            });
            
            const data = await response.json();
            outputText.textContent = data.output;
            
            // Simulate progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += 5;
                progressBar.style.width = `${progress}%`;
                progressText.textContent = `${progress}% Complete`;
                
                if (progress >= 100) {
                    clearInterval(interval);
                }
            }, 50);
        } catch (error) {
            outputText.textContent = `Error: ${error.message}`;
        } finally {
            runButton.disabled = false;
        }
    });

    // Sidebar toggles
    toggleSidebar.addEventListener('click', () => {
        explorer.classList.toggle('hidden');
    });

    toggleOutput.addEventListener('click', () => {
        output.classList.toggle('hidden');
    });

    // Example starter code
    codeEditor.value = `# Welcome to the Python Natural Language IDE!
# Try writing some commands like:

Make a number called x equal to 10
Print x
Add 5 to x
If x is bigger than 12, Print x`;

    updateLineNumbers();
});