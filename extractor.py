import pdfplumber
import re

def process_pdf(file_path, selected_pages, doc_type="pcmso"):
    """
    Lê o PDF usando pdfplumber e tenta extrair tabelas das páginas selecionadas.
    O comportamento muda dependendo do doc_type (pcmso ou pgr).
    """
    extracted_data = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num in selected_pages:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    
                    # Extrair tabelas da página (podem haver múltiplas por página)
                    tables = page.extract_tables()
                    
                    if not tables:
                        continue
                        
                    if doc_type == "pcmso":
                        extracted_data.extend(extract_pcmso(tables, page_num))
                    elif doc_type == "pgr":
                        layout_type = identify_pgr_layout(tables)
                        
                        if layout_type == 1:
                            extracted_data.extend(extract_pgr_type1(tables, page_num))
                        elif layout_type == 2:
                            extracted_data.extend(extract_pgr_type2(tables, page_num))
                        elif layout_type == 3:
                            extracted_data.extend(extract_pgr_type3(tables, page_num))
                        else:
                            extracted_data.extend(extract_pgr_type1(tables, page_num))
                        
    except Exception as e:
        print(f"Erro ao processar PDF: {e}")

    return extracted_data

def identify_pgr_layout(tables):
    for table in tables:
        for row in table:
            clean_row = [str(cell).strip().upper() if cell is not None else "" for cell in row]
            for cell in clean_row:
                if "ANÁLISE PRELIMINAR" in cell or "AMBIENTE AVALIADO" in cell:
                    return 2
                if "CARGO/FUNÇÃO" in cell or "AGENTE NOCIVO" in cell:
                    return 3
    return 1 # Fallback para o layout 1 (Inventário Vertical)

def extract_pcmso(tables, page_num):
    data = []
    for table in tables:
        idx_ghe = -1
        idx_riscos = -1
        idx_exames = -1
        
        for row in table:
            clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
            
            # 1. Identificar o cabeçalho
            if idx_ghe == -1 and idx_riscos == -1 and idx_exames == -1:
                for i, cell_text in enumerate(clean_row):
                    text_upper = cell_text.upper()
                    
                    if idx_ghe == -1 and ("GHE" == text_upper.strip() or "GHE\n" in text_upper or "GRUPO HOMOGÊNEO" in text_upper):
                        idx_ghe = i
                    elif idx_riscos == -1 and ("RISCO" in text_upper or "PERIGO" in text_upper):
                        idx_riscos = i
                    elif idx_exames == -1 and ("EXAME" in text_upper or "MÉDICO" in text_upper):
                        idx_exames = i
                        
                for i, cell_text in enumerate(clean_row):
                    text_upper = cell_text.upper()
                    if idx_ghe == -1 and "GHE" in text_upper and i != idx_riscos and i != idx_exames:
                        idx_ghe = i
                
                if idx_ghe != -1 or idx_riscos != -1 or idx_exames != -1:
                    continue
                    
            # 2. Extrair dados baseados no cabeçalho
            if idx_ghe != -1 or idx_riscos != -1 or idx_exames != -1:
                ghe_val = clean_row[idx_ghe] if idx_ghe != -1 and idx_ghe < len(clean_row) else ""
                riscos_val = clean_row[idx_riscos] if idx_riscos != -1 and idx_riscos < len(clean_row) else ""
                exames_val = clean_row[idx_exames] if idx_exames != -1 and idx_exames < len(clean_row) else ""
                
                if ghe_val or riscos_val or exames_val:
                    data.append({
                        "Página": page_num + 1,
                        "GHE": ghe_val,
                        "Riscos": riscos_val,
                        "Exames": exames_val
                    })
    return data

