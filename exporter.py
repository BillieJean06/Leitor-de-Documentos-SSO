import pandas as pd

def _split_multiline_rows(df, columns_to_split):
    """
    Para colunas que contêm múltiplos valores separados por '\n',
    expande cada valor em uma linha própria, repetindo os dados das outras colunas.
    Isso garante compatibilidade entre LibreOffice e Excel no Windows.
    """
    col = columns_to_split[0]
    
    if col not in df.columns:
        return df
    
    # Divide os valores de texto pelo '\n', criando uma lista por célula
    df = df.copy()
    df[col] = df[col].astype(str).str.split('\n')
    
    # Expande as listas em linhas separadas
    df = df.explode(col)
    
    # Remove linhas vazias que possam ter surgido
    df[col] = df[col].str.strip()
    df = df[df[col] != '']
    df = df[df[col] != 'nan']
    
    df = df.reset_index(drop=True)
    
    # Processa a próxima coluna recursivamente, se houver
    if len(columns_to_split) > 1:
        return _split_multiline_rows(df, columns_to_split[1:])
    
    return df

def export_to_excel(data, output_path):
    """
    Exporta os dados extraídos para uma planilha Excel.
    Campos com múltiplos valores (separados por quebras de linha no PDF) são
    expandidos em linhas individuais para garantir compatibilidade com Excel no Windows.
    """
    if not data:
        return False, "Nenhum dado para exportar."
    
    try:
        df = pd.DataFrame(data)
        
        # O DataFrame pode vir com múltiplas colunas diferentes caso o layout do PGR varie.
        # Vamos reorganizar as colunas conhecidas para a esquerda para manter uma ordem bonita, 
        # e as outras colunas que forem dinâmicas do Layout 2 ficarão na direita.
        if "Layout" in df.columns or "Função" in df.columns or "Cargo/Função" in df.columns:
            # É PGR
            preferred_order = [
                "Página", 
                "Layout",
                "Setor", 
                "Ambiente Avaliado", 
                "Ambiente Avaliado Ponto de Medição",
                "Cargo/Função", 
                "Função", 
                "Descrição do Setor", 
                "Descrição da Função", 
                "Descrição das atividades", 
                "GHE", 
                "Perigo Identificado", 
                "Agente", 
                "Risco", 
                "Tipo/Grupo", 
                "Nível de Risco", 
                "Nível Risco Ocupacional",
                "Probabilidade", 
                "Severidade", 
                "eSocial"
            ]
            
            existing_preferred = [col for col in preferred_order if col in df.columns]
            other_cols = [col for col in df.columns if col not in preferred_order]
            df = df[existing_preferred + other_cols]
            
            # Expande colunas de texto livre do PGR que podem ter múltiplas linhas
            cols_to_expand = [c for c in ["Agente", "Risco", "Perigo Identificado"] if c in df.columns]
            if cols_to_expand:
                df = _split_multiline_rows(df, cols_to_expand)
            
        else:
            # É PCMSO
            cols = ["GHE", "Riscos", "Exames", "Página"]
            cols = [col for col in cols if col in df.columns]
            df = df[cols]
            
            # Expande a coluna de Exames: cada exame fica em sua própria linha,
            # repetindo o GHE e Riscos correspondentes.
            # Isso garante que a saída seja igual em LibreOffice e Excel/Windows.
            cols_to_expand = [c for c in ["Exames", "Riscos"] if c in df.columns]
            if cols_to_expand:
                df = _split_multiline_rows(df, cols_to_expand)
            
            # Reordena as colunas finais
            final_cols = [c for c in ["GHE", "Riscos", "Exames", "Página"] if c in df.columns]
            df = df[final_cols]
            
        df.to_excel(output_path, index=False, engine='openpyxl')
        return True, f"Arquivo exportado com sucesso para: {output_path}"
    except Exception as e:
        return False, f"Erro ao exportar: {str(e)}"
