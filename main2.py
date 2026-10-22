import time
# Note que importamos do seleniumwire, e não do selenium comum
from seleniumwire import webdriver 
from selenium.webdriver.chrome.options import Options

# Configura o Chrome para rodar 100% em segundo plano (Headless)
chrome_options = Options()
chrome_options.add_argument("--headless=new") # Garante o modo invisível moderno
chrome_options.add_argument("--window-size=1366,768") # Define tamanho fantasma da tela

# Inicializa o navegador invisível
driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://www.youtube.com")
    time.sleep(3) # Aguarda carregar as requisições iniciais
    
    print("--- HEADERS CAPTURADOS PELO SELENIUM ---")
    # Varre as requisições feitas pelo navegador em segundo plano
    for request in driver.requests:
        if request.response:
            print(f"URL: {request.url}")
            print(f"Status Code: {request.response.status_code}")
            print("Headers de Resposta:")
            for chave, valor in request.response.headers.items():
                print(f"  {chave}: {valor}")
            print("-" * 50)
            break # Remove o break se quiser listar os headers de TODOS os elementos carregados (imagens, scripts, etc.)

finally:
    driver.quit()
