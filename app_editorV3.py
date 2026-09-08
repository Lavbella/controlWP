import os
import re
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import time

load_dotenv()

st.set_page_config(page_title="Editor de Conteúdo Avançado", layout="wide")

BASE_URL = os.getenv("APP_WORDPRESS_SITE_URL", "")
API_URL = os.getenv("APP_WORDPRESS_BASE_URL", "")
ENV_USER = os.getenv("WP_USER", "")
ENV_PASS = os.getenv("WP_PASS", "")

# Inicializar o estado da sessão na memória do Streamlit se ainda não existir
if "wp_session" not in st.session_state:
    st.session_state["wp_session"] = None
    st.session_state["wp_nonce"] = None
    st.session_state["wp_autenticado"] = False

@st.cache_resource
def iniciar_sessao_wp_funcionava_apenas_para_ver():
    session = requests.Session()
    payload = {
        "log": ENV_USER,
        "pwd": ENV_PASS,
        "wp-submit": "Log In",
        "redirect_to": f"{BASE_URL}/wp-admin/",
        "testcookie": "1"
    }
    try:
        login_response = session.post(f"{BASE_URL}/wp-login.php", data=payload, allow_redirects=True)
        cookies = session.cookies.get_dict()
        autenticado = any("wordpress_logged_in" in nome for nome in cookies.keys())
        
        if not autenticado:
            return None, None
        
        admin_page = session.get(f"{BASE_URL}/wp-admin/post-new.php")
        nonce_match = re.search(r'"wpRestNonce":"([^"]+)"', admin_page.text)
        nonce = nonce_match.group(1) if nonce_match else None
        return session, nonce
    except:
        return None, None


def iniciar_sessao_wp_funcionava_para_inserir():
    session = requests.Session()
    payload = {
        "log": ENV_USER,
        "pwd": ENV_PASS,
        "wp-submit": "Log In",
        "redirect_to": f"{BASE_URL}/wp-admin/",
        "testcookie": "1"
    }
    try:
        login_response = session.post(f"{BASE_URL}/wp-login.php", data=payload, allow_redirects=True)
        cookies = session.cookies.get_dict()
        autenticado = any("wordpress_logged_in" in nome for nome in cookies.keys())
        
        if not autenticado:
            return None, None
        
        # --- ALTERAÇÃO AQUI: Mudámos para o index.php (Painel Principal) ---
        admin_page = session.get(f"{BASE_URL}/wp-admin/index.php")
        
        # --- ALTERAÇÃO AQUI: Regex universal que apanha o nonce do objeto wpApiSettings ---
        nonce_match = re.search(r'"nonce":"([^"]+)"', admin_page.text)
        nonce = nonce_match.group(1) if nonce_match else None
        
        return session, nonce
    except:
        return None, None        

def iniciar_sessao_wp_obter_cookie_adm_paraver_drafts_sem_sucesso():
    session = requests.Session()
    payload = {
        "log": ENV_USER,
        "pwd": ENV_PASS,
        "wp-submit": "Log In",
        "redirect_to": f"{BASE_URL}/wp-admin/",
        "testcookie": "1"
    }
    try:
        login_response = session.post(f"{BASE_URL}/wp-login.php", data=payload, allow_redirects=True)
        cookies = session.cookies.get_dict()
        autenticado = any("wordpress_logged_in" in nome for nome in cookies.keys())
        
        if not autenticado:
            return None, None
        
        # Aceder à página de edição de posts onde o nonce da API REST é injetado obrigatoriamente
        admin_page = session.get(f"{BASE_URL}/wp-admin/edit.php")
        
        # Regex melhorada para capturar o nonce rest do script inline do WordPress
        nonce_match = re.search(r'"nonce":"([^"]+)"', admin_page.text)
        
        # Se não encontrar, tenta o padrão alternativo do Gutenberg
        if not nonce_match:
            nonce_match = re.search(r'"wpRestNonce":"([^"]+)"', admin_page.text)
            
        nonce = nonce_match.group(1) if nonce_match else None
        return session, nonce
    except:
        return None, None

