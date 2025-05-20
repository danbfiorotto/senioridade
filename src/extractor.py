import pdfplumber
import pandas as pd
from typing import List, Dict, Optional, Union
import logging
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_data(file: Union[BytesIO, str], config: Dict) -> pd.DataFrame:
    """
    Extrai dados de um arquivo PDF ou Excel.
    
    Args:
        file: Arquivo PDF ou Excel (BytesIO ou caminho do arquivo)
        config: Dicionário com configurações de extração
        
    Returns:
        DataFrame pandas com os dados extraídos
    """
    try:
        if isinstance(file, BytesIO):
            if file.name.endswith('.pdf'):
                with pdfplumber.open(file) as pdf:
                    first_page = pdf.pages[0]
                    table = first_page.extract_table()
                    
                    if not table:
                        raise ValueError("Nenhuma tabela encontrada no PDF")
                    
                    # Converter para DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
            else:  # Excel file
                df = pd.read_excel(file)
        else:  # File path
            if file.endswith('.pdf'):
                with pdfplumber.open(file) as pdf:
                    first_page = pdf.pages[0]
                    table = first_page.extract_table()
                    
                    if not table:
                        raise ValueError("Nenhuma tabela encontrada no PDF")
                    
                    # Converter para DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
            else:  # Excel file
                df = pd.read_excel(file)
        
        if df.empty:
            raise ValueError("O arquivo não contém dados")
        
        logger.info(f"Colunas encontradas no arquivo: {df.columns.tolist()}")
        
        # Limpar os dados
        df = df.replace('', pd.NA).dropna(how='all')
        logger.info(f"Número de linhas após limpeza inicial: {len(df)}")
        
        # Tentar identificar a coluna do RE
        re_column = None
        
        # Primeiro, procurar por uma coluna chamada 'RE'
        if 'RE' in df.columns:
            re_column = 'RE'
            logger.info("Coluna 'RE' encontrada diretamente")
        else:
            # Procurar por colunas que possam conter o RE
            for col in df.columns:
                # Verificar se a coluna contém números
                if df[col].astype(str).str.contains(r'\d').any():
                    logger.info(f"Coluna '{col}' contém números")
                    # Verificar se os números têm o formato típico de RE (geralmente 5-6 dígitos)
                    sample_values = df[col].astype(str).str.extract(r'(\d{5,6})')[0].dropna()
                    if not sample_values.empty:
                        re_column = col
                        logger.info(f"Coluna '{col}' contém números no formato de RE")
                        break
        
        if re_column is None:
            # Se não encontrou uma coluna específica, tentar usar a primeira coluna que contenha números
            for col in df.columns:
                if df[col].astype(str).str.contains(r'\d').any():
                    re_column = col
                    logger.info(f"Usando coluna '{col}' como RE (contém números)")
                    break
        
        if re_column is None:
            raise ValueError("Não foi possível identificar a coluna do RE")
        
        # Extrair números da coluna do RE
        df['RE'] = df[re_column].astype(str).str.extract(r'(\d+)')[0]
        logger.info(f"REs extraídos: {df['RE'].tolist()[:5]}...")
        
        # Remover linhas sem RE válido
        df = df[df['RE'].notna()]
        logger.info(f"Número de linhas após remover REs nulos: {len(df)}")
        
        # Remover linhas onde o RE não é um número válido (4-7 dígitos)
        df = df[df['RE'].str.len().between(4, 7)]
        logger.info(f"Número de linhas após filtrar REs por tamanho: {len(df)}")
        
        if df.empty:
            raise ValueError("Não foi possível encontrar REs válidos no arquivo")
        
        # Manter apenas as colunas necessárias
        columns_to_keep = ['RE']
        for col in ['FUNÇÃO', 'EQUIPAMENTO', 'NOME', 'NOME DE GUERRA', 'SENIORIDADE']:
            if col in df.columns:
                columns_to_keep.append(col)
        
        df = df[columns_to_keep]
        logger.info(f"Colunas finais: {df.columns.tolist()}")
        logger.info(f"Número final de registros: {len(df)}")
        
        return df
        
    except Exception as e:
        logger.error(f"Erro ao extrair dados do arquivo: {str(e)}")
        raise

class PDFExtractor:
    """Classe responsável por extrair dados de arquivos PDF de listas de senioridade."""
    
    def __init__(self):
        self.required_columns = ['FUNÇÃO', 'EQUIPAMENTO', 'NOME', 'NOME DE GUERRA', 'RE', 'SENIORIDADE']
    
    def extract_table_from_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Extrai tabela de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            DataFrame pandas com os dados extraídos
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Assumindo que a tabela está na primeira página
                first_page = pdf.pages[0]
                table = first_page.extract_table()
                
                if not table:
                    raise ValueError("Nenhuma tabela encontrada no PDF")
                
                # Converter para DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])
                
                # Verificar se todas as colunas necessárias estão presentes
                missing_columns = [col for col in self.required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"Colunas ausentes no PDF: {missing_columns}")
                
                return df
                
        except Exception as e:
            logger.error(f"Erro ao extrair dados do PDF {pdf_path}: {str(e)}")
            raise
    
    def extract_from_pdfs(self, old_pdf_path: str, new_pdf_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Extrai dados de dois PDFs (lista antiga e nova).
        
        Args:
            old_pdf_path: Caminho para o PDF da lista antiga
            new_pdf_path: Caminho para o PDF da lista nova
            
        Returns:
            Tupla com dois DataFrames (lista antiga e nova)
        """
        logger.info("Iniciando extração dos PDFs...")
        
        old_df = self.extract_table_from_pdf(old_pdf_path)
        new_df = self.extract_table_from_pdf(new_pdf_path)
        
        logger.info("Extração concluída com sucesso!")
        return old_df, new_df 