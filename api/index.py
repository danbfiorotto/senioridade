from http.server import BaseHTTPRequestHandler
import json
import pdfplumber
import pandas as pd
import base64
from io import BytesIO

def extract_table_from_pdf(pdf_content):
    """
    Extrai a tabela de um arquivo PDF, ignorando cabeçalho e rodapé.
    """
    try:
        all_tables = []
        with pdfplumber.open(BytesIO(pdf_content)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    table = tables[0]
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append(df)
        
        if not all_tables:
            raise ValueError("Nenhuma tabela encontrada no PDF")
        
        final_df = pd.concat(all_tables, ignore_index=True)
        return final_df.to_dict(orient='records')
        
    except Exception as e:
        return {"error": str(e)}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        try:
            # Decode base64 PDF content
            pdf_content = base64.b64decode(data['pdf_content'])
            
            # Process PDF
            result = extract_table_from_pdf(pdf_content)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Return a simple HTML form
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comparador de Listas de Senioridade</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                }
                h1 {
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .file-input {
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 6px;
                }
                .file-input h3 {
                    color: #2c3e50;
                    margin-bottom: 10px;
                }
                .button {
                    background-color: #3498db;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background-color 0.3s;
                    display: block;
                    margin: 20px auto;
                }
                .button:hover {
                    background-color: #2980b9;
                }
                .stats-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .stat-box {
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }
                .stat-box h3 {
                    color: #7f8c8d;
                    margin: 0;
                    font-size: 14px;
                }
                .stat-number {
                    color: #2c3e50;
                    font-size: 24px;
                    font-weight: bold;
                    margin: 10px 0 0;
                }
                .tables-container {
                    margin-top: 30px;
                }
                .table-section {
                    margin-bottom: 40px;
                }
                .table-section h2 {
                    color: #2c3e50;
                    margin-bottom: 20px;
                }
                .table-container {
                    overflow-x: auto;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background-color: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                th, td {
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    font-weight: 600;
                }
                tr:hover {
                    background-color: #f8f9fa;
                }
                .no-data {
                    text-align: center;
                    color: #7f8c8d;
                    padding: 20px;
                }
                @media (max-width: 768px) {
                    .stats-container {
                        grid-template-columns: 1fr;
                    }
                    .table-container {
                        margin: 0 -20px;
                    }
                }
                .search-section {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }
                .search-box {
                    display: flex;
                    gap: 10px;
                    margin-top: 10px;
                }
                .search-box input {
                    flex: 1;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 16px;
                }
                .search-button {
                    margin: 0;
                }
                .search-result {
                    margin-top: 20px;
                }
                .search-result-content {
                    background-color: white;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .alert {
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .alert.success {
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
                .alert.error {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
                .alert.warning {
                    background-color: #fff3cd;
                    color: #856404;
                    border: 1px solid #ffeeba;
                }
                .alert.info {
                    background-color: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                }
                .data-card {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 20px;
                }
                .data-card h4 {
                    margin-top: 0;
                    color: #2c3e50;
                    margin-bottom: 15px;
                }
                .data-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .data-table th,
                .data-table td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                .data-table th {
                    width: 30%;
                    color: #6c757d;
                }
                .changes-container {
                    display: grid;
                    gap: 20px;
                }
                .changes-card {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                }
                .changes-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .changes-table th,
                .changes-table td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                .changes-table th {
                    background-color: #e9ecef;
                    color: #495057;
                }
                @media (max-width: 768px) {
                    .search-box {
                        flex-direction: column;
                    }
                    .search-button {
                        width: 100%;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Comparador de Listas de Senioridade</h1>
                
                <!-- Adicionando seção de busca por RE -->
                <div class="search-section">
                    <h3>🔍 Buscar por RE</h3>
                    <div class="search-box">
                        <input type="text" id="reSearch" placeholder="Digite o RE para buscar">
                        <button class="button search-button" onclick="searchRE()">Buscar</button>
                    </div>
                    <div id="searchResult" class="search-result"></div>
                </div>

                <div class="file-input">
                    <h3>Lista Antiga</h3>
                    <input type="file" id="oldFile" accept=".pdf">
                </div>
                <div class="file-input">
                    <h3>Lista Nova</h3>
                    <input type="file" id="newFile" accept=".pdf">
                </div>
                <button class="button" onclick="processFiles()">Processar</button>
                <div id="result"></div>
            </div>

            <script>
                let oldData = null;
                let newData = null;

                async function processFiles() {
                    const oldFile = document.getElementById('oldFile').files[0];
                    const newFile = document.getElementById('newFile').files[0];
                    
                    if (!oldFile || !newFile) {
                        alert('Por favor, selecione ambos os arquivos PDF');
                        return;
                    }

                    const resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = 'Processando...';

                    try {
                        // Process old file
                        const oldContent = await readFileAsBase64(oldFile);
                        const oldResponse = await fetch('/api', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ pdf_content: oldContent })
                        });
                        oldData = await oldResponse.json();

                        // Process new file
                        const newContent = await readFileAsBase64(newFile);
                        const newResponse = await fetch('/api', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ pdf_content: newContent })
                        });
                        newData = await newResponse.json();

                        // Compare results
                        const comparison = compareLists(oldData, newData);
                        displayResults(comparison);
                    } catch (error) {
                        resultDiv.innerHTML = 'Erro: ' + error.message;
                    }
                }

                function searchRE() {
                    const reInput = document.getElementById('reSearch').value.trim();
                    const searchResult = document.getElementById('searchResult');
                    
                    if (!reInput) {
                        searchResult.innerHTML = '<p class="error">Por favor, digite um RE para buscar</p>';
                        return;
                    }

                    if (!oldData || !newData) {
                        searchResult.innerHTML = '<p class="error">Por favor, processe os arquivos PDF primeiro</p>';
                        return;
                    }

                    const result = analyzeREChanges(reInput, oldData, newData);
                    displaySearchResult(result);
                }

                function analyzeREChanges(re, oldList, newList) {
                    const oldEntry = oldList.find(item => item.RE === re);
                    const newEntry = newList.find(item => item.RE === re);

                    if (!oldEntry && !newEntry) {
                        return {
                            status: 'not_found',
                            message: 'RE não encontrado em nenhuma das listas'
                        };
                    }

                    if (!oldEntry) {
                        return {
                            status: 'new_entry',
                            message: 'RE encontrado apenas na lista nova',
                            data: newEntry
                        };
                    }

                    if (!newEntry) {
                        return {
                            status: 'exit',
                            message: 'RE encontrado apenas na lista antiga',
                            data: oldEntry
                        };
                    }

                    // Se encontrou em ambas as listas, compara as mudanças
                    const changes = [];
                    for (const key in oldEntry) {
                        if (oldEntry[key] !== newEntry[key]) {
                            changes.push({
                                campo: key,
                                valor_antigo: oldEntry[key],
                                valor_novo: newEntry[key]
                            });
                        }
                    }

                    return {
                        status: 'changed',
                        message: 'RE encontrado em ambas as listas com mudanças',
                        data: {
                            antigo: oldEntry,
                            novo: newEntry,
                            mudancas: changes
                        }
                    };
                }

                function displaySearchResult(result) {
                    const searchResult = document.getElementById('searchResult');
                    
                    let html = '<div class="search-result-content">';
                    
                    switch (result.status) {
                        case 'not_found':
                            html += `<div class="alert warning">${result.message}</div>`;
                            break;
                            
                        case 'new_entry':
                            html += `
                                <div class="alert success">${result.message}</div>
                                <div class="data-card">
                                    <h4>Dados na Lista Nova:</h4>
                                    ${createDataTable(result.data)}
                                </div>`;
                            break;
                            
                        case 'exit':
                            html += `
                                <div class="alert error">${result.message}</div>
                                <div class="data-card">
                                    <h4>Dados na Lista Antiga:</h4>
                                    ${createDataTable(result.data)}
                                </div>`;
                            break;
                            
                        case 'changed':
                            html += `
                                <div class="alert info">${result.message}</div>
                                <div class="changes-container">
                                    <div class="data-card">
                                        <h4>Dados na Lista Antiga:</h4>
                                        ${createDataTable(result.data.antigo)}
                                    </div>
                                    <div class="data-card">
                                        <h4>Dados na Lista Nova:</h4>
                                        ${createDataTable(result.data.novo)}
                                    </div>
                                    <div class="changes-card">
                                        <h4>Mudanças:</h4>
                                        <table class="changes-table">
                                            <thead>
                                                <tr>
                                                    <th>Campo</th>
                                                    <th>Valor Antigo</th>
                                                    <th>Valor Novo</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${result.data.mudancas.map(change => `
                                                    <tr>
                                                        <td>${change.campo}</td>
                                                        <td>${change.valor_antigo}</td>
                                                        <td>${change.valor_novo}</td>
                                                    </tr>
                                                `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>`;
                            break;
                    }
                    
                    html += '</div>';
                    searchResult.innerHTML = html;
                }

                function createDataTable(data) {
                    return `
                        <table class="data-table">
                            <tbody>
                                ${Object.entries(data).map(([key, value]) => `
                                    <tr>
                                        <th>${key}</th>
                                        <td>${value}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                }

                function readFileAsBase64(file) {
                    return new Promise((resolve, reject) => {
                        const reader = new FileReader();
                        reader.onload = () => resolve(reader.result.split(',')[1]);
                        reader.onerror = reject;
                        reader.readAsDataURL(file);
                    });
                }

                function compareLists(oldList, newList) {
                    const oldREs = new Set(oldList.map(item => item.RE));
                    const newREs = new Set(newList.map(item => item.RE));

                    const entries = newList.filter(item => !oldREs.has(item.RE));
                    const exits = oldList.filter(item => !newREs.has(item.RE));

                    return {
                        total_old: oldList.length,
                        total_new: newList.length,
                        entries: entries,
                        exits: exits
                    };
                }

                function displayResults(comparison) {
                    const resultDiv = document.getElementById('result');
                    
                    // Create table HTML for entries
                    const entriesTable = createTable(comparison.entries, 'Pessoas que Entraram');
                    const exitsTable = createTable(comparison.exits, 'Pessoas que Saíram');
                    
                    resultDiv.innerHTML = `
                        <div class="stats-container">
                            <div class="stat-box">
                                <h3>Total na Lista Antiga</h3>
                                <p class="stat-number">${comparison.total_old}</p>
                            </div>
                            <div class="stat-box">
                                <h3>Total na Lista Nova</h3>
                                <p class="stat-number">${comparison.total_new}</p>
                            </div>
                            <div class="stat-box">
                                <h3>Entradas</h3>
                                <p class="stat-number">${comparison.entries.length}</p>
                            </div>
                            <div class="stat-box">
                                <h3>Saídas</h3>
                                <p class="stat-number">${comparison.exits.length}</p>
                            </div>
                        </div>
                        
                        <div class="tables-container">
                            ${entriesTable}
                            ${exitsTable}
                        </div>
                    `;
                }

                function createTable(data, title) {
                    if (!data || data.length === 0) {
                        return `<div class="table-section">
                            <h2>${title}</h2>
                            <p class="no-data">Nenhum registro encontrado</p>
                        </div>`;
                    }

                    const headers = Object.keys(data[0]);
                    const tableRows = data.map(item => {
                        return `<tr>
                            ${headers.map(header => `<td>${item[header]}</td>`).join('')}
                        </tr>`;
                    }).join('');

                    return `
                        <div class="table-section">
                            <h2>${title}</h2>
                            <div class="table-container">
                                <table>
                                    <thead>
                                        <tr>
                                            ${headers.map(header => `<th>${header}</th>`).join('')}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${tableRows}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                }
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode()) 