import pandas as pd

def export_to_excel(data, output_path):
    """
    Exporta os dados extraídos para uma planilha Excel.
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
            
        else:
            # É PCMSO
            cols = ["GHE", "Riscos", "Exames", "Página"]
            cols = [col for col in cols if col in df.columns]
            df = df[cols]
            
        df.to_excel(output_path, index=False, engine='openpyxl')
        return True, f"Arquivo exportado com sucesso para: {output_path}"
    except Exception as e:
        return False, f"Erro ao exportar: {str(e)}"
