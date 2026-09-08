# controlWP
Streamlit app to manage WordPress posts, pages, and media. Features advanced publishing, draft/live editing, and site maintenance checks. Uses beautifulsoup4/lxml to bypass default API limits for draft retrieval. Executable setup based on my other public repos.

# 🌐 WordPress Advanced Manager (v3) / Gestor Avançado de WordPress (v3)

[Português](#português) | [English](#english)

---

## Português

Uma aplicação robusta em Python desenvolvida com **Streamlit** para gerir e publicar conteúdos em sites WordPress. Esta versão (v3) é a mais completa, utilizando autenticação por utilizador, palavra-passe e cookies, permitindo um controlo total sobre posts, páginas e ficheiros multimédia.

### Funcionalidades
* **Gestão Total de Conteúdos:** Visualização e listagem de posts, páginas e ficheiros de media.
* **Métricas de Publicação:** Consulta estatística do número de publicações efetuadas por dia.
* **Criação Avançada de Posts:** Criação de artigos com definição de imagem de fundo (destaque), título, conteúdo e **atribuição de categorias**. Suporta o upload de ficheiros e a inserção dinâmica dos links gerados diretamente no corpo do texto.
* **Modos de Publicação:** Permite publicar diretamente ou guardar como rascunho.
* **Edição Flexível:** Permite editar e alterar as categorias ou o estado de qualquer post existente entre "Publicado" ou "Rascunho".
* **Controlo de Infraestrutura:** Verificação em tempo real se o site WordPress se encontra em modo de manutenção.
* **Acesso Avançado a Rascunhos:** Integração especial com os pacotes `beautifulsoup4` e `lxml` para contornar as limitações nativas da API do WordPress, permitindo extrair e listar rascunhos sem necessidade de permissões administrativas complexas ou outro tipo de autenticação restrita.

### Estrutura do Projeto
* `app.py`: Código principal da aplicação Streamlit (v3).
* `run_app.py`: Script de bootstrap/inicialização para o executável.
* `run_app.spec`: Ficheiro de configuração e especificação do PyInstaller.
* `requirements.txt`: Lista de dependências (incluindo `beautifulsoup4` e `lxml`).

### Como Executar Localmente
1. Crie e ative o seu ambiente virtual:
   ```bash
   python -m venv env
   # No Windows: .\env\Scripts\activate
   # No macOS/Linux: source env/bin/activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie a aplicação:
   ```bash
   streamlit run app.py
   ```

### Como Criar o Executável
A configuração do ficheiro `run_app.spec` e do script `run_app.py` foi estruturada utilizando **exemplos de referência testados noutros repositórios públicos do meu perfil do GitHub**. Para compilar o projeto com o PyInstaller, execute:
```bash
pyinstaller --clean run_app.spec
```
O executável final independente será gerado dentro da pasta `dist/`.

---

## English

A robust Python application built with **Streamlit** to manage and publish content on WordPress websites. This release (v3) is the most complete version, utilizing user, password, and cookie authentication to provide comprehensive control over posts, pages, and media files.

### Features
* **Comprehensive Content Management:** View and list website posts, pages, and media gallery items.
* **Publishing Metrics:** Check and monitor the total number of posts published per day.
* **Advanced Post Creation:** Create new posts with featured background images, titles, body content, and **assigned categories**. Supports file uploads with dynamic link injection into the post content.
* **Flexible Publishing:** Save articles directly as drafts or publish them live immediately.
* **Post Editing:** Modify and change the categories or status of existing posts at any time between "Published" and "Draft".
* **Maintenance Status Check:** Instantly verify whether the target WordPress site is currently in maintenance mode.
* **Advanced Draft Extraction:** Special integration using `beautifulsoup4` and `lxml` packages to bypass default WordPress API restrictions, enabling seamless listing and retrieval of draft posts without demanding complex elevated administrative permissions.

### Project Structure
* `app.py`: Main Streamlit application source code (v3).
* `run_app.py`: Bootstrap/entry-point script for the standalone executable.
* `run_app.spec`: PyInstaller configuration and specification file.
* `requirements.txt`: Python environment dependency list (including `beautifulsoup4` and `lxml`).

### How to Run Locally
1. Create and activate your virtual environment:
   ```bash
   python -m venv env
   # On Windows: .\env\Scripts\activate
   # On macOS/Linux: source env/bin/activate
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   streamlit run app.py
   ```

### How to Build the Executable
The setup for both the `run_app.spec` configuration file and the `run_app.py` bootstrap script was modeled after **existing reference templates from my other public GitHub repositories**. To compile the standalone executable using PyInstaller, run:
```bash
pyinstaller --clean run_app.spec
```
The final standalone bundle will be available inside the `dist/` directory.

