import os
from playwright.sync_api import sync_playwright
import requests

# Pegando os links de variáveis de ambiente (ou coloque direto aqui se preferir)
URL_PRODUTO = "https://www.atacadocollections.com/produto/funko-pop-football-bar-a-jules-kound-109" 
SELETOR_CSS = "#buy-button buy-button-ref"                  

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def enviar_alerta_telegram(mensagem):
    if not TELEGRAM_TOKEN:
        print(f"[ALERTA]: {mensagem}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro Telegram: {e}")

def verificar_estoque():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(URL_PRODUTO, timeout=60000)
            page.wait_for_selector(SELETOR_CSS, timeout=10000)
            texto = page.locator(SELETOR_CSS).inner_text().lower()
            print(f"Status encontrado: '{texto}'")
            
            if "esgotado" not in texto and "indisponível" not in texto:
                enviar_alerta_telegram(f"🚨 *DISPONÍVEL!*\n\n{URL_PRODUTO}")
                print("Disponível! Alerta enviado.")
            else:
                print("Ainda indisponível.")
        except Exception as e:
            print(f"Erro ao acessar: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verificar_estoque()
