import os
from playwright.sync_api import sync_playwright
import requests

# --- CONFIGURAÇÕES ESPECÍFICAS PARA A COPAG ---
URL_PRODUTO = "https://www.copagloja.com.br/blister-triplo-pokemon-me05-escuridao-absoluta/p"
# Seletor do botão de compra/indisponível na Copag Loja
SELETOR_CSS = ".buy-button, .out-of-stock, .product-unavailable, button.buy-button" 

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def enviar_alerta_telegram(mensagem):
    if not TELEGRAM_TOKEN:
        print(f"[ALERTA SEM TELEGRAM]: {mensagem}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro Telegram: {e}")

def verificar_estoque():
    with sync_playwright() as p:
        # Usamos user_agent para o site não bloquear o robô facilmente
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        try:
            print(f"Acessando: {URL_PRODUTO}")
            page.goto(URL_PRODUTO, timeout=60000)
            
            # Aguarda a página carregar os elementos principais
            page.wait_for_load_state("domcontentloaded")
            
            # Verifica se encontra algum texto indicando indisponibilidade na página inteira ou no botão
            pagina_texto = page.inner_text("body").lower()
            
            # Termos comuns de produto esgotado em lojas virtuais brasileiras
            termos_esgotado = ["avise-me", "indisponível", "esgotado", "produto indisponível"]
            
            esgotado = any(termo in pagina_texto for termo in termos_esgotado)
            
            # Tenta achar o botão de compra especificamente
            botao_comprar_existe = page.locator(".buy-button, button:has-text('Comprar')").count() > 0

            print(f"Texto de esgotado detectado? {esgotado}")
            print(f"Botão de compra visível? {botao_comprar_existe}")
            
            # Se não está esgotado OU se o botão de comprar apareceu, mandamos alerta!
            if not esgotado or botao_comprar_existe:
                mensagem = f"🚨 *POKÉMON DISPONÍVEL NA COPAG!*\n\nCorre lá:\n{URL_PRODUTO}"
                enviar_alerta_telegram(mensagem)
                print(">>> PRODUTO DISPONÍVEL! Alerta disparado. <<<")
            else:
                print("Produto ainda indisponível/esgotado.")
                
        except Exception as e:
            print(f"Erro ao acessar a página: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verificar_estoque()
