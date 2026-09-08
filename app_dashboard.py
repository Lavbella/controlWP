import os
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Analytics Dashboard", layout="wide")
st.title("📊 Dashboard de Conteúdo")

BASE_URL = os.getenv("APP_WORDPRESS_SITE_URL", "")
API_URL = os.getenv("APP_WORDPRESS_BASE_URL", "")
ENV_USER = os.getenv("WP_USER", "")
ENV_PASS = os.getenv("WP_PASS", "")

@st.cache_data(ttl=300)  # Guarda os dados em cache por 5 minutos para performance
def carregar_dados_wp():
    session = requests.Session()
    payload = {"log": ENV_USER, "pwd": ENV_PASS, "wp-submit": "Log In", "redirect_to": f"{BASE_URL}/wp-admin/", "testcookie": "1"}
    session.post(f"{BASE_URL}/wp-login.php", data=payload, allow_redirects=False)
    
    # Puxar Posts e Páginas (máximo de 100 itens para o exemplo)
    res_posts = session.get(f"{API_URL}/wp/v2/posts", params={"per_page": 100})
    res_pages = session.get(f"{API_URL}/wp/v2/pages", params={"per_page": 100})
    
    df_posts = pd.json_normalize(res_posts.json()) if res_posts.status_code == 200 else pd.DataFrame()
    df_pages = pd.json_normalize(res_pages.json()) if res_pages.status_code == 200 else pd.DataFrame()
    
    return df_posts, df_pages

df_posts, df_pages = carregar_dados_wp()

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
