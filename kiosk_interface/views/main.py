"""
Application de chat moderne avec système de tickets
"""
from dataclasses import dataclass, field
from datetime import datetime
import threading
from typing import List
import logging
import html, re

import sys
import uuid
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QLabel,
    QLineEdit, QSplitter, QSizePolicy, QScrollArea, QFrame, QDialog,
    QFormLayout, QDialogButtonBox, QMessageBox, QFileDialog, QSpacerItem
)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QAction, QFont, QPixmap, QPainter, QBrush, QColor
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer,QPropertyAnimation, QEasingCurve, QRect,QSize
from PyQt6.QtGui import QPixmap,QIcon
from kiosk_interface.views.chat_api import envoyer_message_au_bot
from kiosk_interface.views.glpi_api import (
    init_session,
    create_ticket as glpi_create_ticket,
    upload_document,
    kill_session,
    get_ticket_status,          # <-- pour les statuts GLPI
    list_ticket_followups,      # <-- pour afficher l’historique
    add_ticket_followup         # <-- pour répondre depuis le chat
)
import speech_recognition as sr
import os, json
from dataclasses import asdict

# Dossier où se trouve main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dossier racine du projet (parent de Views)
PROJECT_DIR = os.path.dirname(BASE_DIR)

# Dossier pour stocker les conversations (à la racine)
CONV_DIR = os.path.join(PROJECT_DIR, "conversations")
os.makedirs(CONV_DIR, exist_ok=True)



# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Data classes (Model)
# ---------------------------
@dataclass
class Message:
    id: str
    text: str
    sender: str  # 'user' or 'bot'
    timestamp: datetime = field(default_factory=datetime.now)
    conversation_id: str = ""  

@dataclass
class Conversation:
    id: str
    title: str
    last_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    unread_count: int = 0

@dataclass
class Ticket:
    id: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    screenshot_path: str | None = None
    status: str = "open"

