import os
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv

# Carregar as variáveis do ficheiro .env
load_dotenv()

st.set_page_config(page_title="AGSE - Validador WordPress API", layout="wide")

st.title("🏛️ AGSE - Validador de Conexão via Cookie")
st.write("Aplicação configurada para validar o acesso através de variáveis de ambiente.")

# Obter URLs e credenciais do ficheiro .env (com fallbacks se não existirem)
BASE_URL = os.getenv("APP_WORDPRESS_SITE_URL", "https://agse.pt")
API_URL = os.getenv("APP_WORDPRESS_BASE_URL", "https://agse.pt")
ENV_USER = os.getenv("WP_USER", "")
ENV_PASS = os.getenv("WP_PASS", "")

# Painel Lateral para Credenciais
st.sidebar.header("🔑 Credenciais de Acesso")
wp_user = st.sidebar.text_input("Nome de Utilizador / Email", value=ENV_USER)
wp_password = st.sidebar.text_input("Senha de Login", value=ENV_PASS, type="password")

# Recursos/Endpoints para testar
endpoints = {
    "Posts (Artigos)": "wp/v2/posts",
    "Pages (Páginas)": "wp/v2/pages",
    "Media (Multimédia)": "wp/v2/media"
}

if st.sidebar.button("Efetuar Login e Listar Recursos"):
    if not wp_user or not wp_password:
        st.sidebar.error("Por favor, preencha o utilizador e a senha.")
    else:
        login_url = f"{BASE_URL}/wp-login.php"
        session = requests.Session()
        
        payload = {
            "log": wp_user,
            "pwd": wp_password,
            "wp-submit": "Log In",
            "redirect_to": f"{BASE_URL}/wp-admin/",
            "testcookie": "1"
        }
        
        st.subheader("🔐 Passo 1: Autenticação")
        with st.spinner("A simular login..."):
            try:
                login_response = session.post(login_url, data=payload, allow_redirects=False)
                cookies_gerados = session.cookies.get_dict()
                autenticado = any("wordpress_logged_in" in nome_cookie for nome_cookie in cookies_gerados.keys())
                
                if autenticado:
                    st.success("🎉 Autenticação bem-sucedida através das credenciais do ambiente!")
                    
                    st.subheader("📊 Passo 2: Recursos Disponíveis (Endpoints)")
                    
                    for name, path in endpoints.items():
                        full_api_url = f"{API_URL}/{path}"
                        
                        with st.spinner(f"A consultar {name}..."):
                            api_response = session.get(full_api_url, params={"per_page": 10})
                            
                            if api_response.status_code == 200:
                                st.write(f"✅ **{name}** acessível.")
                                data = api_response.json()
                                
                                if data:
                                    df = pd.json_normalize(data)
                                    colunas = [c for c in ['id', 'title.rendered', 'name', 'slug', 'date'] if c in df.columns]
                                    st.dataframe(df[colunas] if colunas else df.iloc[:, :4], width='stretch')
                                else:
                                    st.info(f"Nenhum registo encontrado em {name}.")
                            else:
                                st.error(f"❌ Erro {api_response.status_code} ao aceder a {name}.")
                else:
                    st.error("❌ Falha na autenticação. Verifique as credenciais no ficheiro .env.")
                    
            except Exception as e:
                st.error(f"💥 Erro de conexão ao tentar aceder ao servidor: {str(e)}")
