import requests
from typing import List, Dict, Optional

# Configuration
from kiosk_interface.config import ConfParameter

conf = ConfParameter()

API_PROVIDER = conf.api_provider
API_KEY = conf.api_key



# Mémoire de la conversation (simplifiée)
conversation_history: List[Dict[str, str]] = []

def detect_language(text: str) -> str:
    """Détecte la langue du texte (très basique, à améliorer avec une librairie comme langdetect)."""
    if any(word in text.lower() for word in ["hello", "password", "windows", "help"]):
        return "en"
    return "fr"  # par défaut

def envoyer_message_au_bot(message: str, user_id: str = "default") -> str:
    """
    Fonction améliorée pour envoyer un message à une IA.
    - Répond uniquement aux problèmes techniques.
    - Garde la continuité de la conversation.
    - Répond dans la langue de l'utilisateur.
    """
    global conversation_history

    # Détecte la langue
    lang = detect_language(message)
    system_prompt = (
        f"Tu es un assistant technique spécialisé dans les problèmes d'ordinateurs, logiciels et applications. "
        f"Réponds toujours dans la langue de l'utilisateur ({lang}). "
        f"Si la question n'est pas technique, réponds poliment que tu ne peux traiter que les problèmes techniques. "
        f"Garde la continuité de la conversation et pose des questions pour préciser le problème si nécessaire. "
        f"Ne réponds pas hors sujet."
    )

    # Ajoute le message à l'historique
    conversation_history.append({"role": "user", "content": message})

    if API_PROVIDER == "openai":
        return _call_openai(system_prompt, conversation_history, lang)
    elif API_PROVIDER == "anthropic":
        return _call_anthropic(system_prompt, conversation_history, lang)
    elif API_PROVIDER == "gemini":
        return _call_gemini(system_prompt, conversation_history, lang)
    else:
        return "[Erreur] Fournisseur IA inconnu."

# ==== Connecteurs ====

def _call_openai(system_prompt: str, history: List[Dict[str, str]], lang: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            *history
        ]
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        response = r.json()["choices"][0]["message"]["content"].strip()
        # Ajoute la réponse à l'historique
        history.append({"role": "assistant", "content": response})
        return response
    except Exception as e:
        return f"[Erreur API OpenAI] {e}"

def _call_anthropic(system_prompt: str, history: List[Dict[str, str]], lang: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-3-5-haiku-20241022",
        "system": system_prompt,
        "messages": history,
        "max_tokens": 512
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        response = data["content"][0]["text"].strip()
        # Ajoute la réponse à l'historique
        history.append({"role": "assistant", "content": response})
        return response
    except requests.exceptions.RequestException as e:
        return f"[Erreur réseau] {e}"
    except KeyError as e:
        return f"[Erreur format réponse] {e}"
    except Exception as e:
        return f"[Erreur API Anthropic] {e}"

def _call_gemini(system_prompt: str, history: List[Dict[str, str]], lang: str) -> str:
    # Exemple minimal — à compléter avec la vraie API Google Gemini
    return "[Mock] Réponse Gemini"
