import customtkinter as ctk
import threading
import os
import json
import queue
import configparser
from pathlib import Path
from tkinter import messagebox, filedialog
from datetime import datetime
from backend.core.monitor import iniciar_monitor
from backend.core.downloader import descargar_audio, obtener_info_video
from backend.core.utils import es_url_nueva

class ConfigManager:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / 'config.ini'
        self.config = configparser.ConfigParser()
        self.default_config = {
            'settings': {
                # General
                'default_folder': str(Path.home() / 'Music'),
                'default_quality': '320',
                'theme': 'dark',
                
                # Monitor
                'monitor_browser': 'brave',
                'browser_path': 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe',
                'chromedriver_path': str(Path(__file__).parent.parent / 'backend' / 'core' / 'chromedriver.exe'),
                'user_profile': 'Default',
                'monitor_delay': '5',
                'debug_port': '9222'
            }
        }
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not self.config_path.exists():
            self.save_config(self.default_config)
        else:
            self.config.read(self.config_path)
            # Asegurar que todas las claves existan
            for section, options in self.default_config.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                for key, value in options.items():
                    if not self.config.has_option(section, key):
                        self.config.set(section, key, value)
            self.save_config()

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        self.save_config()

    def save_config(self, config_dict=None):
        if config_dict:
            self.config.read_dict(config_dict)
        with open(self.config_path, 'w') as f:
            self.config.write(f)

