import pandas as pd
from datetime import datetime
import os
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Classe responsável por gerar relatórios das mudanças detectadas."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _generate_filename(self, prefix: str = "relatorio") -> str:
        """Gera nome do arquivo com timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}")
    
    def generate_excel_report(self, changes_df: pd.DataFrame) -> str:
        """
        Gera relatório em Excel com as mudanças detectadas.
        
        Args:
            changes_df: DataFrame com as mudanças detectadas
            
        Returns:
            Caminho do arquivo gerado
        """
        logger.info("Gerando relatório Excel...")
        
        # Gerar nome do arquivo
        filename = self._generate_filename() + ".xlsx"
        
        # Criar Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Escrever relatório principal
            changes_df.to_excel(writer, sheet_name='Mudanças', index=False)
            
            # Criar sumário
            summary = pd.DataFrame({
                'Tipo de Mudança': changes_df['Mudança'].value_counts().index,
                'Quantidade': changes_df['Mudança'].value_counts().values
            })
            summary.to_excel(writer, sheet_name='Sumário', index=False)
        
        logger.info(f"Relatório Excel gerado: {filename}")
        return filename
    
    def generate_csv_report(self, changes_df: pd.DataFrame) -> str:
        """
        Gera relatório em CSV com as mudanças detectadas.
        
        Args:
            changes_df: DataFrame com as mudanças detectadas
            
        Returns:
            Caminho do arquivo gerado
        """
        logger.info("Gerando relatório CSV...")
        
        # Gerar nome do arquivo
        filename = self._generate_filename() + ".csv"
        
        # Salvar CSV
        changes_df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        logger.info(f"Relatório CSV gerado: {filename}")
        return filename
    
    def generate_reports(self, changes_df: pd.DataFrame) -> dict:
        """
        Gera relatórios em múltiplos formatos.
        
        Args:
            changes_df: DataFrame com as mudanças detectadas
            
        Returns:
            Dicionário com os caminhos dos arquivos gerados
        """
        excel_file = self.generate_excel_report(changes_df)
        csv_file = self.generate_csv_report(changes_df)
        
        return {
            'excel': excel_file,
            'csv': csv_file
        }

def generate_report(comparison_results: Dict) -> str:
    """
    Gera um relatório HTML com os resultados da comparação.
    
    Args:
        comparison_results: Dicionário com os resultados da comparação
        
    Returns:
        String contendo o relatório em HTML
    """
    try:
        # Criar DataFrame com as diferenças
        differences_df = pd.DataFrame(comparison_results['differences'])
        
        # Gerar HTML
        html = f"""
        <html>
        <head>
            <title>Relatório de Comparação de Listas de Senioridade</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Comparação de Listas de Senioridade</h1>
            <p class="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            
            <div class="summary">
                <h2>Resumo</h2>
                <p>Total na Lista Base: {comparison_results['total_base']}</p>
                <p>Total na Lista de Comparação: {comparison_results['total_compare']}</p>
                <p>Total de Diferenças Encontradas: {comparison_results['total_differences']}</p>
            </div>
            
            <h2>Diferenças Detalhadas</h2>
            {differences_df.to_html(index=False) if not differences_df.empty else '<p>Nenhuma diferença encontrada.</p>'}
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        raise 