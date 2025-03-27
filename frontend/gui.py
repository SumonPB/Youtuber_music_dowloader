import customtkinter as ctk
import threading
import os
import json
import queue
from tkinter import messagebox, filedialog
from datetime import datetime
from backend.core.monitor import iniciar_monitor
from backend.core.downloader import descargar_audio, obtener_info_video
from backend.core.utils import es_url_nueva

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # barra de progreso
        self.downloading = False
        self.current_download = None
        # Configuración de la ventana
        self.title("YouTube Music Downloader PRO")
        self.geometry("900x670")  # Aumentamos un poco el tamaño
        self._center_window()  # Añade esta línea después de geometry()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.monitor_active = False
        self.running = True
        self.historial = self.cargar_historial()
        self.current_songs = []
        self.url_queue = queue.Queue()
        self.download_folder = os.path.join(os.path.expanduser("~"), "Downloads")  # Carpeta por defecto
        
        # Configurar interfaz
        self.setup_ui()
        
        # Iniciar procesador de cola
        self.start_queue_processor()

    def _center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()  # Actualiza los datos de la ventana
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
            text="⬇ Descargar Todo", 
            command=self.download_all
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            control_frame, 
            text="✖ Limpiar Lista", 
            command=self.clear_list,
            fg_color="#d9534f",
            hover_color="#c9302c"
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
    
    def select_download_folder(self):
        """Permite al usuario seleccionar una carpeta de descarga"""
        folder_selected = filedialog.askdirectory(initialdir=self.download_folder)
        if folder_selected:
            self.download_folder = folder_selected
            self.folder_path_label.configure(text=folder_selected)
            self.update_status()
            messagebox.showinfo("Carpeta seleccionada", f"Las descargas se guardarán en:\n{folder_selected}")
    
    def start_queue_processor(self):
        """Procesa las URLs de la cola en el hilo principal"""
        def process_queue():
            while self.running:
                try:
                    url = self.url_queue.get(timeout=0.1)
                    if url:  # Solo procesar si hay una URL válida
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
            with open('historial.json', 'r') as f:
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
            if not self.monitor_active:
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
    #-------------------------------------------------------------
    def download_all(self):
        if not self.current_songs:
            messagebox.showwarning("Advertencia", "No hay canciones para descargar")
            return
        
        if self.downloading:
            messagebox.showwarning("Advertencia", "Ya hay una descarga en progreso")
            return
            
        self.downloading = True
        self.monitor_active = False  # Detener el monitor si está activo
        self.monitor_btn.configure(text="▶ Iniciar Monitor", state="disabled")
        
        # Configurar progreso
        self.progress_bar.set(0)
        self.progress_label.configure(text="Preparando descargas...")
        
        # Iniciar hilo de descarga
        threading.Thread(target=self._download_all_thread, daemon=True).start()
    #-------------------------------------------------------------
    # -------------------------------------------------------------
    def _download_all_thread(self):
        success_count = 0
        total = len(self.current_songs)
        
        for i, song in enumerate(self.current_songs, 1):
            if not self.downloading:  # Permitir cancelación
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
        self.monitor_btn.configure(state="normal")

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
    # -------------------------------------------------------------      
    def update_status(self):
        """Actualiza la barra de estado"""
        status = "Monitor activo" if self.monitor_active else "Monitor detenido"
        self.status_label.configure(
            text=f"Estado: {status} | Canciones: {len(self.current_songs)} | Descargas en: {self.download_folder}"
        )
    
    def on_close(self):
        """Método para cerrar la ventana de forma segura"""
        self.downloading = False  # Esto cancelará las descargas en progreso
        self.running = False
        self.monitor_active = False
        self.destroy()

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()