def iniciar_sessao_wp():
    session = requests.Session()
    # Adicionar cabeçalhos de um browser real para evitar bloqueios de segurança do servidor
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    })
    
    payload = {
        "log": ENV_USER,
        "pwd": ENV_PASS,
        "wp-submit": "Log In",
        "redirect_to": f"{BASE_URL}/wp-admin/",
        "testcookie": "1"
    }
    try:
        login_response = session.post(f"{BASE_URL}/wp-login.php", data=payload, allow_redirects=True)
        cookies = session.cookies.get_dict()
        autenticado = any("wordpress_logged_in" in nome for nome in cookies.keys())
        
        if not autenticado:
            return None, None
            
        # Captura rápida de segurança para quando for fazer o POST
        admin_page = session.get(f"{BASE_URL}/wp-admin/index.php")
        nonce_match = re.search(r'"nonce":"([^"]+)"', admin_page.text)
        nonce = nonce_match.group(1) if nonce_match else None
        
        return session, nonce
    except:
        return None, None



@st.cache_data(ttl=60)
def obter_categorias(_session):
    try:
        res = _session.get(f"{API_URL}/wp/v2/categories", params={"per_page": 100})
        if res.status_code == 200:
            return {cat['name']: cat['id'] for cat in res.json()}
    except:
        pass
    return {"Geral": 1} # Fallback padrão do WP

@st.cache_data(ttl=30)  # Guarda a lista por 30 segundos antes de atualizar

def obter_ultimas_imagens(_session):
    try:
        # Procura os últimos 20 ficheiros do tipo imagem na biblioteca
        res = _session.get(f"{API_URL}/wp/v2/media", params={"per_page": 20, "media_type": "image"})
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

@st.cache_data(ttl=300)  # Guarda os dados em cache por 5 minutos para performance
def carregar_dados_wp():
    
    # Puxar Posts e Páginas (máximo de 100 itens para o exemplo)
    res_posts = session.get(f"{API_URL}/wp/v2/posts", params={"per_page": 100})
    res_pages = session.get(f"{API_URL}/wp/v2/pages", params={"per_page": 100})
    res_media = session.get(f"{API_URL}/wp/v2/media", params={"per_page": 100})
    
    df_posts = pd.json_normalize(res_posts.json()) if res_posts.status_code == 200 else pd.DataFrame()
    df_pages = pd.json_normalize(res_pages.json()) if res_pages.status_code == 200 else pd.DataFrame()
    df_media = pd.json_normalize(res_media.json()) if res_media.status_code == 200 else pd.DataFrame()
    
    return df_posts, df_pages, df_media

# session, nonce = iniciar_sessao_wp()

st.title("✍️ Publicar no WordPress")
    
aba_login, aba_criar, aba_editar, aba_dashboard = st.tabs(["🔐 Autenticação", "🆕 Configurar e Publicar Artigo", "✏️ Editar Artigo Existente", "📊 Dashboard de Conteúdo"])

# --- ABA: LOGIN COMPLETO ---
with aba_login:
    st.subheader("Autenticação no Painel WordPress")
    
    if st.session_state["wp_autenticado"]:
        st.success(f"✅ Já se encontra autenticado!")
        if st.button("🚪 Terminar Sessão (Logout)"):
            st.session_state["wp_session"] = None
            st.session_state["wp_nonce"] = None
            st.session_state["wp_autenticado"] = False
            st.rerun()
    else:
        st.info("Clique no botão abaixo para ligar a aplicação ao site.")
        
        if st.button("🔑 Iniciar Sessão"):
            with st.spinner("A efetuar login..."):
                # REUTILIZAÇÃO DA SUA FUNÇÃO EXISTENTE:
                sessao_obtida, nonce_obtido = iniciar_sessao_wp()
                
                if sessao_obtida:
                    # Guardar os dados devolvidos na memória do Streamlit
                    st.session_state["wp_session"] = sessao_obtida
                    st.session_state["wp_nonce"] = nonce_obtido
                    st.session_state["wp_autenticado"] = True
                    
                    st.success("🎉 Sessão guardada com sucesso! Já pode navegar pelas restantes abas.")
                    st.rerun()
                else:
                    st.error("❌ Falha na autenticação. Verifique as credenciais no ficheiro .env ou bloqueios do servidor.")

