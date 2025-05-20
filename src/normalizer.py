import pandas as pd
import re
from typing import Dict
import logging
import unicodedata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataNormalizer:
    """Classe responsável por normalizar e limpar os dados extraídos dos PDFs."""
    
    def __init__(self):
        self.column_mappings = {
            'FUNÇÃO': self._normalize_function,
            'EQUIPAMENTO': self._normalize_equipment,
            'NOME': self._normalize_name,
            'NOME DE GUERRA': self._normalize_callsign,
            'RE': self._normalize_re,
            'SENIORIDADE': self._normalize_seniority
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto removendo espaços extras e convertendo para maiúsculas."""
        if pd.isna(text):
            return ""
        return ' '.join(str(text).strip().upper().split())
    
    def _normalize_function(self, text: str) -> str:
        """Normaliza função do piloto."""
        return self._normalize_text(text)
    
    def _normalize_equipment(self, text: str) -> str:
        """Normaliza equipamento."""
        return self._normalize_text(text)
    
    def _normalize_name(self, text: str) -> str:
        """Normaliza nome completo."""
        return self._normalize_text(text)
    
    def _normalize_callsign(self, text: str) -> str:
        """Normaliza nome de guerra."""
        return self._normalize_text(text)
    
    def _normalize_re(self, text: str) -> str:
        """Normaliza número de registro (RE)."""
        if pd.isna(text):
            return ""
        # Remove caracteres não numéricos
        return re.sub(r'\D', '', str(text))
    
    def _normalize_seniority(self, text: str) -> str:
        """Normaliza senioridade."""
        if pd.isna(text):
            return ""
        # Remove caracteres não numéricos e converte para inteiro
        return str(int(re.sub(r'\D', '', str(text))))
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza todos os dados do DataFrame.
        
        Args:
            df: DataFrame com dados brutos
            
        Returns:
            DataFrame com dados normalizados
        """
        logger.info("Iniciando normalização dos dados...")
        
        # Criar cópia para não modificar o original
        normalized_df = df.copy()
        
        # Aplicar normalização para cada coluna
        for column, normalizer in self.column_mappings.items():
            if column in normalized_df.columns:
                normalized_df[column] = normalized_df[column].apply(normalizer)
        
        # Remover linhas duplicadas
        normalized_df = normalized_df.drop_duplicates()
        
        # Remover linhas com RE vazio
        normalized_df = normalized_df[normalized_df['RE'] != ""]
        
        logger.info("Normalização concluída!")
        return normalized_df 

def normalize_data(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Normaliza os dados do DataFrame de acordo com as configurações especificadas.
    
    Args:
        df: DataFrame com dados brutos
        config: Dicionário com configurações de normalização
        
    Returns:
        DataFrame com dados normalizados
    """
    try:
        # Criar cópia para não modificar o original
        normalized_df = df.copy()
        
        # Aplicar normalizações básicas
        for column in normalized_df.columns:
            # Converter para string e remover espaços extras
            normalized_df[column] = normalized_df[column].astype(str).str.strip()
            
            # Remover acentos se configurado
            if config.get('remove_accents', True):
                normalized_df[column] = normalized_df[column].apply(
                    lambda x: ''.join(c for c in unicodedata.normalize('NFD', x)
                                    if unicodedata.category(c) != 'Mn')
                )
            
            # Padronizar maiúsculas/minúsculas se configurado
            if config.get('standardize_case', True):
                normalized_df[column] = normalized_df[column].str.upper()
            
            # Remover caracteres especiais se configurado
            if config.get('remove_special_chars', True):
                normalized_df[column] = normalized_df[column].apply(
                    lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x)
                )
        
        # Remover linhas duplicadas
        normalized_df = normalized_df.drop_duplicates()
        
        # Remover linhas vazias
        normalized_df = normalized_df.replace('', pd.NA).dropna(how='all')
        
        return normalized_df
        
    except Exception as e:
        logger.error(f"Erro ao normalizar dados: {str(e)}")
        raise 