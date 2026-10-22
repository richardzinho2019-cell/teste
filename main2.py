import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 1. Configura as opções do Chrome para rodar em segundo plano (Headless)
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Oculta a janela do navegador
chrome_options.add_argument("--window-size=1366,768")
chrome_options.add_argument("--log-level=3")  # Minimiza avisos do sistema no terminal

# 2. Habilita o log de performance para capturar os headers de rede de forma nativa
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Inicializa o navegador invisível usando o Selenium padrão
driver = webdriver.Chrome(options=chrome_options)

try:
    print("Acessando o YouTube em segundo plano...")
    driver.get("https://youtube.com")
    
    # Aguarda o carregamento dos elementos e a geração de cookies por scripts
    time.sleep(4)
    
    # ==========================================
    # CAPTURANDO OS HEADERS (NATIVO DO CHROME)
    # ==========================================
    print("\n" + "="*40)
    print("=== HEADERS DA RESPOSTA (YOUTUBE) ===")
    print("="*40)
    
    logs = driver.get_log("performance")
    headers_encontrados = False
    
    for entry in logs:
        log_data = json.loads(entry["message"])["message"]
        
        # Filtra pelas respostas de rede recebidas
        if log_data["method"] == "Network.responseReceived":
            response = log_data["params"]["response"]
            
            # Garante que estamos pegando os headers da página principal do YouTube
            if "youtube.com" in response["url"] and response["mimeType"] == "text/html":
                headers = response.get("headers", {})
                for chave, valor in headers.items():
                    print(f"{chave}: {valor}")
                headers_encontrados = True
                break  # Para após encontrar os cabeçalhos principais
                
    if not headers_encontrados:
        print("Não foi possível extrair os headers do tráfego principal.")

    # ==========================================
    # CAPTURANDO OS COOKIES
    # ==========================================
    print("\n" + "="*40)
    print("=== COOKIES ARMAZENADOS NO NAVEGADOR ===")
    print("="*40)
    
    cookies = driver.get_cookies()
    if cookies:
        for cookie in cookies:
            print(f"Nome: {cookie['name']}")
            print(f"Valor: {cookie['value']}")
            print(f"Domínio: {cookie.get('domain')}")
            print("-" * 30)
    else:
        print("Nenhum cookie foi gerado na sessão.")

finally:
    # Garante o encerramento do processo oculto do Chrome
    driver.quit()
    print("\nSessão encerrada com sucesso.")
