import requests
import json
# --- Configuration ---
from kiosk_interface.config import ConfParameter

conf = ConfParameter()

GLPI_URL = conf.glpi_url
APP_TOKEN = conf.glpi_app_token
API_TOKEN = conf.glpi_api_token


# --- Connexion à la session ---
def init_session():
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {API_TOKEN}"
    }
    r = requests.get(f"{GLPI_URL}/initSession", headers=headers)
    r.raise_for_status()
    session_token = r.json()["session_token"]

    # On renvoie directement les headers prêts à être réutilisés
    session_headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }
    return session_headers

# --- Déconnexion ---
def kill_session(session_headers):
    requests.get(f"{GLPI_URL}/killSession", headers=session_headers)

# --- Création ticket ---
def create_ticket(session_headers, title, content):
    payload = {
        "input": {
            "name": title,
            "content": content
        }
    }
    r = requests.post(f"{GLPI_URL}/Ticket", headers=session_headers, json=payload)
    r.raise_for_status()
    return r.json()["id"]

# --- Upload capture ---
def upload_document(session_headers, ticket_id, file_path):
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_headers["Session-Token"]
    }
    files = {
        "uploadManifest": (
            None,
            '{"input": {"name": "screenshot.png","_filename":"screenshot.png","items_id": %d,"itemtype": "Ticket"}}' % ticket_id,
            "application/json"
        ),
        "file": open(file_path, "rb")
    }
    r = requests.post(f"{GLPI_URL}/Document", headers=headers, files=files)
    r.raise_for_status()
    return r.json()

# --- Historique (followups) d’un ticket ---
def list_ticket_followups(session_headers, ticket_id: int):
    """Récupère les followups d'un ticket GLPI - VERSION CORRIGÉE"""
    try:
        # MÉTHODE 1: Essayer avec search
        params = {
            'criteria[0][field]': '4',      # items_id (champ 4)
            'criteria[0][searchtype]': 'equals',
            'criteria[0][value]': str(ticket_id),
            'criteria[1][field]': '3',      # itemtype (champ 3)  
            'criteria[1][searchtype]': 'equals',
            'criteria[1][value]': 'Ticket',
            'forcedisplay[0]': '2',         # content
            'forcedisplay[1]': '4',         # items_id
            'forcedisplay[2]': '5',         # date
            'forcedisplay[3]': '19'         # users_id_editor
        }
        
        r = requests.get(f"{GLPI_URL}/search/ITILFollowup", headers=session_headers, params=params)
        print(f"DEBUG search: {r.status_code} - {r.text[:200]}")
        
        if r.status_code == 200:
            data = r.json()
            if 'data' in data and data['data']:
                return data['data']
        
        # MÉTHODE 2: Si search échoue, essayer directement
        print("Tentative méthode directe...")
        r2 = requests.get(f"{GLPI_URL}/Ticket/{ticket_id}/ITILFollowup", headers=session_headers)
        print(f"DEBUG direct: {r2.status_code} - {r2.text[:200]}")
        
        if r2.status_code == 200:
            return r2.json()
            
        # MÉTHODE 3: Dernière tentative avec paramètres simplifiés
        print("Tentative méthode simplifiée...")
        simple_params = {'items_id': ticket_id, 'itemtype': 'Ticket'}
        r3 = requests.get(f"{GLPI_URL}/ITILFollowup", headers=session_headers, params=simple_params)
        print(f"DEBUG simple: {r3.status_code} - {r3.text[:200]}")
        
        if r3.status_code == 200:
            return r3.json()
            
        return []
        
    except Exception as e:
        print(f"Erreur dans list_ticket_followups: {e}")
        return []

# --- Ajouter une réponse (followup) sur un ticket ---
def add_ticket_followup(session_headers, ticket_id: int, content: str):
    """Ajoute un followup à un ticket - VERSION CORRIGÉE"""
    try:
        # CORRECTION: Structure correcte du payload
        payload = {
            "input": {
                "itemtype": "Ticket",
                "items_id": int(ticket_id),
                "content": content
            }
        }
        
        print(f"DEBUG payload: {json.dumps(payload, indent=2)}")
        
        r = requests.post(f"{GLPI_URL}/ITILFollowup", headers=session_headers, json=payload)
        print(f"DEBUG response: {r.status_code} - {r.text}")
        
        if r.status_code == 201:  # Created
            return r.json().get("id")
        elif r.status_code == 200:  # OK
            return r.json().get("id", 1)
        else:
            r.raise_for_status()
            
    except Exception as e:
        print(f"Erreur dans add_ticket_followup: {e}")
        raise e

# --- Récupérer le statut d’un ticket ---
def get_ticket_status(session_headers, ticket_id: int) -> int:
    r = requests.get(f"{GLPI_URL}/Ticket/{ticket_id}", headers=session_headers)
    r.raise_for_status()
    data = r.json()
    return int(data.get("status", 1))  # 1=New, 2=Assigned, 3=Planned, 4=Waiting, 5=Solved, 6=Closed

# --- Exemple d’utilisation ---
if __name__ == "__main__":
    session = init_session()
    ticket_id = create_ticket(session, "Bug avec l’application", "Voici une capture d’écran du problème")
    print(f"✅ Ticket créé avec ID {ticket_id}")

    # Joindre capture d’écran
    resp = upload_document(session, ticket_id, "screenshot.png")
    print("📎 Capture ajoutée :", resp)

    # Historique du ticket
    history = list_ticket_followups(session, ticket_id)
    print("📜 Historique :", history)

    # Ajouter un suivi
    add_ticket_followup(session, ticket_id, "Nouvelle réponse depuis l’API")
    print("💬 Réponse envoyée à GLPI")

    # Vérifier statut
    status = get_ticket_status(session, ticket_id)
    print("📌 Statut actuel :", status)

    kill_session(session)
