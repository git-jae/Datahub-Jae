import sys
import os
import importlib.util

# ── Resolve project root from this file's location ───────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _load(name: str, rel: str):
    """Load a module by absolute path and register it in sys.modules."""
    full = os.path.join(ROOT, rel)
    spec = importlib.util.spec_from_file_location(name, full)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _safe_load(name: str, rel: str):
    """
    Tenta carregar um módulo de página.
    Se falhar, retorna um módulo fictício com render() que exibe o erro,
    sem derrubar o resto da aplicação (sidebar inclusa).
    """
    try:
        return _load(name, rel)
    except Exception as e:
        import types
        err_msg = str(e)
        mod = types.ModuleType(name)

        def render_error(user: dict, _msg=err_msg, _name=name):
            st.error(f"❌ Erro ao carregar o módulo **{_name}**:\n\n```\n{_msg}\n```")
            st.info("Verifique se todos os arquivos e dependências estão no lugar correto.")

        mod.render = render_error
        sys.modules[name] = mod
        return mod


import streamlit as st
from streamlit_option_menu import option_menu

# ── Core modules ──────────────────────────────────────────────────────────────
_auth = _load("auth_users", "auth/auth_users.py")
_ui   = _load("ui_helpers",  "ui/ui_helpers.py")

authenticate       = _auth.authenticate
get_allowed_pages  = _auth.get_allowed_pages
load_css           = _ui.load_css
sidebar_logo       = _ui.sidebar_logo
sidebar_user_badge = _ui.sidebar_user_badge

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jaé · Datahub",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css()


# ── Session ───────────────────────────────────────────────────────────────────
def _init():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None


def _logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()


# ── Login ─────────────────────────────────────────────────────────────────────
def _login():
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
            <div style="text-align:center;padding:32px 0 28px 0;">
                <div style="display:inline-flex;align-items:center;justify-content:center;
                            width:80px;height:80px;background:#00C4B4;border-radius:22px;
                            margin-bottom:20px;box-shadow:0 8px 28px rgba(0,196,180,0.35);">
                    <span style="font-family:'Nunito',sans-serif;font-weight:900;
                                 font-size:26px;color:#fff;">Jaé</span>
                </div>
                <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:26px;
                            color:#e8eaf2;margin-bottom:6px;">Datahub</div>
                <div style="font-size:13px;color:#555c72;letter-spacing:0.5px;">
                    Plataforma de dados interna</div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username  = st.text_input("Usuário",  placeholder="ex: admin")
            password  = st.text_input("Senha",    type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Entrar →", use_container_width=True)

        if submitted:
            user = authenticate(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")


# ── Main app ──────────────────────────────────────────────────────────────────
def _app(user: dict):
    # ── Carrega páginas com proteção contra falha de import ───────────────
    dash  = _safe_load("dashboard_admin", os.path.join("ui", "pages", "dashboard_admin.py"))
    com   = _safe_load("comercial",       os.path.join("ui", "pages", "comercial.py"))
    tele  = _safe_load("telemarketing",   os.path.join("ui", "pages", "telemarketing.py"))
    dev   = _safe_load("devolucao",       os.path.join("ui", "pages", "devolucao.py"))
    log   = _safe_load("logistica",       os.path.join("ui", "pages", "logistica.py"))
    cco   = _safe_load("cco",             os.path.join("ui", "pages", "cco.py"))
    atd   = _safe_load("atendimento",     os.path.join("ui", "pages", "atendimento.py"))
    logs  = _safe_load("logs_admin",      os.path.join("ui", "pages", "logs_admin.py"))

    allowed = get_allowed_pages(user)

    PAGE_MAP = {
        "Dashboard":   ("house",               dash.render),
        "Comercial":   ("shop",                com.render),
        "Logística":   ("truck",               log.render),
        "CCO":         ("credit-card-2-front", cco.render),
        "Atendimento": ("headset",             atd.render),
        "Logs":        ("file-earmark-text",   logs.render),
    }

    items = [p for p in PAGE_MAP if p in allowed]
    icons = [PAGE_MAP[p][0] for p in items]

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        sidebar_logo()
        sidebar_user_badge(user)

        selected = option_menu(
            menu_title=None,
            options=items,
            icons=icons,
            default_index=0,
            styles={
                "container":         {"padding": "0", "background-color": "transparent"},
                "icon":              {"color": "#555c72", "font-size": "15px"},
                "nav-link": {
                    "font-family":   "'Nunito', sans-serif",
                    "font-size":     "14px",
                    "font-weight":   "700",
                    "color":         "#8b90a8",
                    "padding":       "10px 14px",
                    "border-radius": "10px",
                    "margin":        "2px 0",
                    "--hover-color": "rgba(0,196,180,0.08)",
                },
                "nav-link-selected": {
                    "background-color": "rgba(0,196,180,0.12)",
                    "color":       "#00C4B4",
                    "font-weight": "800",
                },
            },
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⏏  Sair", use_container_width=True):
            _logout()

    # ── Renderiza a página selecionada ────────────────────────────────────
    PAGE_MAP[selected][1](user)


# ── Entry point ───────────────────────────────────────────────────────────────
_init()
if not st.session_state.authenticated:
    _login()
else:
    _app(st.session_state.user)