# ---------------------------
# Model - Gestion des données
# ---------------------------
class ChatModel(QObject):
    message_added = pyqtSignal(Message)
    ticket_created = pyqtSignal(Ticket)
    conversation_selected = pyqtSignal(str)
    ticket_updated = pyqtSignal(Ticket) 
    def __init__(self):
        super().__init__()
        self._messages: List[Message] = []
        self._tickets: List[Ticket] = []
        self._conversations: List[Conversation] = []
        self._current_conversation_id: str = ""
        self._init_sample_data()
        self._tickets = self._load_tickets()  # <-- ajoute ceci


    def _init_sample_data(self):
        # Pas de conversations factices au démarrage
        self._conversations = []
        self._current_conversation_id = None


    def add_message(self, text: str, sender: str = "user") -> Message:
        # Assure une conversation sélectionnée
        if not self._current_conversation_id:
            # crée une conversation par défaut si besoin
            self._current_conversation_id = str(uuid.uuid4())
            self._conversations.insert(0, Conversation(self._current_conversation_id, "New conversation"))

        msg = Message(
            id=str(uuid.uuid4()),
            text=text,
            sender=sender,
            timestamp=datetime.now(),
            conversation_id=self._current_conversation_id  # ✅ corrigé (tu avais .je)
        )
        self._messages.append(msg)

        # Met à jour le résumé de conversation
        for c in self._conversations:
            if c.id == self._current_conversation_id:
                c.last_message = text
                c.timestamp = msg.timestamp
                # ✅ si c’est le premier message utilisateur → utiliser comme titre
                if sender == "user" and (c.title == "New conversation" or not c.title):
                    c.title = text.split("\n")[0][:30]  # max 30 caractères
                break

        logger.info(f"Added message: {msg}")
        self.message_added.emit(msg)
        return msg



    def get_messages(self) -> List[Message]:
        return list(self._messages)

    def get_conversations(self) -> List[Conversation]:
        return list(self._conversations)
    
    import os, json, re  # si pas déjà importés

    def _conv_dir(self) -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "conversations")
        os.makedirs(path, exist_ok=True)
        return path

    def _conversation_path(self, conv_id: str) -> str:
        return os.path.join(self._conv_dir(), f"{conv_id}.json")

    def save_current_conversation(self) -> None:
        if not self._current_conversation_id:
            return

        # Messages de la conversation courante
        msgs = [m for m in self._messages if m.conversation_id == self._current_conversation_id or m.conversation_id == ""]
        for m in msgs:
            if not m.conversation_id:
                m.conversation_id = self._current_conversation_id

        meta = next((c for c in self._conversations if c.id == self._current_conversation_id), None)
        data = {
            "id": self._current_conversation_id,
            "title": (meta.title if meta else "Conversation"),
            "last_message": (meta.last_message if meta else (msgs[-1].text if msgs else "")),
            "timestamp": (meta.timestamp.isoformat() if meta else (msgs[-1].timestamp.isoformat() if msgs else datetime.now().isoformat())),
            "messages": [
                {
                    "id": m.id,
                    "text": m.text,
                    "sender": m.sender,
                    "timestamp": m.timestamp.isoformat()
                } for m in msgs
            ]
        }
        # JSON
        with open(self._conversation_path(self._current_conversation_id), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # TXT (transcription simple)
        txt_path = os.path.join(self._conv_dir(), f"{self._current_conversation_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            for m in msgs:
                f.write(f"[{m.timestamp.strftime('%Y-%m-%d %H:%M')}] {m.sender}: {m.text}\n")

    def list_saved_conversations(self) -> list[Conversation]:
        convs: list[Conversation] = []
        for name in os.listdir(self._conv_dir()):
            if name.endswith(".json"):
                try:
                    with open(os.path.join(self._conv_dir(), name), "r", encoding="utf-8") as f:
                        d = json.load(f)
                    convs.append(Conversation(
                        id=d.get("id", name[:-5]),
                        title=d.get("title", "Conversation"),
                        last_message=d.get("last_message", ""),
                        timestamp=datetime.fromisoformat(d.get("timestamp")) if d.get("timestamp") else datetime.now()
                    ))
                except Exception as e:
                    logger.warning(f"Cannot read {name}: {e}")
        # fusionne avec celles en mémoire (échantillons) si pas déjà présentes
        known = {c.id for c in convs}
        for c in self._conversations:
            if c.id not in known:
                convs.append(c)
        convs.sort(key=lambda c: c.timestamp, reverse=True)
        return convs

    def load_conversation(self, conv_id: str) -> None:
        path = self._conversation_path(conv_id)
        self._current_conversation_id = conv_id
        self._messages.clear()
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for md in data.get("messages", []):
            self._messages.append(
                Message(
                    id=md["id"],
                    text=md["text"],
                    sender=md["sender"],
                    timestamp=datetime.fromisoformat(md["timestamp"]),
                    conversation_id=conv_id
                )
            )

    
    
    
    
    def new_conversation(self, title: str = "New conversation") -> str:
        """Crée une nouvelle conversation et retourne son ID"""
        conv_id = str(uuid.uuid4())
        conv = Conversation(id=conv_id, title=title, last_message="", timestamp=datetime.now())
        
        # Ajouter au début de la liste des conversations
        self._conversations.insert(0, conv)
        
        # Définir comme conversation courante
        self._current_conversation_id = conv_id
        
        # Vider les messages actuels
        self._messages.clear()
        
        # Créer le fichier de sauvegarde immédiatement
        self.save_current_conversation()
        
        logger.info(f"Nouvelle conversation créée: {conv_id} - {title}")
        return conv_id

    def set_current_conversation(self, conv_id: str) -> None:
        """Définit la conversation courante"""
        old_id = self._current_conversation_id
        if old_id and old_id != conv_id:
            # Sauvegarder l'ancienne conversation avant de changer
            self.save_current_conversation()
        
        self._current_conversation_id = conv_id
        logger.info(f"Conversation courante changée: {old_id} -> {conv_id}")

    def get_current_conversation_id(self) -> str:
        """Retourne l'ID de la conversation courante"""
        return self._current_conversation_id or ""
        

    

    def create_ticket(self, description: str, screenshot_path: str | None = None) -> Ticket:
        try:
        # 1. Connexion à GLPI
            session = init_session()

            
            # Construire un titre basé sur la description
            title = description.split("\n")[0][:50]  # première ligne, max 50 caractères

            ticket_id = glpi_create_ticket(session, title, description)


            # 3. Upload du screenshot si présent
            if screenshot_path:
                upload_document(session, ticket_id, screenshot_path)

            # 4. Fermer la session GLPI
            kill_session(session)

            # 5. Ticket local avec l'ID GLPI (numérique)
            ticket = Ticket(
                id=str(ticket_id),   # ⚠️ ici on met l'ID retourné par GLPI
                description=description,
                screenshot_path=screenshot_path,
                status="open"
            )
            self._tickets.append(ticket)
            self._save_tickets()
            logger.info(f"✅ Ticket envoyé : {ticket}")
            self.ticket_created.emit(ticket)
            return ticket

        except Exception as e:
            # En cas d'erreur, on garde une trace locale
            logger.error(f"❌ Erreur envoi ticket : {e}")
            ticket = Ticket(
                id=str(uuid.uuid4()),  # fallback local si l'API échoue
                description=description,
                screenshot_path=screenshot_path,
                status="error"
                )
            self._tickets.append(ticket)
            self.ticket_created.emit(ticket)
            return ticket


    def get_tickets(self) -> List[Ticket]:
        return list(self._tickets)
    
    def _tickets_path(self) -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "tickets.json")

    def _load_tickets(self) -> list:
        path = self._tickets_path()
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # transforme en instances Ticket si tu as une dataclass Ticket
        tickets = []
        for d in data:
            tickets.append(Ticket(
                id=str(d["id"]),
                description=d.get("description",""),
                created_at=datetime.fromisoformat(d.get("created_at")) if d.get("created_at") else datetime.now(),
                screenshot_path=d.get("screenshot_path"),
                status=d.get("status","open")
            ))
        return tickets

    def _save_tickets(self) -> None:
        path = self._tickets_path()
        data = []
        for t in self._tickets:
            data.append({
                "id": t.id,
                "description": t.description,
                "created_at": t.created_at.isoformat(),
                "screenshot_path": t.screenshot_path,
                "status": t.status
            })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_ticket_status(self, ticket_id: str, new_status: str):
        """Met à jour le statut d'un ticket et émet le signal"""
        for t in self._tickets:
            if t.id == ticket_id and t.status != new_status:
                t.status = new_status
                self._save_tickets()
                self.ticket_updated.emit(t)
                break  




# ---------------------------
# UI Components
# ---------------------------
class MessageBubble(QWidget):
    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self.message = message
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 8, 15, 8)

        time_label = QLabel(self.message.timestamp.strftime("%H:%M"))
        time_label.setStyleSheet("color: #888; font-size: 10px;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignBottom)

        if self.message.sender == "user":
            bubble_widget = QWidget()
            bubble_widget.setMaximumWidth(400)
            bubble_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
            bubble_widget.setStyleSheet("""
                background-color: #E6E6E6;
                color: black;
                border-radius: 15px;
                border-top-right-radius: 4px
            """)

            bubble_layout = QHBoxLayout(bubble_widget)
            bubble_layout.setContentsMargins(15, 15, 15, 15)
            bubble_layout.setSpacing(10)

            # Avatar utilisateur
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)

            possible_paths = [
                os.path.join(parent_dir, "datas", "avatar.png"),
                os.path.join(current_dir, "..", "datas", "avatar.png"),
            ]

            avatar_label = QLabel()
            for logo_path in possible_paths:
                abs_path = os.path.abspath(logo_path)
                if os.path.exists(abs_path):
                    avatar_pixmap = QPixmap(abs_path)
                    if not avatar_pixmap.isNull():
                        scaled_avatar = avatar_pixmap.scaled(
                            35, 35, 
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        avatar_label.setPixmap(scaled_avatar)
                        break

            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar_label.setFixedSize(35, 35)
            avatar_label.setStyleSheet("background: transparent;")

            # Texte du message
            text_label = QLabel(self.message.text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("""
                color: black;
                font-size: 16px;
                background: transparent;
            """)

            # Ajouter texte et avatar (avatar à droite)
            bubble_layout.addWidget(text_label, 1)
            bubble_layout.addWidget(avatar_label)

            # Positionner à droite
            layout.addStretch()
            layout.addWidget(time_label)
            layout.addSpacing(8)
            layout.addWidget(bubble_widget)
        else:
            # Messages du bot
            bubble_widget = QWidget()
            bubble_widget.setMaximumWidth(400)
            bubble_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
            bubble_widget.setStyleSheet("""
                background-color: #8abf46;
                border-radius: 15px;
                border-top-left-radius: 4px;
            """)
            
            bubble_layout = QHBoxLayout(bubble_widget)
            bubble_layout.setContentsMargins(15, 15, 15, 15)
            bubble_layout.setSpacing(10)
            
            # Logo du bot
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            
            possible_paths = [
                os.path.join(parent_dir, "datas", "medulla.png"),
                os.path.join(current_dir, "..", "datas", "medulla.png")
            ]
            
            logo_label = QLabel()
            for logo_path in possible_paths:
                abs_path = os.path.abspath(logo_path)
                if os.path.exists(abs_path):
                    logo_pixmap = QPixmap(abs_path)
                    if not logo_pixmap.isNull():
                        scaled_logo = logo_pixmap.scaled(
                            35, 35, 
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        logo_label.setPixmap(scaled_logo)
                        break
            
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setFixedSize(35, 35)
            logo_label.setStyleSheet("background: transparent;")
            
            # Texte du message bot
            text_label = QLabel(self.message.text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("""
                color: black;
                font-size: 16px;
                background: transparent;
            """)
            
            # Ajouter logo et texte horizontalement
            bubble_layout.addWidget(logo_label)
            bubble_layout.addWidget(text_label, 1)
            
            # Positionner la bulle à gauche
            layout.addWidget(bubble_widget)
            layout.addSpacing(8)
            layout.addWidget(time_label)
            layout.addStretch()

        self.setLayout(layout)
class ConversationItem(QWidget):
    def __init__(self, conversation: Conversation, parent=None):
        super().__init__(parent)
        self.conversation = conversation
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # === Logo Medulla à gauche ===
        logo_label = QLabel()
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        possible_paths = [
            os.path.join(parent_dir, "datas", "medulla.png"),
            os.path.join(current_dir, "..", "datas", "medulla.png")
        ]
        for logo_path in possible_paths:
            abs_path = os.path.abspath(logo_path)
            if os.path.exists(abs_path):
                pixmap = QPixmap(abs_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        22, 22,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    logo_label.setPixmap(scaled)
                    break
        logo_label.setFixedSize(24, 24)
        logo_label.setStyleSheet("background: transparent;")
        layout.addWidget(logo_label)

        # === Titre de la conversation (premier message utilisateur) ===
        title_label = QLabel(self.conversation.title)
        title_label.setStyleSheet("""
            color: #333;
            font-size: 14px;
            font-weight: normal;   /* pas en gras */
        """)
        layout.addWidget(title_label, 1)

        self.setLayout(layout)

        # === Style bouton transparent ===
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
            QWidget:hover {
                background-color: #E6E6E6;
            }
        """)


class CreateTicketDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create the ticket")
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)
        self.description = ""
        self.screenshot_path: str | None = None
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        desc_label = QLabel("Problem description *")
        desc_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        desc_label.setStyleSheet("color: #333;")
        layout.addWidget(desc_label)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(140)
        self.description_edit.setPlaceholderText("Describe your problem in detail...")
        self.description_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #4caf50;
            }
        """)
        layout.addWidget(self.description_edit)

        screenshot_layout = QHBoxLayout()
        self.screenshot_btn = QPushButton("📷 Screenshot")
        self.screenshot_btn.clicked.connect(self._choose_screenshot)
        self.screenshot_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                color: #495057;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
        """)
        
        screenshot_layout.addWidget(self.screenshot_btn)
        screenshot_layout.addStretch()
        layout.addLayout(screenshot_layout)

        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn = QPushButton("OK")
        
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)
        
        button_style = """
            QPushButton {
                padding: 12px 25px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                min-width: 80px;
            }
        """
        
        self.cancel_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #6c757d;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        self.ok_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #007bff;
                color: white;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addSpacing(5)
        button_layout.addWidget(self.ok_btn)
        layout.addLayout(button_layout)

    def _choose_screenshot(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Choose screenshot", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.screenshot_path = path
            self.screenshot_btn.setText("📷 Screenshot ✓")
            self.screenshot_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d4edda;
                    border: 2px solid #c3e6cb;
                    padding: 10px 20px;
                    border-radius: 6px;
                    color: #155724;
                    font-size: 13px;
                }
            """)

    def accept(self):
        desc = self.description_edit.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Validation", "Problem description is required.")
            return
        self.description = desc
        super().accept()

# ---------------------------
# Main Window
# ---------------------------
class MainWindow(QMainWindow):
    voice_text_ready = pyqtSignal(str) 
    ticket_updated = pyqtSignal(Ticket)

    def __init__(self, model: ChatModel):
        super().__init__()
        self.model = model
        self.current_view = "chats"
        self.setWindowTitle("medulla")
        self.resize(1200, 700)
        self._build_ui()
        self._connect_signals()
        self.model.ticket_updated.connect(lambda _t: self._populate_tickets())
        self.reply_ticket_id = None

        
        self._show_chats()
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        self.microphone = None       # sera fixé au premier clic
        self.stop_listening = None 
        self.voice_text_ready.connect(self.update_input_field)
        self.ticket_refresh_timer = QTimer(self)
        self.ticket_refresh_timer.setInterval(60_000)  # 60s
        self.ticket_refresh_timer.timeout.connect(self._refresh_ticket_statuses_from_glpi)
        self.ticket_refresh_timer.start()

    


    def _refresh_ticket_statuses_from_glpi(self):
        tickets = self.model.get_tickets()  
        if not tickets:
            return
        try:
            session = init_session()
            for t in tickets:
                try:
                    code = get_ticket_status(session, int(t.id))
                    # mappe le code GLPI en label UI
                    if code == 1: ui = "Open"
                    elif code in (2,3,4): ui = "In progress"
                    elif code == 5: ui = "Resolved"
                    elif code == 6: ui = "Closed"
                    else: ui = "Open"
                    self.model.update_ticket_status(t.id, ui)
                except Exception as e:
                    logger.warning(f"Impossible d'obtenir statut {t.id}: {e}")
            kill_session(session)
        except Exception as e:
            logger.warning(f"Erreur rafraîchissement GLPI: {e}")





    def update_input_field(self, text: str):
        """Met à jour le champ de saisie avec le texte reçu par reconnaissance vocale."""
        if hasattr(self, "input_field"):  # si ton champ existe
            self.input_field.setText(text)
        else:
            print("⚠ Aucun champ input_field défini pour afficher :", text)


    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._build_left_panel()
        main_layout.addWidget(self.left_panel)

        self._build_right_panel()
        main_layout.addWidget(self.right_panel)

        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)

    def _build_left_panel(self):
        self.left_panel = QWidget()
        self.left_panel.setObjectName("leftPanel")
        self.left_panel.setFixedWidth(300)

        # fond gris à l’extérieur
        self.left_panel.setStyleSheet("""
            #leftPanel { background-color: #F0F0F0; }
        """)

        layout = QVBoxLayout(self.left_panel)
        layout.setContentsMargins(15, 15, 15, 15)  # espace gris autour du conteneur
        layout.setSpacing(0)

        # CONTENEUR PRINCIPAL (fond blanc + bordure noire)
        main_container = QWidget()
        main_container.setObjectName("leftContainer")
        main_container.setStyleSheet("""
            #leftContainer {
            background-color: white;   /* intérieur blanc */
            border: 2px solid black;  /* bordure noire */
            border-radius: 8px;
            }
        """)

        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(5, 8, 5, 8)  # padding interne blanc
        container_layout.setSpacing(10)


      # Navigation buttons (Chats/Tickets)
        nav_widget = QWidget()
        nav_widget.setFixedHeight(60)
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(10)

        # Création des boutons avec vos icônes SVG
        import os

        # Vérification et chargement des icônes
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Remonter d'un niveau depuis views vers kiosk_interface, puis aller dans datas
        parent_dir = os.path.dirname(script_dir)
        chat_icon_path = os.path.join(parent_dir, "datas", "chat.svg")
        ticket_icon_path = os.path.join(parent_dir, "datas", "tickets.svg")


        self.chats_btn = QPushButton("Chats")
        if os.path.exists(chat_icon_path):
            self.chats_btn.setIcon(QIcon(chat_icon_path))
        self.chats_btn.setCheckable(True)
        self.chats_btn.setChecked(True)  # Chats sélectionné par défaut

        self.tickets_btn = QPushButton("Tickets")
        if os.path.exists(ticket_icon_path):
            self.tickets_btn.setIcon(QIcon(ticket_icon_path))
        self.tickets_btn.setCheckable(True)


                # Style des boutons chats et tickets
        nav_button_style = """
            QPushButton {
                background-color: #e8f5e8;
                border: 3px solid #8bc34a;
                padding: 10px 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                color: #4a7c59;
                width: 160px;
                height: 60px;
                text-align: center;
                icon-size: 20px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #d4f0d4;
                border-color: #7cb342;
            }
            QPushButton:checked {
                background-color: #8bc34a;
                color: white;
                border-color: #8bc34a;
            }
            QPushButton:checked:hover {
                background-color: #7cb342;
            }
            QPushButton:!checked {
                background-color: #f0f5f0;
                color: #666666;
                border-color: #cccccc;
            }
"""

        # Application du style
        self.chats_btn.setStyleSheet(nav_button_style)
        self.tickets_btn.setStyleSheet(nav_button_style)

        # Ajout des boutons au layout
        nav_layout.addWidget(self.chats_btn)
        nav_layout.addWidget(self.tickets_btn)
        nav_layout.addStretch()  # Pousse les boutons vers la gauche

        # Connexion des signaux pour gérer l'état exclusif
        def on_chats_clicked():
            if self.chats_btn.isChecked():
                self.tickets_btn.setChecked(False)
            else:
                self.chats_btn.setChecked(True)

        def on_tickets_clicked():
            if self.tickets_btn.isChecked():
                self.chats_btn.setChecked(False)
            else:
                self.tickets_btn.setChecked(True)

        self.chats_btn.clicked.connect(on_chats_clicked)
        self.tickets_btn.clicked.connect(on_tickets_clicked)
                
        for btn in [self.chats_btn, self.tickets_btn]:
            btn.setCheckable(True)
            btn.setStyleSheet(nav_button_style)
            nav_layout.addWidget(btn)
        
        self.chats_btn.setChecked(True)
        container_layout.addWidget(nav_widget)

        # For Chats view: Add action buttons
        self.action_buttons_widget = QWidget()
        action_layout = QVBoxLayout(self.action_buttons_widget)
        action_layout.setContentsMargins(5, 0, 5, 10)
        action_layout.setSpacing(5)
        
      # Chargement des icônes SVG pour les boutons d'action
        parent_dir = os.path.dirname(script_dir)
        plus_icon_path = os.path.join(parent_dir, "datas", "plus.svg")  # Icône + pour nouveau
        history_icon_path = os.path.join(parent_dir, "datas", "machine.svg")  # Vous avez déjà machine.svg
        search_icon_path = os.path.join(parent_dir, "datas", "recherche.svg")  # Icône de recherche

        # New conversation button
        self.new_conversation_btn = QPushButton("New conversation")
        if os.path.exists(plus_icon_path):
            self.new_conversation_btn.setIcon(QIcon(plus_icon_path))
        self.new_conversation_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #8bc34a;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 14px;
                color: #495057;
                text-align: left;
                icon-size: 18px;
            }
            QPushButton:hover {
                background-color: #e9f7e9;
            }
        """)
        action_layout.addWidget(self.new_conversation_btn)

        # Conversation history button
        self.conversation_history_btn = QPushButton("Conversation history")
        if os.path.exists(history_icon_path):
            self.conversation_history_btn.setIcon(QIcon(history_icon_path))
        self.conversation_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #8bc34a;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 14px;
                color: #495057;
                text-align: left;
                icon-size: 18px;
            }
            QPushButton:hover {
                background-color: #e9f7e9;
            }
        """)
        action_layout.addWidget(self.conversation_history_btn)

        # Search chats button
        self.search_chats_btn = QPushButton("Search chats")
        if os.path.exists(search_icon_path):
            self.search_chats_btn.setIcon(QIcon(search_icon_path))
        self.search_chats_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #8bc34a;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 14px;
                color: #495057;
                text-align: left;
                icon-size: 18px;
            }
            QPushButton:hover {
                background-color: #e9f7e9;
            }
        """)
        action_layout.addWidget(self.search_chats_btn)
        action_layout.addStretch()
        container_layout.addWidget(self.action_buttons_widget)
      
        self.item_list = QListWidget()
      

        self.item_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.item_list.setFrameStyle(QFrame.Shape.NoFrame)
        self.item_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: none;
            }
            QListWidget::item {
                padding: 0px;
                border-bottom: 1px solid #f0f0f0;
                background-color: white;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
    
        # Ajouter la liste au conteneur avec bordure
        container_layout.addWidget(self.item_list)
        # Ajouter le conteneur principal au layout du panneau
        layout.addWidget(main_container)

    
    def _build_right_panel(self):
        self.right_panel = QWidget()
        self.right_panel.setObjectName("rightPanel")
        
    
        self.right_panel.setStyleSheet("""
            #rightPanel { background-color: #F0F0F0; }
        """)

        layout = QVBoxLayout(self.right_panel)
        layout.setContentsMargins(15, 15, 15, 15)  # espace gris autour du conteneur
        layout.setSpacing(0)

        # CONTENEUR PRINCIPAL (fond blanc + bordure noire)
        main_container = QWidget()
        main_container.setObjectName("rightContainer")
        main_container.setStyleSheet("""
             #rightContainer {
                background-color: white;
                border: 2px solid black;  /* bordure noire */            
                border-radius: 15px;
            }
        """)

        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(2, 2, 2, 2)
        container_layout.setSpacing(0)

        self._build_chat_area()
        container_layout.addWidget(self.chat_scroll_area)

        self._build_input_area()
        container_layout.addWidget(self.input_widget)
        
        # Ajouter le conteneur principal au layout du panneau
        layout.addWidget(main_container)

    def _build_chat_area(self):
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        self.chat_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(20)
        self.chat_layout.setContentsMargins(25, 25, 25, 25)
        
        self.chat_scroll_area.setWidget(self.chat_widget)

    def _build_input_area(self):
        self.input_widget = QWidget()
        self.input_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: none;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        input_layout = QVBoxLayout(self.input_widget)
        input_layout.setContentsMargins(15, 10, 15, 15)
        input_layout.setSpacing(15)
        
        # Bouton "Create a ticket" 
        self.create_ticket_btn = QPushButton("Create a ticket")
        self.create_ticket_btn.setFixedHeight(48)
        self.create_ticket_btn.setStyleSheet("""
            QPushButton {
                padding: 15px 18px;
                border: none;
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 #00bcd4, stop:1 #2196f3);
                color: white;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 #00acc1, stop:1 #1976d2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 #0097a7, stop:1 #1565c0);
            }
        """)
        
        # MASQUER le bouton au début
        self.create_ticket_btn.hide()
        
        # Zone de saisie principale
        input_area = QWidget()
        input_area.setFixedHeight(48)
        input_area.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border-radius: 15px;
                border: 2px solid #e0e0e0;
            }
            QWidget:focus-within {
                border: 2px solid #4caf50;
            }
        """)
        input_area_layout = QHBoxLayout(input_area)
        input_area_layout.setContentsMargins(10, 5, 10, 5)
        input_area_layout.setSpacing(10)

        # Champ de saisie
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.setFixedHeight(48)
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 13px 13px;
                border: none;
                border-radius: 15px;
                background-color: transparent;
                font-size: 16px;
                color: #333;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        
        # Connecter l'événement focus pour changer la bordure du conteneur parent
        self.input_field.focusInEvent = self._on_input_focus_in
        self.input_field.focusOutEvent = self._on_input_focus_out
        self.input_area = input_area  # Garder référence pour le style
        
        # Bouton microphone
        import os
    
        # Récupérer le chemin du dossier actuel (Views)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Construire le chemin vers lr logo (Datas/micro.png)
        self.normal_mic_icon = os.path.join(base_dir, "..", "Datas", "micro.png")
        self.red_mic_icon = os.path.join(base_dir, "..", "Datas", "micro_red.png")

        # Bouton micro
        self.mic_btn = QPushButton("")
        self.mic_btn.setIcon(QIcon( self.normal_mic_icon ))
        self.mic_btn.setIconSize(QSize(30, 30))   # ajuste la taille

        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
               
            }
            QPushButton:hover {
                background-color: Transparent;
            }
            QPushButton:pressed {
                background-color: TRANSPARENT;
            }
        """)


        # Bouton envoi 
        import os


        # Chemin vers l’icône d’envoi
        base_dir = os.path.dirname(os.path.abspath(__file__))
        send_icon_path = os.path.join(base_dir, "..", "Datas", "envoi.png")

        # Bouton envoi (juste icône)
        self.send_btn = QPushButton("")
        self.send_btn.setIcon(QIcon(send_icon_path))
        self.send_btn.setIconSize(QSize(30, 30))   

        self.send_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background: transparent;
            }
            QPushButton:pressed {
                background: transparent;
            }
        """)

        input_area_layout.addWidget(self.input_field)
        input_area_layout.addWidget(self.mic_btn)
        input_area_layout.addWidget(self.send_btn)

        # Ajout des widgets dans l'ordre: input puis ticket (ticket en bas)
        input_layout.addWidget(input_area)
        input_layout.addWidget(self.create_ticket_btn)

    def _on_input_focus_in(self, event):
        """Changer la bordure en vert quand le champ de saisie a le focus"""
        self.input_area.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border-radius: 15px;
                border: 2px solid #4caf50;
            }
        """)
        # Appeler la méthode originale
        QLineEdit.focusInEvent(self.input_field, event)

    def _on_input_focus_out(self, event):
        """Remettre la bordure normale quand le champ perd le focus"""
        self.input_area.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border-radius: 15px;
                border: 2px solid #e0e0e0;
            }
        """)
        # Appeler la méthode originale
        QLineEdit.focusOutEvent(self.input_field, event)

   

    def _scroll_to_bottom(self):
        """Scroller automatiquement vers le bas"""
        scrollbar = self.chat_scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
