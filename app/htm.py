# Interface Frontend (HTML/CSS/JS) para a Ana
# ---------------------------------------------------------------------------

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ana - Auditora de Saúde</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-deep: #0f172a;
            --bg-card: #1e293b;
            --accent-primary: #22d3ee;
            --accent-secondary: #14b8a6;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --glass-border: rgba(255, 255, 255, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-deep);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 900px;
            background: var(--bg-card);
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            border: 1px solid var(--glass-border);
            overflow: hidden;
            animation: fadeIn 0.8s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        header {
            padding: 30px;
            text-align: center;
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.1), rgba(20, 184, 166, 0.1));
            border-bottom: 1px solid var(--glass-border);
        }

        header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        header p {
            color: var(--text-dim);
            font-size: 1rem;
        }

        .chat-area {
            padding: 30px;
            max-height: 600px;
            overflow-y: auto;
        }

        .input-group {
            padding: 30px;
            background: rgba(15, 23, 42, 0.5);
            display: flex;
            gap: 15px;
            border-top: 1px solid var(--glass-border);
        }

        input[type="text"] {
            flex: 1;
            background: var(--bg-deep);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 15px 20px;
            color: white;
            font-size: 1rem;
            transition: all 0.3s;
            outline: none;
        }

        input[type="text"]:focus {
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.2);
        }

        button {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border: none;
            border-radius: 12px;
            color: #0f172a;
            padding: 0 25px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, filter 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        button:hover {
            transform: scale(1.02);
            filter: brightness(1.1);
        }

        button:active {
            transform: scale(0.98);
        }

        .result-card {
            background: rgba(15, 23, 42, 0.3);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid var(--glass-border);
            display: none;
        }

        .result-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            color: var(--accent-primary);
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .ana-output {
            line-height: 1.6;
            color: #e2e8f0;
        }

        .ana-output table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.9rem;
        }

        .ana-output th, .ana-output td {
            border: 1px solid var(--glass-border);
            padding: 8px 12px;
            text-align: left;
        }

        .ana-output th {
            background: rgba(34, 211, 238, 0.1);
        }

        .metrics {
            margin-top: 20px;
            display: flex;
            gap: 20px;
            font-size: 0.8rem;
            color: var(--text-dim);
        }

        .metric-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 5px 12px;
            border-radius: 20px;
        }

        .suggested {
            padding: 0 30px 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .suggestion-chip {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--glass-border);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s;
            color: var(--text-dim);
        }

        .suggestion-chip:hover {
            background: rgba(34, 211, 238, 0.1);
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }

        .loader {
            display: none;
            text-align: center;
            padding: 20px;
            color: var(--accent-primary);
            font-style: italic;
        }

        .dot-flashing {
            position: relative;
            width: 10px;
            height: 10px;
            border-radius: 5px;
            background-color: var(--accent-primary);
            color: var(--accent-primary);
            animation: dotFlashing 1s infinite linear alternate;
            display: inline-block;
            margin-left: 15px;
        }

        @keyframes dotFlashing {
            0% { background-color: var(--accent-primary); }
            50%, 100% { background-color: rgba(34, 211, 238, 0.2); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; max-width: 840px; margin: 0 auto;">
                <div style="text-align: left;">
                    <h1>Ana Auditora</h1>
                    <p style="margin-bottom: 0;">Sua assistente inteligente para análise de glosas.</p>
                </div>
                <a href="/mlflow" target="_blank" class="suggestion-chip" style="text-decoration: none; border-color: var(--accent-primary); color: var(--accent-primary); display: flex; align-items: center; gap: 8px; padding: 8px 16px; font-weight: 600;">
                    📊 Dash MLflow
                </a>
            </div>
        </header>

        <div class="chat-area" id="chatArea">
            <div id="welcomeMessage">
                <p style="color: var(--text-dim); text-align: center; font-style: italic;">
                    Faça uma pergunta sobre reembolsos, glosas ou empresas específicas abaixo.
                </p>
            </div>
            <div class="loader" id="loader">
                Ana está refletindo <div class="dot-flashing"></div>
            </div>
            <div id="resultContainer" class="result-card">
                <div class="result-header">✨ Resposta da Ana</div>
                <div class="ana-output" id="anaOutput"></div>
                <div class="metrics" id="metrics"></div>
            </div>
        </div>

        <div class="suggested">
            <div class="suggestion-chip" onclick="ask('Qual o resumo das glosas previstas?')">Resumo de Glosas</div>
            <div class="suggestion-chip" onclick="ask('Maiores glosas da Empresa Alfa?')">Empresa Alfa</div>
            <div class="suggestion-chip" onclick="ask('Qual a média de valor solicitado por empresa?')">Média por Empresa</div>
        </div>

        <div class="input-group">
            <input type="text" id="userInput" placeholder="Pergunte algo à Ana..." onkeypress="handleKey(event)">
            <button onclick="submitQuery()">
                Perguntar
            </button>
        </div>
    </div>

    <script>
        async function ask(text) {
            document.getElementById('userInput').value = text;
            await submitQuery();
        }

        function handleKey(e) {
            if (e.key === 'Enter') submitQuery();
        }

        async function submitQuery() {
            const input = document.getElementById('userInput');
            const query = input.value.trim();
            if (!query) return;

            // Reset UI
            document.getElementById('welcomeMessage').style.display = 'none';
            const resultCard = document.getElementById('resultContainer');
            const loader = document.getElementById('loader');
            const output = document.getElementById('anaOutput');
            const metrics = document.getElementById('metrics');

            resultCard.style.display = 'none';
            loader.style.display = 'block';
            input.value = '';
            input.disabled = true;

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: query })
                });

                const data = await response.json();

                if (response.ok) {
                    // Render Markdown
                    output.innerHTML = marked.parse(data.answer);
                    
                    // Render Metrics
                    metrics.innerHTML = `
                        <div class="metric-item">⏱️ ${data.duration_ms}ms</div>
                        <div class="metric-item">⚙️ ${data.tools_used.join(', ')}</div>
                        <div class="metric-item">📊 Passos: ${data.step_count}</div>
                    `;
                    
                    resultCard.style.display = 'block';
                    // Auto scroll
                    document.getElementById('chatArea').scrollTop = document.getElementById('chatArea').scrollHeight;
                } else {
                    alert('Erro: ' + data.detail);
                }
            } catch (err) {
                alert('Erro de conexão com o servidor.');
            } finally {
                loader.style.display = 'none';
                input.disabled = false;
                input.focus();
            }
        }
    </script>
</body>
</html>
"""
