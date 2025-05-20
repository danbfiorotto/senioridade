import pandas as pd
from typing import Dict, List, Tuple
import logging
import unicodedata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ListComparator:
    """Classe responsável por comparar duas listas de senioridade."""
    
    def __init__(self):
        self.changes = []
    
    def _detect_changes(self, old_row: pd.Series, new_row: pd.Series) -> List[Dict]:
        """
        Detecta mudanças entre duas linhas de dados.
        
        Args:
            old_row: Linha da lista antiga
            new_row: Linha da lista nova
            
        Returns:
            Lista de dicionários com as mudanças detectadas
        """
        changes = []
        
        # Comparar cada campo
        for column in ['FUNÇÃO', 'EQUIPAMENTO', 'NOME', 'NOME DE GUERRA', 'SENIORIDADE']:
            if old_row[column] != new_row[column]:
                changes.append({
                    'campo': column,
                    'valor_antigo': old_row[column],
                    'valor_novo': new_row[column]
                })
        
        return changes
    
    def compare_lists(self, old_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compara duas listas de senioridade e identifica mudanças.
        
        Args:
            old_df: DataFrame com a lista antiga
            new_df: DataFrame com a lista nova
            
        Returns:
            DataFrame com o relatório de mudanças
        """
        logger.info("Iniciando comparação das listas...")
        
        # Criar conjuntos de REs
        old_res = set(old_df['RE'])
        new_res = set(new_df['RE'])
        
        # Identificar REs que entraram e saíram
        entered_res = new_res - old_res
        left_res = old_res - new_res
        
        # Criar lista para armazenar mudanças
        changes_list = []
        
        # Processar entradas
        for re in entered_res:
            new_row = new_df[new_df['RE'] == re].iloc[0]
            changes_list.append({
                'RE': re,
                'Nome': new_row['NOME'],
                'Mudança': 'ENTRADA',
                'Detalhes': f"Novo piloto: {new_row['NOME']} ({new_row['NOME DE GUERRA']})"
            })
        
        # Processar saídas
        for re in left_res:
            old_row = old_df[old_df['RE'] == re].iloc[0]
            changes_list.append({
                'RE': re,
                'Nome': old_row['NOME'],
                'Mudança': 'SAÍDA',
                'Detalhes': f"Piloto removido: {old_row['NOME']} ({old_row['NOME DE GUERRA']})"
            })
        
        # Processar mudanças para REs presentes em ambas as listas
        common_res = old_res.intersection(new_res)
        for re in common_res:
            old_row = old_df[old_df['RE'] == re].iloc[0]
            new_row = new_df[new_df['RE'] == re].iloc[0]
            
            changes = self._detect_changes(old_row, new_row)
            if changes:
                for change in changes:
                    changes_list.append({
                        'RE': re,
                        'Nome': new_row['NOME'],
                        'Mudança': f"MUDANÇA DE {change['campo']}",
                        'Detalhes': f"De: {change['valor_antigo']} Para: {change['valor_novo']}"
                    })
        
        # Criar DataFrame com as mudanças
        changes_df = pd.DataFrame(changes_list)
        
        logger.info(f"Comparação concluída! {len(changes_df)} mudanças detectadas.")
        return changes_df 

def normalize_text(text: str) -> str:
    """
    Normaliza o texto removendo acentos e caracteres especiais.
    """
    # Converter para string e remover espaços extras
    text = str(text).strip()
    
    # Remover acentos
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')
    
    # Converter para maiúsculas
    text = text.upper()
    
    return text

def compare_tables(base_df: pd.DataFrame, compare_df: pd.DataFrame) -> Dict:
    """
    Compara duas tabelas e retorna as diferenças encontradas.
    
    Args:
        base_df: DataFrame com a tabela base
        compare_df: DataFrame com a tabela para comparação
        
    Returns:
        Dicionário com as diferenças encontradas
    """
    try:
        # Garantir que os REs sejam strings
        base_df['RE'] = base_df['RE'].astype(str)
        compare_df['RE'] = compare_df['RE'].astype(str)
        
        logger.info(f"Total de registros na tabela base: {len(base_df)}")
        logger.info(f"Total de registros na tabela de comparação: {len(compare_df)}")
        
        # Criar conjuntos de REs
        base_res = set(base_df['RE'])
        compare_res = set(compare_df['RE'])
        
        # Identificar REs que entraram e saíram
        entered_res = compare_res - base_res
        left_res = base_res - compare_res
        
        logger.info(f"REs que entraram: {sorted(list(entered_res))}")
        logger.info(f"REs que saíram: {sorted(list(left_res))}")
        
        # Lista para armazenar diferenças
        differences = []
        
        # Processar entradas
        for re in entered_res:
            compare_row = compare_df[compare_df['RE'] == re].iloc[0]
            differences.append({
                'RE': re,
                'Nome': compare_row.get('NOME', 'N/A'),
                'Nome de Guerra': compare_row.get('NOME DE GUERRA', 'N/A'),
                'Função': compare_row.get('FUNÇÃO', 'N/A'),
                'Equipamento': compare_row.get('EQUIPAMENTO', 'N/A'),
                'Tipo': 'ENTRADA',
                'Detalhes': f"Novo piloto: RE {re}"
            })
        
        # Processar saídas
        for re in left_res:
            base_row = base_df[base_df['RE'] == re].iloc[0]
            differences.append({
                'RE': re,
                'Nome': base_row.get('NOME', 'N/A'),
                'Nome de Guerra': base_row.get('NOME DE GUERRA', 'N/A'),
                'Função': base_row.get('FUNÇÃO', 'N/A'),
                'Equipamento': base_row.get('EQUIPAMENTO', 'N/A'),
                'Tipo': 'SAÍDA',
                'Detalhes': f"Piloto removido: RE {re}"
            })
        
        # Processar mudanças para REs presentes em ambas as tabelas
        common_res = base_res.intersection(compare_res)
        logger.info(f"REs em comum: {sorted(list(common_res))}")
        
        for re in common_res:
            base_row = base_df[base_df['RE'] == re].iloc[0]
            compare_row = compare_df[compare_df['RE'] == re].iloc[0]
            
            # Comparar cada campo
            for column in ['FUNÇÃO', 'EQUIPAMENTO', 'NOME', 'NOME DE GUERRA', 'SENIORIDADE']:
                if column in base_row and column in compare_row:
                    base_value = normalize_text(base_row[column])
                    compare_value = normalize_text(compare_row[column])
                    
                    if base_value != compare_value:
                        logger.info(f"Diferença encontrada em {column} para RE {re}:")
                        logger.info(f"Base: {base_value}")
                        logger.info(f"Comparação: {compare_value}")
                        
                        differences.append({
                            'RE': re,
                            'Nome': compare_row.get('NOME', 'N/A'),
                            'Nome de Guerra': compare_row.get('NOME DE GUERRA', 'N/A'),
                            'Função': compare_row.get('FUNÇÃO', 'N/A'),
                            'Equipamento': compare_row.get('EQUIPAMENTO', 'N/A'),
                            'Tipo': f"MUDANÇA DE {column}",
                            'Detalhes': f"De: {base_row[column]} Para: {compare_row[column]}"
                        })
        
        logger.info(f"Total de diferenças encontradas: {len(differences)}")
        
        return {
            'differences': differences,
            'total_base': len(base_df),
            'total_compare': len(compare_df),
            'total_differences': len(differences),
            'entered': len(entered_res),
            'left': len(left_res)
        }
        
    except Exception as e:
        logger.error(f"Erro ao comparar tabelas: {str(e)}")
        raise 