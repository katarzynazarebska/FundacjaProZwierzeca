"""
MODUŁ USŁUGI: EMAIL SERVICE
---------------------------
Rola: Wrapper (opakowanie) dla biblioteki 'smtplib'.
Zadanie: Dostarczenie prostego interfejsu do wysyłania wiadomości e-mail
bez konieczności powtarzania kodu konfiguracyjnego w innych miejscach aplikacji.

"""

import smtplib
from email.mime.text import MIMEText
from services import config 

def wyslij_email_resetu(odbiorca, kod_resetu):
    """
    Funkcja biznesowa: Wysyłka kodu weryfikacyjnego (2FA) do resetu hasła.
    
    Argumenty:
        odbiorca (str): Adres e-mail użytkownika.
        kod_resetu (str): 6-cyfrowy token wygenerowany w crud.py.
    
    Zwraca:
        tuple (bool, str): Status operacji (Sukces/Błąd) oraz komunikat dla użytkownika.
    """
    
    # 1. Przygotowanie nagłówków i treści wiadomości
    temat = "Fundacja - Reset Hasła"
    

    tresc = f"""
    Witaj!
    
    System Fundacji otrzymał zgłoszenie resetu hasła.
    Twój jednorazowy kod weryfikacyjny to:
    
    {kod_resetu}
    
    Wpisz ten kod w aplikacji, aby zdefiniować nowe hasło.
    Ważność kodu: Bezterminowo (do momentu wygenerowania nowego).
    """

    try:
        # 2. Tworzenie obiektu MIMEText
        msg = MIMEText(tresc, 'plain', 'utf-8')
        msg['Subject'] = temat
        msg['From'] = config.EMAIL_SENDER     
        msg['To'] = odbiorca

        # 3. Nawiązywanie połączenia z serwerem SMTP
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        
        # 4. Szyfrowanie połączenia (TLS - Transport Layer Security)
        server.starttls() 
        
        # 5. Autentykacja (Logowanie)
        clean_password = config.EMAIL_PASSWORD.replace(" ", "").strip()
        server.login(config.EMAIL_SENDER, clean_password)
        
        # 6. Fizyczna wysyłka
        server.sendmail(config.EMAIL_SENDER, odbiorca, msg.as_string())
        
        # 7. Zamknięcie sesji
        server.quit()
        
        print(f"✅ [EMAIL SERVICE] Pomyślnie wysłano kod do: {odbiorca}")
        return True, "Kod weryfikacyjny został wysłany na Twój e-mail."
        
    except smtplib.SMTPAuthenticationError:
        print("❌ [EMAIL ERROR] Błąd autoryzacji SMTP. Sprawdź plik services/config.py.")
        return False, "Błąd serwera pocztowego (Autoryzacja)."
        
    except Exception as e:
        print(f"❌ [EMAIL ERROR] Nieoczekiwany wyjątek: {e}")
        return False, "Wystąpił błąd podczas łączenia z serwerem pocztowym."