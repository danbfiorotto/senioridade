# Leitor de PDF - Lista de Senioridade

Aplicativo para extrair e visualizar tabelas de senioridade de arquivos PDF.

## 🚀 Funcionalidades

- Extração de dados de arquivos PDF
- Visualização da tabela extraída
- Exportação dos dados em CSV
- Interface web amigável

## 📋 Pré-requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd lista_senioridade
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🎮 Uso

Execute o aplicativo com:
```bash
streamlit run src/app.py
```

O aplicativo abrirá em seu navegador padrão. Basta fazer upload do arquivo PDF contendo a lista de senioridade e a tabela será extraída e exibida.

## 📁 Estrutura do Projeto

```
lista_senioridade/
├── src/                   # Código fonte
│   └── app.py            # Aplicativo Streamlit
├── requirements.txt      # Dependências
└── README.md            # Documentação
```

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 