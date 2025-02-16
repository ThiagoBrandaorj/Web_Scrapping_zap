from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import re

def human_delay(min_sec=1, max_sec=3):
    """Atraso humano com variação aleatória"""
    time.sleep(random.uniform(min_sec, max_sec))

# Configuração do driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Abrir a página de listagem
url_base = "https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/?transacao=venda&pagina=1"
driver.get(url_base)

# Esperar a página carregar
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CLASS_NAME, "ListingCard_result-card__Pumtx.ListingCard_result-card__highlight__UgAvU.ListingCard_result-card__highlight--super__8WmjB"))
)

def human_scroll():
    """Scroll mais humano com movimentos variados"""
    scroll_passes = random.randint(3, 5)
    for _ in range(scroll_passes):
        driver.execute_script("window.scrollBy(0, window.innerHeight/1.5);")
        human_delay(0.5, 1.5)
        # Movimento de scroll reverso aleatório
        if random.random() > 0.7:
            driver.execute_script("window.scrollBy(0, -window.innerHeight/3);")
            human_delay(0.3, 0.8)

# Scroll para carregar todos os cards
human_scroll()

# Coletar todos os links dos imóveis
cards = driver.find_elements(By.CLASS_NAME, "ListingCard_result-card__Pumtx.ListingCard_result-card__highlight__UgAvU.ListingCard_result-card__highlight--super__8WmjB")
links = [card.get_attribute("href") for card in cards if card.get_attribute("href")]

print(f"Encontrados {len(links)} imóveis.")

# Iterar sobre cada link para extrair informações
for link in links:
    try:
        # Abrir a página de detalhes
        driver.get(link)
        
        # Esperar a página carregar
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='ldp-propertyFeatures-txt']"))
        )
        
        # Extrair características
        features = driver.find_element(By.CSS_SELECTOR, "[data-cy='ldp-propertyFeatures-txt']").text
        
        # Buscar suítes com regex
        suites = re.findall(r'(\d+[\-\+]?\d*)\s+(?:suíte|suites|suite|suítes)', features, re.IGNORECASE)
        
        if suites:
            print(f"\n Imóvel com suítes encontrado: {link}")
            print(f"   Quantidade de suítes: {', '.join(suites)}")
        else:
            print(f"\n Nenhuma suíte encontrada em: {link}")
            
    except Exception as e:
        print(f"\n Erro ao processar o imóvel {link}: {str(e)[:70]}...")
    
    # Espera entre as páginas
    human_delay()

# Fechar o driver
driver.quit()