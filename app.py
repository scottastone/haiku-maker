# --- Haiku Syllable Analyzer Flask App ---
# This single file contains the backend, frontend, and styling for the web app.

from flask import Flask, request, jsonify, render_template_string
import syllables
import re

# Initialize the Flask application
app = Flask(__name__)

# --- HTML & JavaScript Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>haiku validator</title>
    <style>
        :root {
            --bg-color: #1a1a1a;
            --text-color: #e0e0e0;
            --primary-color: #4CAF50;
            --secondary-color: #2c2c2c;
            --border-color: #444;
            --error-color: #e57373;
            --success-color: #81c784;
            --font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            font-family: var(--font-family);
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }
        .container {
            width: 100%;
            max-width: 1000px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            background-color: var(--secondary-color);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        header {
            grid-column: 1 / -1;
            text-align: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }
        header h1 {
            color: var(--primary-color);
            margin: 0;
        }
        #haiku-input {
            width: 100%;
            height: 225px;
            background-color: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            font-size: 2rem;
            resize: none;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }
        #haiku-input:focus {
            outline: none;
            border-color: var(--primary-color);
        }
        #analysis-results {
            background-color: var(--bg-color);
            padding: 1rem;
            border-radius: 8px;
            height: 225px;
            overflow-y: auto;
            box-sizing: border-box;
            border: 1px solid var(--border-color);
        }
        .line-analysis {
            margin-bottom: 1rem;
        }
        .line-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
        }
        .syllable-count {
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.9rem;
        }
        .syllable-count.correct { background-color: var(--success-color); color: #111; }
        .syllable-count.incorrect { background-color: var(--error-color); color: #111; }
        .word-breakdown {
            font-size: 0.9rem;
            color: #aaa;
            margin-top: 0.3rem;
            word-wrap: break-word;
        }
        #haiku-status {
            grid-column: 1 / -1;
            text-align: center;
            padding-top: 1.5rem;
            font-size: 1.2rem;
            font-weight: bold;
            height: 30px;
        }
        
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
            body { padding: 1rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>haiku validator</h1>
            <p>3 lines, with 5-7-5 syllables</p>
        </header>
        
        <div>
            <textarea id="haiku-input" placeholder="type your haiku here..." maxlength="1000"></textarea>
        </div>

        <div id="analysis-results">
            <p style="color: #888;"></p>
        </div>
        
        <div id="haiku-status"></div>

        <footer style="grid-column: 1 / -1; text-align: center; margin-top: 2rem; font-size: 0.8rem; color: #666;">
            made by scott stone using 
            <code style="font-family: 'Courier New', Courier, monospace;"><a href="https://flask.palletsprojects.com/" target="_blank" style="color: #666;">Flask</a></code> 
            and 
            <code style="font-family: 'Courier New', Courier, monospace;"><a href="https://pypi.org/project/syllables/" target="_blank" style="color: #666;">syllables</a></code>.
            <br>
            <a href="/overrides" style="color: #666; text-decoration: none;">view syllable overrides file</a>
        </footer>
    </div>

    <script>
        const haikuInput = document.getElementById('haiku-input');
        const analysisResults = document.getElementById('analysis-results');
        const haikuStatus = document.getElementById('haiku-status');
        let debounceTimer;

        haikuInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                analyzeText(haikuInput.value);
            }, 100); // Wait 300ms after user stops typing
        });

        async function analyzeText(text) {
            if (!text.trim()) {
                analysisResults.innerHTML = '<p style="color: #888;"></p>';
                haikuStatus.textContent = '';
                return;
            }

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const data = await response.json();
                updateResults(data);
            } catch (error) {
                console.error("Error analyzing text:", error);
                analysisResults.innerHTML = '<p style="color: var(--error-color);">Error connecting to the server.</p>';
            }
        }

        function updateResults(data) {
            analysisResults.innerHTML = '';
            const expectedSyllables = [5, 7, 5];
            
            data.lines.forEach((lineData, index) => {
                if (!lineData.line.trim() && index >= data.lines.length) return;

                const expected = expectedSyllables[index];
                const isCorrect = lineData.syllables === expected;
                
                const lineDiv = document.createElement('div');
                lineDiv.className = 'line-analysis';
                
                let countClass = 'incorrect';
                if (lineData.syllables > 0) {
                   countClass = isCorrect ? 'correct' : 'incorrect';
                }

                lineDiv.innerHTML = `
                    <div class="line-header">
                        <span>Line ${index + 1}</span>
                        <span class="syllable-count ${countClass}">${lineData.syllables} / ${expected}</span>
                    </div>
                    <div class="word-breakdown">${lineData.breakdown || '&nbsp;'}</div>
                `;
                analysisResults.appendChild(lineDiv);
            });

            if (data.is_haiku) {
                haikuStatus.textContent = "haiku detected!";
                haikuStatus.style.color = 'var(--success-color)';
            } else {
                haikuStatus.textContent = "keep writing...";
                haikuStatus.style.color = 'var(--text-color)';
            }
        }
    </script>
</body>
</html>
"""

# --- Backend Logic ---

# Dictionary for manual syllable count overrides for common miscounted words
SYLLABLE_OVERRIDES = {}
SYLLABLE_OVERRIDES_FILE = "syllable_overrides.txt"
def load_syllable_overrides(filename: str):
    """Loads syllable overrides from a file."""
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            word, count = line.strip().split(':')
            SYLLABLE_OVERRIDES[word] = int(count)
        
def analyze_line(line):
    """Analyzes a single line of text for syllable count and breakdown."""
    # Updated regex to include apostrophes within words
    words = re.findall(r"[\w']+", line.lower())
    total_syllables = 0
    word_counts = []
    
    for word in words:
        try:
            # Check for a manual override first, otherwise estimate
            if word in SYLLABLE_OVERRIDES:
                count = SYLLABLE_OVERRIDES[word]
            else:
                count = syllables.estimate(word)
            
            total_syllables += count
            word_counts.append(f"{word}({count})")
        except Exception:
            word_counts.append(f"{word}(?)")
            
    return {
        "line": line,
        "syllables": total_syllables,
        "breakdown": " ".join(word_counts)
    }

@app.route('/')
def index():
    """Renders the main HTML page."""
    load_syllable_overrides(SYLLABLE_OVERRIDES_FILE)
    return render_template_string(HTML_TEMPLATE)

@app.route('/overrides', methods=['GET'])
def show_overrides():
    """Renders a page showing all syllable overrides."""
    load_syllable_overrides(SYLLABLE_OVERRIDES_FILE) # Ensure overrides are loaded
    with open(SYLLABLE_OVERRIDES_FILE, 'r') as file:
        content = file.read()
    return f"{content}", 200, {'Content-Type': 'text/plain'}

@app.route('/analyze', methods=['POST'])
def analyze():
    """simple API endpoint to analyze text and return syllable counts."""
    data = request.get_json()
    text = data.get('text', '')
    lines = text.split('\n')

    # Analyze the first 3 lines
    analysis = [analyze_line(line) for line in lines[:3]]
    
    # Pad with empty results if less than 3 lines
    while len(analysis) < 3:
        analysis.append({"line": "", "syllables": 0, "breakdown": ""})

    # Check if it's a valid haiku
    is_haiku = (
        analysis[0]['syllables'] == 5 and
        analysis[1]['syllables'] == 7 and
        analysis[2]['syllables'] == 5
    )

    return jsonify({
        "lines": analysis,
        "is_haiku": is_haiku
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
