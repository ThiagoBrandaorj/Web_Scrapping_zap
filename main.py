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

# Configuração do driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

url_base = "https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/?transacao=venda&pagina=1"
driver.get(url_base)

def fecha_popups():
    """Fecha popups, se existirem."""
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='overlay-close-modal']"))
        ).click()
    except:
        pass

def coleta_suites():
    """Coleta o número de suítes da página do imóvel."""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='ldp-propertyFeatures']"))
        )
        
        suites = "N/A"
        try:
            features = driver.find_element(By.CSS_SELECTOR, "[data-cy='ldp-propertyFeatures']").text
            suite_match = re.search(r'(\d+)\s+suítes?', features, re.IGNORECASE)
            if suite_match:
                suites = suite_match.group(1)
        except:
            pass

        return {'suites': suites}

    except Exception as e:
        print(f"Erro ao coletar suítes: {str(e)}")
        return None

# Execução principal
try:
    # Espera a página carregar e fecha popups
    time.sleep(5)
    fecha_popups()

    # Seleciona os cards dos imóveis
    cards = driver.find_elements(By.CSS_SELECTOR, ".BaseCard_card__content__pL2Vc.w-full.p-3")
    print(f"Encontrados {len(cards)} cards")

    for index, card in enumerate(cards[:2]):  # Teste com os 2 primeiros cards
        try:
            # Scroll até o card
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})", card)

            # Espera o card ser clicável e clica nele
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(card))
            ActionChains(driver).move_to_element(card).pause(0.5).click().perform()

            # Alterna para a nova aba
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[1])

            # Coleta número de suítes
            detalhes = coleta_suites()
            print(f"Card {index+1}: {detalhes}")

            # Fecha a aba e volta para a principal
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # Pausa aleatória entre execuções
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"Erro no card {index+1}: {str(e)}")
            continue

finally:
    driver.quit()