# Singleton para fácil acceso
config = ConfigManager()

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Cargar configuraciones
        self.load_config()
        
        # barra de progreso
        self.downloading = False
        self.current_download = None
        
        # Configuración de la ventana
        self.title("YouTube Music Downloader PRO")
        self.geometry("900x670")
        self._center_window()
        ctk.set_appearance_mode(self.theme.capitalize())
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.monitor_active = False
        self.running = True
        self.historial = self.cargar_historial()
        self.current_songs = []
        self.url_queue = queue.Queue()
        
        # Configurar interfaz
        self.setup_ui()
        
        # Iniciar procesador de cola
        self.start_queue_processor()

    def load_config(self):
        """Carga las configuraciones desde el archivo"""
        # Configuración general
        self.download_folder = config.get('settings', 'default_folder')
        self.default_quality = config.get('settings', 'default_quality')
        self.theme = config.get('settings', 'theme')
        
        # Configuración del monitor
        self.monitor_browser = config.get('settings', 'monitor_browser')
        self.browser_path = config.get('settings', 'browser_path')
        self.chromedriver_path = config.get('settings', 'chromedriver_path')
        self.user_profile = config.get('settings', 'user_profile')
        self.monitor_delay = config.get('settings', 'monitor_delay')
        self.debug_port = config.get('settings', 'debug_port')

    def save_config(self):
        """Guarda las configuraciones actuales"""
        config.set('settings', 'default_folder', self.download_folder)
        config.set('settings', 'default_quality', self.default_quality)
        config.set('settings', 'theme', self.theme.lower())
        
        # Configuración del monitor
        config.set('settings', 'monitor_browser', self.monitor_browser)
        config.set('settings', 'browser_path', self.browser_path)
        config.set('settings', 'chromedriver_path', self.chromedriver_path)
        config.set('settings', 'user_profile', self.user_profile)
        config.set('settings', 'monitor_delay', self.monitor_delay)
        config.set('settings', 'debug_port', self.debug_port)

    def _center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width - width) // 5
        y = (screen_height - height) // 18
        
        self.geometry(f'+{x}+{y}')

    def setup_ui(self):
        """Configura los elementos de la interfaz"""
        # Frame principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Añadir barra de progreso
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            orientation="horizontal",
            mode="determinate",
            height=20
        )
        self.progress_bar.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        self.progress_bar.set(0)
        self.progress_label = ctk.CTkLabel(
            main_frame,
            text="Preparado para descargar",
            anchor="center"
        )
        self.progress_label.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        
        # Barra de título
        title_frame = ctk.CTkFrame(main_frame, height=50)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(
            title_frame, 
            text="🎵 YouTube Music Downloader", 
            font=("Arial", 20)
        ).pack(pady=10)
        
        # Frame de configuración
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Selector de carpeta de descarga
        ctk.CTkLabel(
            config_frame,
            text="Carpeta de descarga:",
            font=("Arial", 12)
        ).pack(side="left", padx=(10, 5))
        
        self.folder_path_label = ctk.CTkLabel(
            config_frame,
            text=self.download_folder,
            font=("Arial", 10),
            wraplength=500,
            anchor="w",
            justify="left"
        )
        self.folder_path_label.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(
            config_frame,
            text="📁 Seleccionar",
            command=self.select_download_folder,
            width=100
        ).pack(side="right", padx=10)
        
        # Lista de canciones
        self.song_list = ctk.CTkScrollableFrame(
            main_frame,
            height=350,
            scrollbar_button_color="#333333",
            scrollbar_button_hover_color="#555555"
        )
        self.song_list.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.song_list.grid_columnconfigure(0, weight=1)
        
        # Barra de control
        control_frame = ctk.CTkFrame(main_frame, height=50)
        control_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        # Botones
        self.monitor_btn = ctk.CTkButton(
            control_frame, 
            text="▶ Iniciar Monitor", 
            command=self.toggle_monitor
        )
        self.monitor_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame, 
            text="⚙ Configuración", 
            command=self.show_settings_dialog
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            control_frame, 
            text="✖ Limpiar Lista", 
            command=self.clear_list,
            fg_color="#d9534f",
            hover_color="#c9302c"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            control_frame, 
            text="⬇ Descargar Todo", 
            command=self.download_all
        ).pack(side="right", padx=5)
        
        # Barra de estado
        self.status_label = ctk.CTkLabel(
            main_frame,
            text=f"Estado: Monitor detenido | Canciones: 0 | Descargas en: {self.download_folder}",
            anchor="w"
        )
        self.status_label.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        
        # Entrada manual
        self.url_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Pega URL de YouTube aquí"
        )
        self.url_entry.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        
        ctk.CTkButton(
            main_frame,
            text="➕ Añadir Manualmente",
            command=self.add_manual_url
        ).grid(row=6, column=0, sticky="ew", pady=(5, 10))
    
    def show_settings_dialog(self):
        """Muestra el diálogo de configuración"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Configuración")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Pestañas
        tabview = ctk.CTkTabview(dialog)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña General
        general_tab = tabview.add("General")
        
        # Carpeta de descarga
        ctk.CTkLabel(general_tab, text="Carpeta de descarga predeterminada:").pack(pady=(10, 0))
        folder_frame = ctk.CTkFrame(general_tab, fg_color="transparent")
        folder_frame.pack(fill="x", padx=5, pady=5)
        
        self.settings_folder_entry = ctk.CTkEntry(folder_frame)
        self.settings_folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.settings_folder_entry.insert(0, self.download_folder)
        
        ctk.CTkButton(
            folder_frame,
            text="📁",
            width=30,
            command=lambda: self.select_settings_folder(dialog)
        ).pack(side="right")
        
        # Calidad de descarga
        ctk.CTkLabel(general_tab, text="Calidad de audio predeterminada:").pack(pady=(10, 0))
        self.quality_var = ctk.StringVar(value=self.default_quality)
        quality_frame = ctk.CTkFrame(general_tab, fg_color="transparent")
        quality_frame.pack(fill="x", padx=5, pady=5)
        
        qualities = ["320", "256", "192", "128"]
        for quality in qualities:
            ctk.CTkRadioButton(
                quality_frame,
                text=f"{quality} kbps",
                variable=self.quality_var,
                value=quality
            ).pack(side="left", padx=5)
        
        # Tema
        ctk.CTkLabel(general_tab, text="Tema de la aplicación:").pack(pady=(10, 0))
        self.theme_var = ctk.StringVar(value=self.theme.lower())
        ctk.CTkOptionMenu(
            general_tab,
            values=["dark", "light", "system"],
            variable=self.theme_var
        ).pack(fill="x", padx=5, pady=5)
        
        # Pestaña Monitor
        monitor_tab = tabview.add("Monitor")
        
        # Configuración del navegador
        ctk.CTkLabel(monitor_tab, text="Navegador para el monitor:").pack(pady=(10, 0))
        self.browser_var = ctk.StringVar(value=self.monitor_browser)
        ctk.CTkEntry(
            monitor_tab,
            textvariable=self.browser_var
        ).pack(fill="x", padx=5, pady=5)
        
        # Botones
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=lambda: self.save_settings(dialog)
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="transparent",
            border_width=1
        ).pack(side="right", padx=5)

    def select_settings_folder(self, dialog):
        """Selecciona la carpeta para la configuración"""
        folder_selected = filedialog.askdirectory(initialdir=self.download_folder)
        if folder_selected:
            self.settings_folder_entry.delete(0, "end")
            self.settings_folder_entry.insert(0, folder_selected)

    def save_settings(self, dialog):
        """Guarda la configuración"""
        self.download_folder = self.settings_folder_entry.get()
        self.default_quality = self.quality_var.get()
        self.theme = self.theme_var.get()
        
        # Configuración del monitor
        self.monitor_browser = self.browser_var.get()
        
        # Aplicar cambios
        ctk.set_appearance_mode(self.theme.capitalize())
        self.folder_path_label.configure(text=self.download_folder)
        self.update_status()
        
        # Guardar configuración
        self.save_config()
        
        dialog.destroy()
        messagebox.showinfo("Configuración", "Los cambios se han guardado correctamente")

    def select_download_folder(self):
        """Permite al usuario seleccionar una carpeta de descarga"""
        folder_selected = filedialog.askdirectory(initialdir=self.download_folder)
        if folder_selected:
            self.download_folder = folder_selected
            self.folder_path_label.configure(text=folder_selected)
            self.update_status()
            messagebox.showinfo("Carpeta seleccionada", f"Las descargas se guardarán en:\n{folder_selected}")
            self.save_config()
    
    def start_queue_processor(self):
        """Procesa las URLs de la cola en el hilo principal"""
        def process_queue():
            while self.running:
                try:
                    url = self.url_queue.get(timeout=0.1)
                    if url:
                        self.after(0, self._safe_add_song, url)
                except queue.Empty:
                    continue
                
        threading.Thread(target=process_queue, daemon=True).start()
    
    def _safe_add_song(self, url):
        """Versión segura de add_song para usar con after()"""
        try:
            self.add_song(url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo añadir canción: {str(e)}")
    
    def cargar_historial(self):
        """Carga el historial desde el archivo JSON"""
        try:
            with open('historial.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def guardar_historial(self):
        """Guarda el historial sin duplicados"""
        historial_actualizado = self.historial.copy()
        urls_existentes = {item['url'] for item in historial_actualizado}

        for song in self.current_songs:
            if song['url'] not in urls_existentes:
                historial_actualizado.append(song)
                urls_existentes.add(song['url'])

        with open('historial.json', 'w') as f:
            json.dump(historial_actualizado, f, indent=2)
        self.historial = historial_actualizado

    def toggle_monitor(self):
        """Inicia o detiene el monitor"""
        if self.downloading:
            messagebox.showwarning("Advertencia", "No se puede modificar el monitor durante una descarga")
            return
        
        self.monitor_active = not self.monitor_active
    
        if self.monitor_active:
            self.monitor_btn.configure(text="⏸ Detener Monitor")
            threading.Thread(target=self.run_monitor, daemon=True).start()
        else:
            self.monitor_btn.configure(text="▶ Iniciar Monitor")
    
        self.update_status()
    
    def run_monitor(self):
        """Envía URLs a la cola en lugar de actualizar la GUI directamente"""
        for url in iniciar_monitor():
            if not self.monitor_active or self.downloading:  # Verificamos también downloading
                break
            self.url_queue.put(url)
    
    def add_song(self, url):
        """Añade canción a la lista mostrando título y URL"""
        try:
            if not es_url_nueva(url, self.historial, self.current_songs):
                print(f"⚠️ URL ya existe: {url}")
                return

            info = obtener_info_video(url)
            song_data = {
                'url': url,
                'titulo': info['titulo'],
                'duracion': info['duracion'],
                'fecha': datetime.now().isoformat()
            }
            self.current_songs.append(song_data)
            self._safe_update_song_list()
            self.update_status()
    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener información: {str(e)}")
    
    def _safe_update_song_list(self):
        """Actualiza la lista de canciones con mejor visualización"""
        try:
            # Limpiar lista actual de forma segura
            for widget in self.song_list.winfo_children():
                widget.destroy()
            
            # Crear nuevos elementos con mejor formato
            for idx, song in enumerate(self.current_songs):
                # Frame principal para cada canción
                song_frame = ctk.CTkFrame(
                    self.song_list,
                    height=60,
                    corner_radius=5
                )
                song_frame.pack(fill="x", pady=3, padx=5)
                song_frame.grid_columnconfigure(0, weight=1)
                
                # Contenedor para texto
                text_frame = ctk.CTkFrame(song_frame, fg_color="transparent")
                text_frame.grid(row=0, column=0, sticky="nsew", padx=5)
                text_frame.grid_columnconfigure(0, weight=1)
                
                # Etiqueta para el título
                title_label = ctk.CTkLabel(
                    text_frame,
                    text=song['titulo'],
                    font=("Arial", 12, "bold"),
                    anchor="w",
                    justify="left"
                )
                title_label.grid(row=0, column=0, sticky="ew")
                
                # Etiqueta para la URL
                url_label = ctk.CTkLabel(
                    text_frame,
                    text=song['url'],
                    font=("Arial", 10),
                    anchor="w",
                    justify="left",
                    text_color="#AAAAAA"
                )
                url_label.grid(row=1, column=0, sticky="ew", pady=(0, 5))
                
                # Botón para eliminar
                delete_btn = ctk.CTkButton(
                    song_frame,
                    text="✖",
                    width=30,
                    height=30,
                    command=lambda idx=idx: self.after(10, self.remove_song, idx),
                    fg_color="#d9534f",
                    hover_color="#c9302c"
                )
                delete_btn.grid(row=0, column=1, rowspan=2, padx=(5, 10), pady=5, sticky="ns")
            
            # Ajustar el viewport del scrollable frame
            self.song_list._parent_canvas.yview_moveto(0.0)
            self.update_idletasks()
            
        except Exception as e:
            print(f"Error en actualización de lista: {e}")
        
    def add_manual_url(self):
        """Añade una URL manualmente"""
        url = self.url_entry.get().strip()
        if url:
            self.url_queue.put(url)
            self.url_entry.delete(0, "end")
    
    def remove_song(self, index):
        """Elimina una canción de la lista"""
        if 0 <= index < len(self.current_songs):
            self.current_songs.pop(index)
            self._safe_update_song_list()
            self.update_status()
    
    def clear_list(self):
        """Limpia toda la lista de canciones"""
        self.current_songs = []
        self._safe_update_song_list()
        self.update_status()
    
    def download_all(self):
        if not self.current_songs:
            messagebox.showwarning("Advertencia", "No hay canciones para descargar")
            return
        
        if self.downloading:
            messagebox.showwarning("Advertencia", "Ya hay una descarga en progreso")
            return
            
        self.downloading = True
        self.monitor_btn.configure(text="▶ Iniciar Monitor", state="disabled")
        
        # Configurar progreso
        self.progress_bar.set(0)
        self.progress_label.configure(text="Preparando descargas...")
        
        # Iniciar hilo de descarga
        threading.Thread(target=self._download_all_thread, daemon=True).start()
    def _download_all_thread(self):
        success_count = 0
        total = len(self.current_songs)
    
        for i, song in enumerate(self.current_songs, 1):
            if not self.downloading:
                break
            
            self.current_download = song['titulo']
            self._update_progress(i/total, f"Descargando: {song['titulo']}")
        
            try:
                os.makedirs(self.download_folder, exist_ok=True)
                archivo = descargar_audio(
                    song['url'], 
                    output_dir=self.download_folder,
                    progress_hook=self._download_progress_hook
                )
            
                self.historial.append({
                    'url': song['url'],
                    'titulo': song['titulo'],
                    'fecha': song['fecha'],
                    'ruta': str(archivo.resolve())
                })
                success_count += 1
            
            except Exception as e:
                print(f"Error al descargar {song['titulo']}: {str(e)}")
                self._update_progress(i/total, f"Error: {song['titulo']}")
    
        # Finalización
        self.guardar_historial()
        self._update_progress(1.0, f"Descargadas {success_count}/{total} canciones")
        self.clear_list()
        self.downloading = False
        self.current_download = None
    
        self.after(0, lambda: messagebox.showinfo(
            "Descarga completada",
            f"Descargadas {success_count}/{total} canciones\nen: {self.download_folder}"
        ))
    
        # Restaurar el estado del botón según el estado actual del monitor
        if self.monitor_active:
            self.monitor_btn.configure(text="⏸ Detener Monitor", state="normal")
        else:
            self.monitor_btn.configure(text="▶ Iniciar Monitor", state="normal")

    def _download_progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').replace('%', '')
            try:
                percent_float = float(percent)/100
                self.after(0, self._update_progress, 
                          percent_float, 
                          f"Descargando {self.current_download}: {d.get('_percent_str', '')}")
            except ValueError:
                pass
        return True    
    
    def _update_progress(self, value, text):
        self.progress_bar.set(value)
        self.progress_label.configure(text=text)
        self.update_idletasks()
    
    def update_status(self):
        """Actualiza la barra de estado"""
        status = "Monitor activo" if self.monitor_active else "Monitor detenido"
        self.status_label.configure(
            text=f"Estado: {status} | Canciones: {len(self.current_songs)} | Descargas en: {self.download_folder}"
        )
    
    def on_close(self):
        """Método para cerrar la ventana de forma segura"""
        self.downloading = False
        self.running = False
        self.monitor_active = False
        self.save_config()  # Guardar configuraciones al cerrar
        self.destroy()

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()