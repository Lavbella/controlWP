import os
import re
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Editor de Conteúdo", layout="centered")
st.title("✍️ Gestor e Publicador de Artigos")

BASE_URL = os.getenv("APP_WORDPRESS_SITE_URL", "https://xxxx.pt")
API_URL = os.getenv("APP_WORDPRESS_BASE_URL", "https://xxxx.pt")
ENV_USER = os.getenv("WP_USER", "")
ENV_PASS = os.getenv("WP_PASS", "")

# Função para autenticar e obter a sessão + Nonce de segurança
def iniciar_sessao_wp():
    session = requests.Session()
    payload = {
        "log": ENV_USER,
        "pwd": ENV_PASS,
        "wp-submit": "Log In",
        "redirect_to": f"{BASE_URL}/wp-admin/",
        "testcookie": "1"
    }
    
    # Login
    login_response = session.post(f"{BASE_URL}/wp-login.php", data=payload, allow_redirects=True)
    cookies = session.cookies.get_dict()
    autenticado = any("wordpress_logged_in" in nome for nome in cookies.keys())
    
    if not autenticado:
        return None, None
    
    # Capturar o Nonce de segurança para permitir POST/PUT
    admin_page = session.get(f"{BASE_URL}/wp-admin/post-new.php")
    nonce_match = re.search(r'"wpRestNonce":"([^"]+)"', admin_page.text)
    
    nonce = nonce_match.group(1) if nonce_match else None
    return session, nonce

session, nonce = iniciar_sessao_wp()

if not session:
    st.error("❌ Falha na autenticação. Verifique o ficheiro `.env`.")
else:
    headers = {"X-WP-Nonce": nonce} if nonce else {}

    aba_criar, aba_editar = st.tabs(["🆕 Publicar Novo Artigo", "✏️ Editar Artigo Existente"])

    # --- ABA: CRIAR ARTIGO ---
    with aba_criar:
        st.subheader("Criar Novo Post")
        novo_titulo = st.text_input("Título do Artigo", key="c_titulo")
        novo_conteudo = st.text_area("Conteúdo (HTML ou Texto Limpo)", height=250, key="c_conteudo")
        novo_status = st.selectbox("Estado", ["draft", "publish", "pending"], format_func=lambda x: "Rascunho" if x=="draft" else "Publicado" if x=="publish" else "Pendente")
        
        if st.button("🚀 Publicar no Site"):
            if not novo_titulo:
                st.warning("O título é obrigatório.")
            else:
                payload = {"title": novo_titulo, "content": novo_conteudo, "status": novo_status}
                with st.spinner("A enviar para o WordPress..."):
                    res = session.post(f"{API_URL}/wp/v2/posts", json=payload, headers=headers)
                    if res.status_code in [200, 201]:
                        st.success(f"🎉 Artigo criado com sucesso! ID: {res.json().get('id')}")
                    else:
                        st.error(f"Erro ao criar ({res.status_code}): {res.text}")

    # --- ABA: EDITAR ARTIGO ---
    with aba_editar:
        st.subheader("Modificar um Artigo")
        
        # Procurar os últimos 10 posts para escolher
        with st.spinner("A carregar artigos recentes..."):
            res_posts = session.get(f"{API_URL}/wp/v2/posts", params={"per_page": 10, "status": "publish"})
            
        if res_posts.status_code == 200 and res_posts.json():
            lista_posts = res_posts.json()
            opcoes_posts = {p['title']['rendered']: p for p in lista_posts}
            
            selecionado = st.selectbox("Selecione o artigo para editar", list(opcoes_posts.keys()))
            post_dados = opcoes_posts[selecionado]
            
            # Preencher campos com dados atuais
            edit_titulo = st.text_input("Editar Título", value=post_dados['title']['rendered'])
            edit_conteudo = st.text_area("Editar Conteúdo", value=post_dados['content']['rendered'], height=250)
            edit_status = st.selectbox("Alterar Estado", ["draft", "publish", "pending"], index=["draft", "publish", "pending"].index(post_dados['status']))
            
            if st.button("💾 Gravar Alterações"):
                payload = {"title": edit_titulo, "content": edit_conteudo, "status": edit_status}
                with st.spinner("A atualizar artigo..."):
                    res_patch = session.post(f"{API_URL}/wp/v2/posts/{post_dados['id']}", json=payload, headers=headers)
                    if res_patch.status_code == 200:
                        st.success("✨ Artigo atualizado com sucesso!")
                    else:
                        st.error(f"Erro ao atualizar ({res_patch.status_code}): {res_patch.text}")
        else:
            st.info("Não foi possível carregar os artigos para edição.")