# --- ABA: CRIAR ARTIGO ---
with aba_criar:

    st.subheader("⚙️ Criar Novo Artigo")

    if not st.session_state["wp_autenticado"]:
        st.warning("⚠️ Por favor, efetue o login na aba 'Autenticação' primeiro para poder gerir artigos.")
        st.stop()
    else:
        # Define as variáveis locais que o seu código antigo já espera usar
        session = st.session_state["wp_session"]
        headers = {"X-WP-Nonce": st.session_state["wp_nonce"]} if st.session_state["wp_nonce"] else {}

    # Carregar categorias dinamicamente do WordPress
    categorias_disponiveis = obter_categorias(session)
    
    # Duas colunas para organizar o ecrã
    col_principal, col_opcoes = st.columns([2, 1])
    
    with col_opcoes:
        st.subheader("📎 Gestor de Ficheiros e Media")
        st.info("Arraste múltiplos ficheiros. Depois de carregados, mude o nome se desejar e copie o código.")
        
        # 1. Permitir múltiplos ficheiros ao mesmo tempo
        uploaded_files = st.file_uploader(
            "Escolha um ou mais ficheiros (Imagens, PDFs, Docs)", 
            type=["png", "jpg", "jpeg", "pdf", "docx", "xlsx"],
            accept_multiple_files=True
        )
        
        # Inicializar uma lista no histórico da sessão para guardar os ficheiros carregados com sucesso
        if "ficheiros_carregados_wp" not in st.session_state:
            st.session_state["ficheiros_carregados_wp"] = []
            
        # Botão para processar o lote de uploads
        if uploaded_files:
            if st.button("📤 Enviar todos para o WordPress"):
                with st.spinner(f"A enviar {len(uploaded_files)} ficheiro(s)..."):
                    for f in uploaded_files:
                        # Evitar re-enviar o mesmo ficheiro se já foi processado nesta sessão
                        if any(item['original_name'] == f.name for item in st.session_state["ficheiros_carregados_wp"]):
                            continue
                            
                        media_headers = headers.copy()
                        media_headers["Content-Disposition"] = f'attachment; filename="{f.name}"'
                        media_headers["Content-Type"] = f.type
                        
                        res_media = session.post(f"{API_URL}/wp/v2/media", data=f.getvalue(), headers=media_headers)
                        
                        if res_media.status_code == 201:
                            media_data = res_media.json()
                            # Guardar os dados essenciais recebidos do WordPress
                            st.session_state["ficheiros_carregados_wp"].append({
                                "id": media_data.get("id"),
                                "original_name": f.name,
                                "custom_name": f.name.split('.')[0].replace('_', ' ').title(), # Nome sugerido limpo
                                "url": media_data.get("source_url"),
                                "type": media_data.get("media_type")
                            })
                            # Se for imagem, define como a última imagem para uso fácil
                            if media_data.get("media_type") == "image":
                                st.session_state["ultima_imagem_id"] = media_data.get("id")
                    st.success("✅ Processamento de uploads concluído!")

        # 2. Gerar a lista dinâmica com os ficheiros enviados para edição de nomes em lote
        if st.session_state["ficheiros_carregados_wp"]:
            st.markdown("##### 📁 Ficheiros prontos:")
            
            # --- BOTÃO PARA INSERIR TODOS EM LOTE ---
            if st.button("➕ Inserir TODOS no fim do texto", type="secondary", use_container_width=True):
                blocos_html = []
                for item in st.session_state["ficheiros_carregados_wp"]:
                    if item["type"] == "image":
                        blocos_html.append(f'<img src="{item["url"]}" alt="{item["custom_name"]}" class="aligncenter" />')
                    else:
                        blocos_html.append(f'<p><a href="{item["url"]}" target="_blank" rel="noopener">{item["custom_name"]}</a></p>')
                
                st.session_state["conteudo_artigo"] += "\n\n" + "\n".join(blocos_html)
                st.rerun()
            
            # Criar uma interface limpa para cada ficheiro carregado
            for idx, item in enumerate(st.session_state["ficheiros_carregados_wp"]):
                with st.expander(f"📄 {item['original_name']}", expanded=True):
                    # Permitir alterar o nome de exibição em tempo real
                    novo_nome = st.text_input(
                        f"Nome do link / Alt text", 
                        value=item["custom_name"], 
                        key=f"name_{item['id']}_{idx}"
                    )
                    st.session_state["ficheiros_carregados_wp"][idx]["custom_name"] = novo_nome
                    
                    # Gerar o código final dinâmico
                    if item["type"] == "image":
                        tag_codigo = f'<img src="{item["url"]}" alt="{novo_nome}" class="aligncenter" />'
                    else:
                        tag_codigo = f'<a href="{item["url"]}" target="_blank" rel="noopener">{novo_nome}</a>'
                        
                    st.text_area("📋 Código para o texto:", value=tag_codigo, height=65, key=f"code_{item['id']}_{idx}")
                    
                    if st.button("➕ Inserir no fim do texto", key=f"btn_{item['id']}_{idx}"):
                        st.session_state["conteudo_artigo"] += f"\n\n{tag_codigo}"
                        st.rerun()
            
            if st.button("🗑️ Limpar Lista de Ficheiros"):
                st.session_state["ficheiros_carregados_wp"] = []
                st.rerun()

        
        # --- GALERIA E IMAGEM DE DESTAQUE ---
        st.markdown("---")
        st.subheader("🖼️ Biblioteca de Imagens Existentes")
        
        if st.button("🔄 Atualizar Galeria WP"):
            st.cache_data.clear()
            st.rerun()
            
        imagens_wp = obter_ultimas_imagens(session)
        id_imagem_final = None
        usar_imagem_destaque = False
        
        if imagens_wp:
            opcoes_galeria = {"[Nenhuma imagem selecionada]": None}
            for img in imagens_wp:
                titulo_img = img.get("title", {}).get("rendered", "")
                if not titulo_img:
                    titulo_img = img.get("source_url", "").split("/")[-1]
                label = f"ID: {img['id']} - {titulo_img[:25]}"
                opcoes_galeria[label] = img
            
            escolha_galeria = st.selectbox("Selecione uma imagem da sua biblioteca WP:", options=list(opcoes_galeria.keys()))
            imagem_dados = opcoes_galeria[escolha_galeria]
            
            if imagem_dados:
                id_imagem_final = imagem_dados["id"]
                url_miniatura = imagem_dados.get("media_details", {}).get("sizes", {}).get("thumbnail", {}).get("source_url")
                if not url_miniatura:
                    url_miniatura = imagem_dados.get("source_url")
                    
                st.image(url_miniatura, width=100, caption=f"ID: {id_imagem_final}")
                
                tag_img_existente = f'<img src="{imagem_dados["source_url"]}" alt="{titulo_img}" class="aligncenter" />'
                st.text_area("📋 Código para copiar e colar no texto:", value=tag_img_existente, height=70)
                
                usar_imagem_destaque = st.checkbox("Definir esta imagem como Capa (Destaque)", value=True)
        else:
            st.info("Não foi possível carregar imagens recentes da biblioteca.")
        
        st.markdown("---")
        st.subheader("⚙️ Configurações do Post")
        categorias_selecionadas = st.multiselect(
            "Categorias do Post", 
            options=list(categorias_disponiveis.keys()),
            default=[k for k in ["Notícias", "Geral", "Reserva de Recrutamento"] if k in categorias_disponiveis]
        )
        
        novo_status = st.selectbox("Estado de Publicação", ["draft", "publish", "pending"], format_func=lambda x: "Rascunho" if x=="draft" else "Publicar" if x=="publish" else "Pendente")

    with col_principal:
        if "conteudo_artigo" not in st.session_state:
            st.session_state["conteudo_artigo"] = ""
            
        novo_titulo = st.text_input("✍️ Título do Artigo", placeholder="Escreva o título aqui...")
        novo_conteudo = st.text_area("📝 Corpo do Texto (HTML / Texto)", value=st.session_state["conteudo_artigo"], height=500)
        st.session_state["conteudo_artigo"] = novo_conteudo

        if st.button("🚀 VALIDAR E PUBLICAR ARTIGO", use_container_width=True, type="primary"):
            if not novo_titulo:
                st.error("⚠️ O título do artigo é obrigatório.")
            else:
                ids_categorias = [categorias_disponiveis[cat] for cat in categorias_selecionadas]
                payload = {
                    "title": novo_titulo,
                    "content": novo_conteudo,
                    "status": novo_status,
                    "categories": ids_categorias
                }
                
                # CORREÇÃO DA IMAGEM DE DESTAQUE AQUI
                if usar_imagem_destaque and id_imagem_final:
                    payload["featured_media"] = id_imagem_final
                    
                with st.spinner("A enviar post ..."):
                    res = session.post(f"{API_URL}/wp/v2/posts", json=payload, headers=headers)
                    if res.status_code in[200, 201]:
                        st.success(f"🎉 Artigo publicado com sucesso! ID: {res.json().get('id')}")
                        st.session_state["conteudo_artigo"] = ""
                        st.rerun()
                    else:
                        st.error(f"❌ Erro ao publicar ({res.status_code}): {res.text}")


