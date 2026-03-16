import hashlib
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Usuários do sistema
#
# Para adicionar um novo usuário:
#   "login": {
#       "hash":  hashlib.sha256("senha".encode()).hexdigest(),
#       "role":  "admin" | "user",
#       "name":  "Nome exibido",
#       "pages": ["Dashboard", "Comercial", ...],  # páginas liberadas
#   }
# ─────────────────────────────────────────────────────────────────────────────

_USERS = {
    # ── Administrador ─────────────────────────────────────────────────────
    "admin": {
        "hash":  hashlib.sha256("admin123".encode()).hexdigest(),
        "role":  "admin",
        "name":  "Administrador",
        "pages": ["Dashboard", "Comercial", "Logística", "CCO", "Logs"],
    },

    # ── Equipes operacionais ───────────────────────────────────────────────
    "comercial": {
        "hash":  hashlib.sha256("comercial123".encode()).hexdigest(),
        "role":  "user",
        "name":  "Equipe Comercial",
        "pages": ["Comercial"],
    },
    "logistica": {
        "hash":  hashlib.sha256("log123".encode()).hexdigest(),
        "role":  "user",
        "name":  "Equipe Logística",
        "pages": ["Logística"],
    },

    # ── Equipe CCO (novo) ─────────────────────────────────────────────────
    "cco": {
        "hash":  hashlib.sha256("cco123".encode()).hexdigest(),
        "role":  "user",
        "name":  "Equipe CCO",
        "pages": ["CCO"],
    },
}


def authenticate(username: str, password: str) -> Optional[dict]:
    u = _USERS.get(username.strip().lower())
    if u and u["hash"] == hashlib.sha256(password.encode()).hexdigest():
        return {
            "username":      username.strip().lower(),
            "display_name":  u["name"],
            "role":          u["role"],
            "allowed_pages": u["pages"],
        }
    return None


def get_allowed_pages(user: dict) -> list:
    return user.get("allowed_pages", [])
