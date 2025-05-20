import pdfplumber
import pandas as pd
import logging
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_table_from_pdf(pdf_file) -> pd.DataFrame:
    """
    Extrai tabelas de todas as páginas de um arquivo PDF, focando nas colunas específicas de listas de senioridade.
    
    Args:
        pdf_file: Arquivo PDF (pode ser um arquivo ou BytesIO)
        
    Returns:
        DataFrame pandas com os dados extraídos
    """
    try:
        all_tables = []
        with pdfplumber.open(pdf_file) as pdf:
            logger.info(f"Total de páginas no PDF: {len(pdf.pages)}")
            
            # Processar cada página
            for page_num, page in enumerate(pdf.pages, 1):
                logger.info(f"Processando página {page_num}")
                
                # Extrair a tabela da página
                table = page.extract_table()
                
                if table:
                    # Se for a primeira página, usar os cabeçalhos
                    if page_num == 1:
                        df = pd.DataFrame(table[1:], columns=table[0])
                    else:
                        # Para outras páginas, usar os mesmos cabeçalhos da primeira página
                        df = pd.DataFrame(table[1:], columns=all_tables[0].columns)
                    
                    # Log das colunas encontradas
                    logger.info(f"Colunas encontradas na página {page_num}: {df.columns.tolist()}")
                    
                    # Limpar os dados
                    df = df.replace('', pd.NA).dropna(how='all')
                    logger.info(f"Número de linhas na página {page_num} após limpeza: {len(df)}")
                    
                    all_tables.append(df)
                else:
                    logger.warning(f"Nenhuma tabela encontrada na página {page_num}")
            
            if not all_tables:
                raise ValueError("Nenhuma tabela encontrada no PDF")
            
            # Combinar todas as tabelas
            combined_df = pd.concat(all_tables, ignore_index=True)
            logger.info(f"Total de linhas após combinar todas as páginas: {len(combined_df)}")
            
            # Identificar e renomear colunas
            column_mapping = {}
            for col in combined_df.columns:
                col_upper = str(col).upper()
                if 'FUNÇÃO' in col_upper or 'FUNCAO' in col_upper:
                    column_mapping[col] = 'FUNÇÃO'
                elif 'EQUIPAMENTO' in col_upper:
                    column_mapping[col] = 'EQUIPAMENTO'
                elif 'NOME' in col_upper and 'GUERRA' not in col_upper:
                    column_mapping[col] = 'NOME'
                elif 'GUERRA' in col_upper:
                    column_mapping[col] = 'NOME DE GUERRA'
                elif 'RE' in col_upper:
                    column_mapping[col] = 'RE'
                elif 'SENIORIDADE' in col_upper:
                    column_mapping[col] = 'SENIORIDADE'
            
            # Renomear colunas
            combined_df = combined_df.rename(columns=column_mapping)
            
            # Manter apenas as colunas necessárias
            required_columns = ['FUNÇÃO', 'EQUIPAMENTO', 'NOME', 'NOME DE GUERRA', 'RE', 'SENIORIDADE']
            available_columns = [col for col in required_columns if col in combined_df.columns]
            
            if not available_columns:
                raise ValueError("Não foi possível identificar as colunas necessárias no PDF")
            
            combined_df = combined_df[available_columns]
            
            # Limpar dados
            for col in combined_df.columns:
                combined_df[col] = combined_df[col].astype(str).str.strip()
            
            # Remover linhas duplicadas
            combined_df = combined_df.drop_duplicates()
            
            logger.info(f"Colunas finais: {combined_df.columns.tolist()}")
            logger.info(f"Número final de registros: {len(combined_df)}")
            
            return combined_df
            
    except Exception as e:
        logger.error(f"Erro ao extrair dados do PDF: {str(e)}")
        raise 