# --- ABA: EDITAR ARTIGO ---
with aba_editar:
    st.subheader("⚙️ Modificar um Artigo")

    if not st.session_state["wp_autenticado"]:
        st.warning("⚠️ Por favor, efetue o login na aba 'Autenticação' primeiro para poder gerir artigos.")
    else:
        # Define as variáveis locais que o seu código antigo já espera usar
        session = st.session_state["wp_session"]
        headers = {"X-WP-Nonce": st.session_state["wp_nonce"]} if st.session_state["wp_nonce"] else {}        

    with st.spinner("A extrair artigos diretamente do painel administrativo..."):
        try:
            from bs4 import BeautifulSoup
            
            # 1. Aceder diretamente à listagem geral do WP (contém todos os estados: rascunhos, lixo, etc.)
            res_admin = session.get(f"{BASE_URL}/wp-admin/edit.php")
            
            if res_admin.status_code == 200:
                # 2. Passar o HTML da página para a biblioteca BeautifulSoup analisar
                soup = BeautifulSoup(res_admin.text, "html.parser")
                
                # 3. Encontrar todas as linhas da tabela de posts do WordPress
                linhas_posts = soup.select("table.posts tbody tr")
                
                opcoes_posts = {}
                
                for linha in linhas_posts:
                    # Extrair o ID do post (o WP guarda-o no ID da linha do HTML, ex: "post-1234")
                    id_attr = linha.get("id", "")
                    if id_attr and id_attr.startswith("post-"):
                        post_id = id_attr.replace("post-", "")
                        
                        # Extrair o título do link do post
                        link_titulo = linha.select_one("td.title a.row-title")
                        if link_titulo:
                            titulo = link_titulo.text.strip()
                            
                            # Detetar se é rascunho ou lixo (o WP coloca labels em texto ao lado do título)
                            estado_texto = "PUBLISHED"
                            post_state = linha.select_one("td.title span.post-state")
                            if post_state:
                                estado_texto = post_state.text.strip().upper()
                                
                            # Criar um rótulo limpo para o Selectbox
                            label = f"[{estado_texto}] {titulo} (ID: {post_id})"
                            
                            # Guardar os dados mínimos necessários para a edição
                            opcoes_posts[label] = {
                                "id": post_id,
                                "title": titulo
                            }
                
                if opcoes_posts:
                    selecionado = st.selectbox("Selecione o artigo para editar ou recuperar:", list(opcoes_posts.keys()))
                    post_dados = opcoes_posts[selecionado]
                    
                    # --- CARREGAR O CONTEÚDO DO POST SELECIONADO ---
                    # Para ler o conteúdo real do texto, entramos na página de edição desse ID específico

                    if st.checkbox("Carregar conteúdo do artigo selecionado", key=f"load_{post_dados['id']}"):
                        with st.spinner("A descarregar conteúdo original do WordPress..."):
                            try:
                                # 1. Chamar o exportador nativo do WordPress para este post específico
                                # Este URL devolve um XML com os dados brutos e ignora completamente o Gutenberg e a API
                                res_export = session.get(
                                    f"{BASE_URL}/wp-admin/export.php", 
                                    params={"download": "true", "content": "posts", "post_list": post_dados["id"]}
                                )

                                if res_export.status_code == 200:

                                    from bs4 import BeautifulSoup

                                    soup_xml = BeautifulSoup(res_export.text, "lxml-xml")

                                    conteudo_atual = ""
                                    post_id_procurado = str(post_dados["id"])

                                    for item in soup_xml.find_all("item"):

                                        tag_post_id = item.find("wp:post_id")

                                        if tag_post_id and tag_post_id.text.strip() == post_id_procurado:

                                            tag_conteudo = item.find("content:encoded")

                                            if tag_conteudo and tag_conteudo.text:
                                                conteudo_atual = tag_conteudo.text.strip()

                                            break

                                    if conteudo_atual:
                                        st.success(f"✅ Conteúdo importado para o artigo ID {post_id_procurado}")
                                    else:
                                        st.warning(f"⚠️ Não foi encontrado conteúdo para o artigo ID {post_id_procurado}")

                                    edit_titulo = st.text_input(
                                        "Editar Título",
                                        value=post_dados["title"]
                                    )

                                    edit_conteudo = st.text_area(
                                        "Editar Conteúdo",
                                        value=conteudo_atual,
                                        height=450
                                    )
                                    
                            except Exception as err_xml:
                                st.error(f"💥 Falha ao analisar os dados do artigo: {str(err_xml)}")
                    
                    if st.button("💾 Gravar Alterações"):
                        payload = {
                            "title": edit_titulo, 
                            "content": edit_conteudo
                        }
                        with st.spinner("A atualizar artigo..."):
                            res_patch = session.post(
                                f"{API_URL}/wp/v2/posts/{post_dados['id']}", 
                                json=payload, 
                                headers=headers
                            )
                            if res_patch.status_code in[200, 201]:
                                st.success("✨ Artigo atualizado com sucesso!")
                            else:
                                st.error(f"Erro ao atualizar ({res_patch.status_code}): {res_patch.text}")
                else:
                    st.info("Não foram encontrados artigos publicados no site.")
            else:
                st.error(f"❌ Erro {res_posts.status_code} ao carregar artigos.")
        except Exception as e:
            st.error(f"💥 Erro: {str(e)}")

