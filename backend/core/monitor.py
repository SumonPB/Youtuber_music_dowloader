from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def iniciar_monitor():
    """Monitor optimizado para evitar duplicados"""
    # Configuración de Brave
    brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    chromedriver_path = os.path.join(os.getcwd(), "backend", "core", "chromedriver.exe")
    
    options = Options()
    options.binary_location = brave_path
    options.add_argument("--disable-notifications")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # Usar perfil existente
    user_data = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data')
    options.add_argument(f"user-data-dir={user_data}")
    options.add_argument("profile-directory=Default")

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get("https://www.youtube.com")
        print("🔍 Monitoreando YouTube...")
        ultima_url = None
        
        while True:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
            )
            current_url = driver.current_url
            
            if "watch?v=" in current_url:
                url_limpia = current_url.split('&list=')[0].split('&t=')[0]
                
                # Evitar duplicados consecutivos
                if url_limpia != ultima_url:
                    print(f"🎵 URL detectada: {url_limpia}")
                    ultima_url = url_limpia
                    yield url_limpia
                    
            time.sleep(5)
            
    except Exception as e:
        print(f"⚠️ Error en el monitor: {str(e)}")
    finally:
        driver.quit()