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
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .container { border: 1px solid #ccc; padding: 20px; border-radius: 5px; }
                .file-input { margin: 10px 0; }
                .button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                .button:hover { background-color: #45a049; }
                #result { margin-top: 20px; }
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
                    resultDiv.innerHTML = `
                        <h2>Resultados</h2>
                        <p>Total na Lista Antiga: ${comparison.total_old}</p>
                        <p>Total na Lista Nova: ${comparison.total_new}</p>
                        <p>Entradas: ${comparison.entries.length}</p>
                        <p>Saídas: ${comparison.exits.length}</p>
                        
                        <h3>Pessoas que Entraram</h3>
                        <pre>${JSON.stringify(comparison.entries, null, 2)}</pre>
                        
                        <h3>Pessoas que Saíram</h3>
                        <pre>${JSON.stringify(comparison.exits, null, 2)}</pre>
                    `;
                }
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode()) 