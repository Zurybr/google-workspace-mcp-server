#!/usr/bin/env python3
import os
import sys
import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None
    token_path = os.path.expanduser('~/.config/gogcli/token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            cred_paths = ['credentials.json', os.path.expanduser('~/.config/gogcli/credentials.json')]
            cred_file = None
            for path in cred_paths:
                if os.path.exists(path):
                    cred_file = path
                    break
            if not cred_file:
                raise FileNotFoundError("No se encontró credentials.json")
            flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def send_html_email(to, subject, html_body):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    message = EmailMessage()
    message.set_content('Plain text fallback - usa un cliente compatible con HTML')
    message.add_alternative(html_body, subtype='html')
    message['To'] = to
    message['Subject'] = subject
    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': encoded}).execute()
    return result

html = '''<!DOCTYPE html><html><body><h1>Hola desde Claude Code</h1><p>Este es un correo de <strong>prueba</strong> con HTML.</p><ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul><p style="color: #1a73e8;">Texto azul</p><p style="color: #d93025;">Texto rojo</p><a href="https://github.com">Enlace a GitHub</a><hr><p><em>Enviado desde Python Gmail API</em></p></body></html>'''

result = send_html_email('brandom2ledesma@gmail.com', 'Test HTML desde Python', html)
print(f"Enviado! ID: {result['id']}")
