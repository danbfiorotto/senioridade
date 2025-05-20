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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Comparador de Listas de Senioridade</h1>
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
                        const oldData = await oldResponse.json();

                        // Process new file
                        const newContent = await readFileAsBase64(newFile);
                        const newResponse = await fetch('/api', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ pdf_content: newContent })
                        });
                        const newData = await newResponse.json();

                        // Compare results
                        const comparison = compareLists(oldData, newData);
                        displayResults(comparison);
                    } catch (error) {
                        resultDiv.innerHTML = 'Erro: ' + error.message;
                    }
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