def extract_pgr_type1(tables, page_num):
    data = []
    for table in tables:
        current_setor = ""
        current_desc_setor = ""
        current_funcoes = []
        current_ghe = ""
        last_key = ""
        
        for row in table:
            clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
            if not any(clean_row):
                continue
                
            is_single_cell = len(clean_row) == 1 or (len(clean_row) > 1 and not any(clean_row[1:]))
            
            if is_single_cell:
                text = clean_row[0]
                text_upper = text.upper()
                
                if text_upper.startswith("SETOR:"):
                    current_setor = text[6:].strip()
                    current_funcoes = []
                    current_desc_setor = ""
                    last_key = "setor"
                elif last_key == "setor" and text_upper.startswith("COBERTURA:"):
                    current_desc_setor = text.strip()
                    last_key = "desc_setor"
                elif text_upper.startswith("FUNÇÃO:"):
                    funcao_name = text[7:].split("- CBO")[0].strip()
                    current_funcoes.append({"funcao": funcao_name, "desc": ""})
                    last_key = "funcao"
                elif last_key == "funcao" and not text_upper.startswith("GHE:"):
                    if current_funcoes:
                        current_funcoes[-1]["desc"] += text.strip() + " "
                elif text_upper.startswith("GHE:"):
                    current_ghe = text[4:].strip()
                    last_key = "ghe"
            
            else:
                agente = ""
                risco = ""
                esocial = ""
                
                for cell in clean_row:
                    c_upper = cell.upper()
                    if c_upper.startswith("AGENTE:"):
                        agente = cell[7:].strip()
                    elif c_upper.startswith("RISCO:"):
                        risco = cell[6:].strip()
                    elif c_upper.startswith("ESOCIAL:"):
                        esocial = cell[8:].strip()
                
                if agente or risco or esocial:
                    if not current_funcoes:
                        data.append({
                            "Página": page_num + 1,
                            "Layout": "Formato Ficha 1",
                            "Setor": current_setor,
                            "Descrição do Setor": current_desc_setor,
                            "Função": "",
                            "Descrição da Função": "",
                            "GHE": current_ghe,
                            "Agente": agente,
                            "Risco": risco,
                            "eSocial": esocial
                        })
                    else:
                        for f in current_funcoes:
                            data.append({
                                "Página": page_num + 1,
                                "Layout": "Formato Ficha 1",
                                "Setor": current_setor,
                                "Descrição do Setor": current_desc_setor,
                                "Função": f["funcao"],
                                "Descrição da Função": f["desc"].strip(),
                                "GHE": current_ghe,
                                "Agente": agente,
                                "Risco": risco,
                                "eSocial": esocial
                            })
    return data

def extract_pgr_type2(tables, page_num):
    data = []
    for table in tables:
        headers = []
        for row in table:
            clean_row = [str(cell).strip().replace('\n', ' ') if cell is not None else "" for cell in row]
            if len([c for c in clean_row if c]) > 2:
                headers = clean_row
                break
                
        if not headers:
            continue
            
        for row in table:
            clean_row = [str(cell).strip().replace('\n', ' ') if cell is not None else "" for cell in row]
            if clean_row == headers or len([c for c in clean_row if c]) <= 1:
                continue
                
            row_data = {"Página": page_num + 1, "Layout": "Formato Tabela Clássica"}
            for i, header in enumerate(headers):
                if header:
                    val = clean_row[i] if i < len(clean_row) else ""
                    row_data[header] = val
            
            if len(row_data) > 2:
                data.append(row_data)
                
    return data

def extract_pgr_type3(tables, page_num):
    data = []
    current_cargo = ""
    current_desc = ""
    current_row_data = None
    
    for table in tables:
        for row in table:
            clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
            if len(clean_row) >= 2:
                key = clean_row[0].upper().replace('\n', ' ')
                val = clean_row[1].replace('\n', ' ')
                
                if "CARGO" in key and "FUNÇÃO" in key:
                    current_cargo = val
                    current_desc = ""
                elif "DESCRIÇÃO DAS ATIVIDADES" in key:
                    current_desc = val
                elif "AGENTE NOCIVO" in key:
                    current_row_data = {
                        "Página": page_num + 1,
                        "Layout": "Formato Ficha de Cargo",
                        "Cargo/Função": current_cargo,
                        "Descrição das atividades": current_desc,
                        "Agente": val,
                        "Tipo/Grupo": "",
                        "Nível de Risco": "",
                        "Probabilidade": "",
                        "Severidade": ""
                    }
                    data.append(current_row_data)
                elif current_row_data is not None:
                    if "TIPO" in key or "GRUPO" in key:
                        current_row_data["Tipo/Grupo"] = val
                    elif "NÍVEL DE RISCO" in key:
                        current_row_data["Nível de Risco"] = val
                    elif "PROBABILIDADE" in key:
                        current_row_data["Probabilidade"] = val
                    elif "SEVERIDADE" in key:
                        current_row_data["Severidade"] = val
    return data
