import streamlit as st
import pdfplumber
import pandas as pd

st.set_page_config(
    page_title="Comparador de Listas de Senioridade",
    page_icon="📄",
    layout="wide"
)

def extract_table_from_pdf(pdf_file) -> pd.DataFrame:
    """
    Extrai a tabela de um arquivo PDF, ignorando cabeçalho e rodapé.
    """
    try:
        all_tables = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                # Extrai tabelas da página
                tables = page.extract_tables()
                if tables:
                    # Pega a primeira tabela de cada página
                    table = tables[0]
                    # Converte para DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])  # Primeira linha como cabeçalho
                    all_tables.append(df)
        
        if not all_tables:
            raise ValueError("Nenhuma tabela encontrada no PDF")
        
        # Combina todas as tabelas
        final_df = pd.concat(all_tables, ignore_index=True)
        
        # Limpa os dados
        final_df = clean_dataframe(final_df)
        
        return final_df
        
    except Exception as e:
        st.error(f"Erro ao extrair tabela do PDF: {str(e)}")
        raise

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e padroniza o DataFrame.
    """
    # Remove linhas vazias
    df = df.dropna(how='all')
    
    # Remove espaços em branco
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
    
    return df

def compare_lists(old_df: pd.DataFrame, new_df: pd.DataFrame) -> dict:
    """
    Compara duas listas de senioridade e retorna as mudanças.
    """
    # Garante que a coluna RE existe
    if 'RE' not in old_df.columns or 'RE' not in new_df.columns:
        raise ValueError("A coluna 'RE' não foi encontrada em uma ou ambas as listas")
    
    # Converte RE para string para comparação
    old_df['RE'] = old_df['RE'].astype(str)
    new_df['RE'] = new_df['RE'].astype(str)
    
    # Encontra entradas e saídas
    old_res = set(old_df['RE'])
    new_res = set(new_df['RE'])
    
    # Pessoas que entraram (estão na nova lista mas não na antiga)
    entries = new_df[new_df['RE'].isin(new_res - old_res)]
    
    # Pessoas que saíram (estão na lista antiga mas não na nova)
    exits = old_df[old_df['RE'].isin(old_res - new_res)]
    
    return {
        'entradas': entries,
        'saidas': exits,
        'total_antigo': len(old_df),
        'total_novo': len(new_df),
        'total_entradas': len(entries),
        'total_saidas': len(exits)
    }

def analyze_re_changes(re: str, old_df: pd.DataFrame, new_df: pd.DataFrame) -> dict:
    """
    Analisa as mudanças específicas de um RE entre as listas.
    """
    # Converte RE para string
    re = str(re)
    
    # Busca o RE nas duas listas
    old_info = old_df[old_df['RE'] == re]
    new_info = new_df[new_df['RE'] == re]
    
    if old_info.empty and new_info.empty:
        return {
            'status': 'not_found',
            'message': 'RE não encontrado em nenhuma das listas'
        }
    
    if old_info.empty:
        return {
            'status': 'new_entry',
            'message': 'RE encontrado apenas na lista nova',
            'data': new_info.iloc[0].to_dict()
        }
    
    if new_info.empty:
        return {
            'status': 'exit',
            'message': 'RE encontrado apenas na lista antiga',
            'data': old_info.iloc[0].to_dict()
        }
    
    # Se encontrou em ambas as listas, compara as mudanças
    old_row = old_info.iloc[0]
    new_row = new_info.iloc[0]
    
    changes = []
    
    # Verifica mudanças em cada coluna
    for col in old_df.columns:
        if old_row[col] != new_row[col]:
            changes.append({
                'campo': col,
                'valor_antigo': old_row[col],
                'valor_novo': new_row[col]
            })
    
    return {
        'status': 'changed',
        'message': 'RE encontrado em ambas as listas com mudanças',
        'data': {
            'antigo': old_row.to_dict(),
            'novo': new_row.to_dict(),
            'mudancas': changes
        }
    }

def main():
    st.title("📄 Comparador de Listas de Senioridade")
    
    st.markdown("""
    Este aplicativo compara duas listas de senioridade e identifica quem entrou e quem saiu.
    Faça upload dos arquivos PDF das listas antiga e nova para ver as mudanças.
    """)
    
    # Seção de busca por RE
    st.subheader("🔍 Buscar por RE")
    re_input = st.text_input("Digite o RE para ver as mudanças específicas:")
    
    # Upload dos arquivos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Lista Antiga")
        old_file = st.file_uploader("Upload da lista antiga (PDF)", type=['pdf'])
    
    with col2:
        st.subheader("Lista Nova")
        new_file = st.file_uploader("Upload da lista nova (PDF)", type=['pdf'])
    
    # Botão para executar a análise
    if old_file is not None and new_file is not None:
        execute_button = st.button("🔍 Executar Análise", type="primary")
        
        if execute_button:
            try:
                # Extrai as tabelas dos PDFs
                with st.spinner("Processando as listas..."):
                    old_df = extract_table_from_pdf(old_file)
                    new_df = extract_table_from_pdf(new_file)
                    
                    # Compara as listas
                    comparison = compare_lists(old_df, new_df)
                    
                    # Se houver um RE para buscar, analisa as mudanças
                    if re_input:
                        changes = analyze_re_changes(re_input, old_df, new_df)
                        
                        st.markdown("### 📊 Análise do RE")
                        if changes['status'] == 'not_found':
                            st.warning(changes['message'])
                        elif changes['status'] == 'new_entry':
                            st.success(f"Novo na lista! Dados: {changes['data']}")
                        elif changes['status'] == 'exit':
                            st.error(f"Saiu da lista. Dados: {changes['data']}")
                        else:  # changed
                            st.info("Mudanças encontradas:")
                            
                            # Mostra as mudanças em um formato mais amigável
                            for change in changes['data']['mudancas']:
                                st.write(f"**{change['campo']}**:")
                                st.write(f"- Antigo: {change['valor_antigo']}")
                                st.write(f"- Novo: {change['valor_novo']}")
                                st.write("---")
                
                # Mostra estatísticas gerais
                st.markdown("### 📈 Estatísticas Gerais")
                st.success("Processamento concluído!")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total na Lista Antiga", comparison['total_antigo'])
                with col2:
                    st.metric("Total na Lista Nova", comparison['total_novo'])
                with col3:
                    st.metric("Entradas", comparison['total_entradas'])
                with col4:
                    st.metric("Saídas", comparison['total_saidas'])
                
                # Mostra as entradas
                if not comparison['entradas'].empty:
                    st.subheader("Pessoas que Entraram")
                    st.dataframe(comparison['entradas'])
                    
                    # Botão para download das entradas
                    csv_entries = comparison['entradas'].to_csv(index=False)
                    st.download_button(
                        label="Baixar Lista de Entradas (CSV)",
                        data=csv_entries,
                        file_name="entradas.csv",
                        mime="text/csv"
                    )
                
                # Mostra as saídas
                if not comparison['saidas'].empty:
                    st.subheader("Pessoas que Saíram")
                    st.dataframe(comparison['saidas'])
                    
                    # Botão para download das saídas
                    csv_exits = comparison['saidas'].to_csv(index=False)
                    st.download_button(
                        label="Baixar Lista de Saídas (CSV)",
                        data=csv_exits,
                        file_name="saidas.csv",
                        mime="text/csv"
                    )
                
            except Exception as e:
                st.error(f"Erro durante o processamento: {str(e)}")

if __name__ == "__main__":
    main() 