from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import logging
from backend.core.config_manager import config  # Asegúrate de que esta importación sea correcta

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def iniciar_monitor():
    """Monitor optimizado usando el perfil real del usuario"""
    try:
        # Obtener configuración
        browser = config.get('settings', 'monitor_browser').lower()
        browser_path = config.get('settings', 'browser_path')
        chromedriver_path = config.get('settings', 'chromedriver_path')
        monitor_delay = float(config.get('settings', 'monitor_delay'))
        debug_port = config.get('settings', 'debug_port')
        user_profile = config.get('settings', 'user_profile')

        # Validar rutas
        if not os.path.exists(browser_path):
            raise FileNotFoundError(f"Ruta del navegador no encontrada: {browser_path}")
        if not os.path.exists(chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver no encontrado en: {chromedriver_path}")

        # Configuración de opciones
        options = Options()
        options.binary_location = browser_path
        options.add_argument("--disable-notifications")
        options.add_argument(f"--remote-debugging-port={debug_port}")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
        options.add_argument("--autoplay-policy=no-user-gesture-required")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")

        # Configuración específica para Brave o Chrome
        if browser == 'brave':
            options.add_argument("--disable-brave-update")
            user_data = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data')
        else:
            user_data = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data')

        # Perfil real
        options.add_argument(f"user-data-dir={user_data}")
        options.add_argument(f"profile-directory={user_profile}")

        # Configuración del servicio
        service = Service(
            executable_path=chromedriver_path,
            service_args=["--verbose", "--log-path=chromedriver.log"]
        )

        # Inicializar driver con reintentos
        max_attempts = 3
        attempt = 0
        driver = None
        
        while attempt < max_attempts:
            try:
                driver = webdriver.Chrome(service=service, options=options)
                break
            except Exception as e:
                attempt += 1
                logger.warning(f"Intento {attempt} fallido al iniciar ChromeDriver: {str(e)}")
                if attempt == max_attempts:
                    raise
                time.sleep(2)

        try:
            # Configurar tiempos de espera
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # Navegar a YouTube
            driver.get("https://www.youtube.com")
            logger.info("🔍 Monitoreando YouTube...")
            logger.info(f"Configuración: Browser={browser}, Profile={user_profile}, Delay={monitor_delay}s")
            
            ultima_url = None
            url_count = 0
            
            while True:
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
                    )
                    
                    current_url = driver.current_url
                    
                    if "watch?v=" in current_url:
                        url_limpia = current_url.split('&')[0]
                        
                        if url_limpia != ultima_url:
                            url_count += 1
                            logger.info(f"🎵 URL detectada ({url_count}): {url_limpia}")
                            ultima_url = url_limpia
                            yield url_limpia
                            
                    # Asegurar que el video siga reproduciéndose
                    play_script = """
                    var video = document.querySelector('video');
                    if (video && video.paused) { video.play(); }
                    """
                    driver.execute_script(play_script)

                    time.sleep(monitor_delay)
                    
                except Exception as e:
                    logger.warning(f"Error durante el monitoreo: {str(e)}")
                    # Solo esperar, no refrescar automáticamente
                    time.sleep(5)
                    
        except Exception as e:
            logger.error(f"⚠️ Error crítico en el monitor: {str(e)}", exc_info=True)
            raise
        finally:
            if driver is not None:
                try:
                    driver.quit()
                    logger.info("🛑 Monitor detenido correctamente")
                except Exception as e:
                    logger.error(f"Error al cerrar el driver: {str(e)}")

    except Exception as e:
        logger.critical(f"❌ Error crítico al iniciar monitor: {str(e)}")
        raise
