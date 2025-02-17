from selenium_stealth import stealth
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random
import os

# Lista de user-agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
]

start_time = time.time()

# Configuração do driver com headers personalizados e stealth
service = Service(ChromeDriverManager().install())
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Aplica técnicas de stealth
stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

# Função para rolar a página suavemente
def smooth_scroll():
    last_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    scroll_step = random.randint(200, 400)  # Passos menores de scroll
    
    while True:
        # Rola gradualmente com velocidade variável
        for _ in range(random.randint(2, 4)):  # Número de "etapas" por scroll
            current_position += scroll_step
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.3, 0.7))  # Tempo entre os micro-scrolls
        
        # Verifica se chegou ao final
        new_height = driver.execute_script("return document.body.scrollHeight")
        if current_position >= new_height:
            break
            
        # Atualiza a altura se a página cresceu
        if new_height > last_height:
            last_height = new_height
            
        # Pausa aleatória entre os grupos de scroll
        time.sleep(random.uniform(0.5, 1.5))

# Lista para armazenar todos os dados coletados
dados_imoveis = []

# Loop para iterar sobre as páginas
for pagina in range(1, 10):  # Páginas 1, 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9
    try:
        print(f"Coletando dados da página {pagina}...")
        
        # URL da página atual
        url_base = f"https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/?transacao=venda&onde=,Rio%20de%20Janeiro,Rio%20de%20Janeiro,,,,,city,BR%3ERio%20de%20Janeiro%3ENULL%3ERio%20de%20Janeiro,-22.906847,-43.172897,&tipos=apartamento_residencial,studio_residencial,kitnet_residencial,casa_residencial,sobrado_residencial,condominio_residencial,casa-vila_residencial,cobertura_residencial,flat_residencial,loft_residencial,lote-terreno_residencial,granja_residencial&pagina={pagina}"
        driver.get(url_base)

        # Espera inicial para carregar
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "BaseCard_card__content__pL2Vc.w-full.p-3"))
            )
        except TimeoutException:
            print(f"Erro: A página {pagina} não carregou corretamente. Pulando para a próxima página...")
            continue

        # Pausa aleatória entre as páginas
        time.sleep(random.uniform(5, 10))

        # Primeiro scroll para carregar todos os elementos
        smooth_scroll()

        # Coleta todos os cards após o scroll
        cards = driver.find_elements(By.CLASS_NAME, "BaseCard_card__content__pL2Vc.w-full.p-3")

        # Verifica se há cards na página
        if not cards:
            print(f"Nenhum card encontrado na página {pagina}. Pulando para a próxima página...")
            continue

        # Scroll fino para cada card individualmente
        for index, card in enumerate(cards):
            try:
                # Scroll suave para o card
                driver.execute_script("""
                    arguments[0].scrollIntoView({
                        behavior: 'smooth',
                        block: 'center',
                        inline: 'center'
                    });
                """, card)
            
                # Tempo de espera variável e progressivo
                wait_time = random.uniform(0.5, 1.2) * (index/len(cards) + 0.5)
                time.sleep(wait_time)
            
                # Atualiza a lista de cards periodicamente
                if index % 5 == 0:
                    cards = driver.find_elements(By.CLASS_NAME, "BaseCard_card__content__pL2Vc.w-full.p-3")
            
                # Extração de dados
                try:
                    bairro_element = card.find_element(By.CLASS_NAME, "truncate.text-2.font-semibold.text-neutral-120")
                    bairro_text = bairro_element.text.split(",")[0].strip()
                except:
                    bairro_text = "N/A"

                try:
                    tipo_imovel_element = driver.find_element(By.CSS_SELECTOR, ".truncate.pb-0-5.text-1-5.text-neutral-110.md\\:text-1-75")
                    tipo_imovel_text = tipo_imovel_element.text.split(" ")[0]
                except:
                    tipo_imovel_text = "N/A"

                try:
                    area_imovel_element = card.find_element(By.CSS_SELECTOR, "[data-cy='rp-cardProperty-propertyArea-txt']")
                    area_imovel_text = area_imovel_element.text.strip()
                    area_match = re.findall(r"\d+", area_imovel_text)
                    area_imovel_numero = "-".join(area_match) if area_match else "N/A"
                except:
                    area_imovel_numero = "N/A"

                try:
                    n_quartos_element = card.find_element(By.CSS_SELECTOR, "[data-cy='rp-cardProperty-bedroomQuantity-txt']")
                    n_quatos_text = n_quartos_element.text.strip()
                except:
                    n_quatos_text = "N/A"
        
                try:
                    n_banheiros_element = card.find_element(By.CSS_SELECTOR, "[data-cy='rp-cardProperty-bathroomQuantity-txt']")
                    n_banheiros_text = n_banheiros_element.text.strip()
                except:
                    n_banheiros_text = "N/A"

                try:
                    n_vagas_element = card.find_element(By.CSS_SELECTOR, "[data-cy='rp-cardProperty-parkingSpacesQuantity-txt']")
                    n_vagas_text = n_vagas_element.text.strip()
                except:
                    n_vagas_text = "N/A"

                try:
                    preco_element = card.find_element(By.CSS_SELECTOR, "p.l-text.l-text--weight-bold")
                    preco_text = preco_element.text.strip()
                    preco_match = re.search(r"[\d\.,]+", preco_text)
                    preco_numero = preco_match.group().replace(",", "") if preco_match else "N/A"
                except:
                    preco_numero = "N/A"

                try:
                    cond_iptu_element = card.find_element(By.CLASS_NAME, "l-text.l-u-color-neutral-44.l-text--variant-body-small.l-text--weight-regular.text-balance")
                    cond_iptu_text = cond_iptu_element.text.strip()
                    condominio_match = re.search(r"Cond\. R\$ ([\d,.]+)", cond_iptu_text)
                    iptu_match = re.search(r"IPTU R\$ ([\d,.]+)", cond_iptu_text)
                    condominio_valor = condominio_match.group(1) if condominio_match else "N/A"
                    iptu_valor = iptu_match.group(1) if iptu_match else "N/A"
                except:
                    condominio_valor = "N/A"
                    iptu_valor = "N/A"
            
                # Verifica se o imóvel já foi coletado
                imovel_id = f"{bairro_text}-{tipo_imovel_text}-{area_imovel_numero}-{preco_numero}"
                if imovel_id not in set([f"{item['bairro']}-{item['tipo']}-{item['area']}-{item['preco']}" for item in dados_imoveis]):
                    dados_imoveis.append({
                        "bairro": bairro_text,
                        "tipo": tipo_imovel_text,
                        "area": area_imovel_numero,
                        "qtd_quartos": n_quatos_text,
                        "qtd_banheiros": n_banheiros_text,
                        "qtd_vagas_garagem": n_vagas_text,
                        "preco": preco_numero,
                        "cond": condominio_valor,
                        "iptu": iptu_valor
                    })

            except Exception as e:
                print(f"Erro no card {index} da página {pagina}: {str(e)}")
                continue

    except NoSuchWindowException:
        print("Erro: Navegador fechado ou bloqueado. Reiniciando o navegador...")
        driver.quit()  # Fecha o navegador atual
        driver = webdriver.Chrome(service=service, options=chrome_options)  # Reinicia o navegador
        continue  # Volta para o início do loop e tenta novamente

# Finaliza a contagem do tempo
end_time = time.time()
execution_time = end_time - start_time  # Calcula o tempo total
minutes = int(execution_time // 60)
seconds = int(execution_time % 60)

# Salvar os dados de forma incremental
if os.path.exists("dados_zap_imoveis.csv"):
    df_existente = pd.read_csv("dados_zap_imoveis.csv")
else:
    df_existente = pd.DataFrame()

df_novos_dados = pd.DataFrame(dados_imoveis)
df_final = pd.concat([df_existente, df_novos_dados], ignore_index=True)
df_final.drop_duplicates(inplace=True)
df_final.to_csv("dados_zap_imoveis.csv", index=False)

print(f"Encontrados {len(dados_imoveis)} imóveis")  # Verifica se encontrou algo
print("Dados salvos de forma incremental com sucesso!")
print(f"Tempo total de execução: {minutes}:{seconds:02d} minutos")  # Exibe o tempo total formatado
driver.quit()