with aba_dashboard:            

    st.subheader("⚙️ Monotorizar")

    if not st.session_state["wp_autenticado"]:
        st.warning("⚠️ Por favor, efetue o login na aba 'Autenticação' primeiro para poder gerir artigos.")
    else:
        # Define as variáveis locais que o seu código antigo já espera usar
        session = st.session_state["wp_session"]
        headers = {"X-WP-Nonce": st.session_state["wp_nonce"]} if st.session_state["wp_nonce"] else {}


    df_posts, df_pages, df_media = carregar_dados_wp()

    # --- VERIFICAÇÃO EM TEMPO REAL (IGNORANDO CACHE) ---
    try:
        # Adiciona um número único baseado no tempo atual ao URL (ex: ?cache=1715012345)
        # Isto força o Cloudflare ou qualquer plugin a ignorar a cache e perguntar ao servidor real
        url_sem_cache = f"{BASE_URL}/?nocache={int(time.time())}"
        
        # Usamos o GET com stream=True para ler apenas os cabeçalhos iniciais sem descarregar a página
        resposta_site = requests.get(url_sem_cache, timeout=5, stream=True)
        
        if resposta_site.status_code == 503:
            st.error("🚧 **Estado do Site:** O site encontra-se atualmente em **Modo de Manutenção**.")
        elif resposta_site.status_code == 200:
            st.success("🟢 **Estado do Site:** O site está **Online** e operacional.")
        else:
            st.warning(f"⚠️ **Estado do Site:** Resposta do servidor (Código HTTP: {resposta_site.status_code}).")
            
        resposta_site.close() # Fechar a ligação de forma limpa
    except requests.exceptions.RequestException:
        st.error("🚨 **Estado do Site:** Não foi possível contactar o servidor. O site pode estar offline.")

    st.markdown("---")

    if df_posts.empty and df_pages.empty:
        st.error("Não foi possível extrair dados para o Dashboard. Verifique a ligação.")
    else:
        # --- MÉTRICAS GERAIS ---
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Artigos (Últimos 100)", len(df_posts))
        with col2:
            st.metric("Total de Páginas (Últimas 100)", len(df_pages))
            
        st.markdown("---")
        
        # --- ANÁLISE DE POSTS ---
        if not df_posts.empty:
            st.subheader("Análise Cronológica de Artigos")
            
            # Converter coluna de data
            df_posts['date'] = pd.to_datetime(df_posts['date'])
            df_posts['Ano-Mês'] = df_posts['date'].dt.to_period('M').astype(str)
            
            # Gráfico 1: Publicações por Mês
            volumetria_mensal = df_posts.groupby('Ano-Mês').size().reset_index(name='Quantidade')
            st.markdown("**Volume de Artigos Criados por Mês:**")
            st.bar_chart(data=volumetria_mensal, x='Ano-Mês', y='Quantidade')
            
            # Gráfico 2: Distribuição por Estado (Status)
            if 'status' in df_posts.columns:
                st.markdown("**Distribuição por Estado de Publicação:**")
                status_dist = df_posts['status'].value_counts()
                st.bar_chart(status_dist)
                
            # Tabela Detalhada
            st.markdown("**Lista Recente de Artigos:**")
            colunas_exibição = [c for c in ['id', 'date', 'title.rendered', 'slug', 'status'] if c in df_posts.columns]
            st.dataframe(df_posts[colunas_exibição], width='stretch')

            # Tabela Detalhada
            st.markdown("**Lista Recente de páginas:**")
            colunas_exibição = [c for c in ['id', 'date', 'title.rendered', 'slug', 'status'] if c in df_pages.columns]
            st.dataframe(df_pages[colunas_exibição], width='stretch')