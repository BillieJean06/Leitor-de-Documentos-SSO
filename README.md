# Leitor de Documentos SSO (PCMSO e PGR) 📄➡️📊

Um aplicativo desktop com interface gráfica (GUI) construído em Python que automatiza a extração de dados tabulares de arquivos PDF de **PCMSO** (Programa de Controle Médico de Saúde Ocupacional) e **PGR** (Programa de Gerenciamento de Riscos), exportando-os de forma organizada para planilhas do Excel.

## 🎯 Funcionalidades

- **Interface Visual Amigável:** Carregue um PDF e visualize todas as páginas renderizadas como miniaturas.
- **Seleção Flexível:** Escolha apenas as páginas relevantes (que contêm as tabelas) para processar.
- **Suporte Multi-Documento (SSO):**
  - **PCMSO:** Extração de tabelas contendo "GHE" (Grupo Homogêneo de Exposição), "Riscos" e "Exames".
  - **PGR:** Identificação automática do layout das tabelas de riscos (Ficha de Setor/Função, Tabela Clássica ou Ficha de Cargo) e estruturação dos respectivos dados.
- **Tecnologia OCR Integrada:** Permite aplicar OCR (Reconhecimento Óptico de Caracteres) diretamente em PDFs escaneados ou baseados em imagens, tornando o texto legível para a extração.
- **Exportação para Excel:** Organiza e salva os dados estruturados diretamente em um arquivo `.xlsx` com colunas padronizadas.

## 🛠️ Tecnologias Utilizadas

- **[PyQt6](https://pypi.org/project/PyQt6/):** Interface gráfica moderna para interação com o usuário.
- **[pdfplumber](https://pypi.org/project/pdfplumber/):** Extração precisa de tabelas e textos estruturados.
- **[PyMuPDF (fitz)](https://pypi.org/project/PyMuPDF/):** Renderização rápida das páginas do PDF para visualização.
- **[Pandas](https://pandas.pydata.org/):** Estruturação e tratamento de dados tabulares.
- **[OpenPyXL](https://openpyxl.readthedocs.io/en/stable/):** Geração de planilhas nativas do Excel.
- **[OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF):** Ferramenta robusta para aplicação de OCR no documento.

## 🚀 Como Instalar e Rodar (Linux / Ubuntu / Mint)

### Pré-requisitos do Sistema
Certifique-se de ter o Python 3, gerenciador de pacotes (`pip`), suporte a ambientes virtuais (`venv`) e as dependências de sistema (para a interface do PyQt6 e o motor de OCR) instalados:

Abra seu terminal e execute:
```bash
sudo apt update
sudo apt install python3-pip python3-venv libxcb-cursor0 ocrmypdf tesseract-ocr-por -y
```

### Configurando o Projeto
1. Clone este repositório ou baixe os arquivos.
2. Navegue até a pasta do projeto no terminal:
   ```bash
   cd caminho/para/leitor-de-pcmso
   ```
3. Crie e ative um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Instale as dependências Python necessárias:
   ```bash
   pip install -r requirements.txt
   ```

### Executando o Aplicativo
Com o ambiente virtual ativado, execute:
```bash
python3 main.py
```

## 📖 Como Usar

1. Na janela do aplicativo, selecione o tipo de documento que deseja processar (**PCMSO** ou **PGR**).
2. Clique em **"Carregar PDF"** e escolha o arquivo.
3. Se o PDF for um escaneamento (não contiver texto selecionável), clique no botão **"Aplicar OCR"** e aguarde a conclusão do processo.
4. O aplicativo exibirá miniaturas das páginas do documento. Marque a caixinha de seleção correspondente às páginas contendo as tabelas desejadas.
5. Clique em **"Extrair Selecionados e Exportar"**.
6. Escolha o nome e o local para salvar sua planilha `.xlsx`.

## 🤝 Contribuições
Contribuições são sempre bem-vindas! Se você tiver melhorias nos algoritmos de extração para novos formatos de relatórios, sinta-se à vontade para abrir uma Issue ou enviar um Pull Request.

---
*Desenvolvido em Python*
