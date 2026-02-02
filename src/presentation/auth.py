"""
Sistema de autenticação simples para o dashboard.
"""

import streamlit as st
import hashlib
from typing import Optional, Dict


class AuthService:
    """
    Serviço de autenticação básica.
    
    Em produção, substituir por autenticação com banco de dados.
    """
    
    # Usuários hardcoded (APENAS PARA DESENVOLVIMENTO)
    # Em produção, usar banco de dados com senhas hasheadas
    USERS: Dict[str, Dict[str, str]] = {
        "admin": {
            "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
            "role": "admin",
            "name": "Administrador"
        },
        "viewer": {
            "password_hash": hashlib.sha256("viewer123".encode()).hexdigest(),
            "role": "viewer",
            "name": "Visualizador"
        }
    }
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash SHA-256 da senha.
        
        Args:
            password: Senha em texto plano.
            
        Returns:
            Hash da senha.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verificar_login(username: str, password: str) -> bool:
        """
        Verifica credenciais do usuário.
        
        Args:
            username: Nome de usuário.
            password: Senha.
            
        Returns:
            True se credenciais válidas.
        """
        if username not in AuthService.USERS:
            return False
        
        password_hash = AuthService.hash_password(password)
        return AuthService.USERS[username]["password_hash"] == password_hash
    
    @staticmethod
    def get_user_info(username: str) -> Optional[Dict[str, str]]:
        """
        Obtém informações do usuário.
        
        Args:
            username: Nome de usuário.
            
        Returns:
            Dicionário com informações ou None.
        """
        if username in AuthService.USERS:
            return {
                "username": username,
                "name": AuthService.USERS[username]["name"],
                "role": AuthService.USERS[username]["role"]
            }
        return None
    
    @staticmethod
    def exibir_login() -> Optional[str]:
        """
        Renderiza tela de login no Streamlit.
        
        Returns:
            Username se login bem-sucedido, None caso contrário.
        """
        st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <h1>🔐 DataCloud SaaS Analytics</h1>
            <p>Sistema de Análise de Assinaturas</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Login")
            
            with st.form("login_form"):
                username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
                password = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
                
                submitted = st.form_submit_button("🚀 Entrar", use_container_width=True)
                
                if submitted:
                    if not username or not password:
                        st.error("❌ Preencha usuário e senha")
                    elif AuthService.verificar_login(username, password):
                        st.session_state.authenticated = True
                        st.session_state.user_info = AuthService.get_user_info(username)
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos")
            
            with st.expander("ℹ️ Credenciais de Teste"):
                st.info("""
                **Admin:**
                - Usuário: `admin`
                - Senha: `admin123`
                
                **Visualizador:**
                - Usuário: `viewer`
                - Senha: `viewer123`
                """)
        
        return None
    
    @staticmethod
    def logout():
        """Realiza logout do usuário."""
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()
    
    @staticmethod
    def is_admin() -> bool:
        """Verifica se usuário logado é admin."""
        if 'user_info' in st.session_state and st.session_state.user_info:
            return st.session_state.user_info.get('role') == 'admin'
        return False
    
    @staticmethod
    def render_user_info():
        """Renderiza informações do usuário logado na sidebar."""
        if 'user_info' in st.session_state and st.session_state.user_info:
            user = st.session_state.user_info
            
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"**👤 {user['name']}**")
            st.sidebar.caption(f"Função: {user['role'].title()}")
            
            if st.sidebar.button("🚪 Sair", use_container_width=True):
                AuthService.logout()
