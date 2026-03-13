"""
MODUŁ USŁUGI: MAINTENANCE (UTRZYMANIE RUCHU)
--------------------------------------------
Rola: Automatyzacja zadań w tle
"""

import sqlite3
import os
import time
import smtplib
import threading
from datetime import datetime, timedelta
import pytz  

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from services import config 

# Definicje stałych lokalnych
SOURCE_DB = "fundacja.db"      
BACKUP_DIR = "backups"          

def czy_backup_zrobiony_dzisiaj():
    """
    Sprawdza integralność procesu backupu.
    Cel: Zapobieganie duplikacji maili w przypadku restartu serwera w ciągu dnia.
    
    Zwraca:
        bool: True jeśli plik z dzisiejszą datą już istnieje, False w przeciwnym razie.
    """
    if not os.path.exists(BACKUP_DIR):
        return False
        
    dzis_str = datetime.now().strftime("%Y-%m-%d")
    
    for plik in os.listdir(BACKUP_DIR):
        if plik.startswith(f"backup_{dzis_str}"):
            return True
    return False

def wyslij_backup_mailem(sciezka_pliku, nazwa_pliku):
    """
    Wysyła binarny plik bazy danych jako załącznik e-mail.
    Korzysta ze standardu MIME (Multipurpose Internet Mail Extensions).
    """
    print(f"📧 [MAINTENANCE] Przygotowanie wysyłki SMTP: {nazwa_pliku}...")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = config.EMAIL_SENDER
        msg['To'] = config.EMAIL_BACKUP_TARGET
        msg['Subject'] = f"Fundacja - Backup Systemowy: {nazwa_pliku}"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body = f"Raport automatyczny.\nUtworzono kopię bezpieczeństwa bazy danych.\nSygnatura czasowa: {timestamp}"
        msg.attach(MIMEText(body, 'plain'))
        
        with open(sciezka_pliku, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        
        part.add_header("Content-Disposition", f"attachment; filename= {nazwa_pliku}")
        msg.attach(part)
        
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls() 
        
        clean_pass = config.EMAIL_PASSWORD.replace(" ", "").strip()
        server.login(config.EMAIL_SENDER, clean_pass)
        
        server.sendmail(config.EMAIL_SENDER, config.EMAIL_BACKUP_TARGET, msg.as_string())
        server.quit()
        
        print("✅ [MAINTENANCE] Backup wysłany pomyślnie.")
        return True
        
    except Exception as e:
        print(f"❌ [MAINTENANCE ERROR] Błąd wysyłki SMTP: {e}")
        return False

def wykonaj_backup():
    """
    Procedura wykonawcza: Kopia lokalna -> Wysyłka -> Sprzątanie.
    Używa mechanizmu 'Online Backup API' z SQLite.
    """
    if not os.path.exists(SOURCE_DB):
        print("⚠️ [MAINTENANCE] Brak pliku bazy źródłowej. Backup pominięty.")
        return
        
    if not os.path.exists(BACKUP_DIR): 
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nazwa = f"backup_{timestamp}.db"
    sciezka = os.path.join(BACKUP_DIR, nazwa)

    try:
        # --- SEKCJA KRYTYCZNA: KOPIOWANIE DANYCH ---
        conn_src = sqlite3.connect(SOURCE_DB)
        conn_dst = sqlite3.connect(sciezka)
        
        # Metoda .backup() automatycznie zarządza blokadami (locks).
        conn_src.backup(conn_dst)
        
        conn_dst.close()
        conn_src.close()
        # -------------------------------------------
        
        wyslij_backup_mailem(sciezka, nazwa)
        
        if os.path.exists(sciezka):
            os.remove(sciezka)
            print("🧹 [MAINTENANCE] Usunięto lokalny plik tymczasowy.")
            
    except Exception as e:
        print(f"❌ [MAINTENANCE CRITICAL] Błąd procesu backupu: {e}")

def run_scheduler():
    """
    Logika harmonogramu (Scheduler Logic).
    Działa w pętli nieskończonej wewnątrz wątku w tle.
    """
    tz_pl = pytz.timezone('Europe/Warsaw')
    print("🕒 [SCHEDULER] Wątek harmonogramu uruchomiony.")
    
    while True:
        # 1. Obliczenie czasu celu 
        now = datetime.now(tz_pl)
        target_hour = config.BACKUP_HOUR
        
        # Ustawiamy cel na dzisiaj na godzinę z configu 
        target = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        
        # 2. Logika decyzyjna
        if now > target:
            if not czy_backup_zrobiony_dzisiaj():
                print(f"⚠️ [SCHEDULER] Wykryto brak dzisiejszego backupu. Uruchamiam procedurę awaryjną...")
                wykonaj_backup()
            
            target += timedelta(days=1)
        
        seconds_to_wait = (target - datetime.now(tz_pl)).total_seconds()
        
        if seconds_to_wait < 0: seconds_to_wait = 10
        
        hours = seconds_to_wait / 3600
        print(f"💤 [SCHEDULER] Uśpienie wątku na {hours:.2f}h (do {target.strftime('%d-%m %H:%M')})")
        
        # 4. Usypiamy wątek. W tym czasie nie zużywa on zasobów procesora (CPU).
        time.sleep(seconds_to_wait)

def start_background_backup():
    """
    Punkt wejścia (Entry Point) dla systemu backupu.
    Tworzy i uruchamia wątek typu Daemon.
    
    Daemon Thread: Wątek, który jest zabijany automatycznie, gdy główny proces
    aplikacji (Streamlit) zostaje zamknięty. Zapobiega to 'wiszącym procesom'.
    """
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()