import customtkinter as ctk
import threading
import os
import json  # Importación faltante
from tkinter import messagebox
from datetime import datetime
from backend.core.monitor import iniciar_monitor
from backend.core.downloader import descargar_audio  # Importación clave

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("YouTube Music Downloader PRO")
        self.geometry("900x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.monitor_active = False
        self.historial = self.cargar_historial()
        self.current_songs = []
        
        # Configurar interfaz
        self.setup_ui()
        
    def setup_ui(self):
        """Configura los elementos de la interfaz"""
        # Frame principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Barra de título
        title_frame = ctk.CTkFrame(main_frame, height=50)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(
            title_frame, 
            text="🎵 YouTube Music Downloader", 
            font=("Arial", 20)
        ).pack(pady=10)
        
        # Lista de canciones
        self.song_list = ctk.CTkScrollableFrame(main_frame)
        self.song_list.grid(row=1, column=0, sticky="nsew")
        
        # Barra de control
        control_frame = ctk.CTkFrame(main_frame, height=50)
        control_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
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
            text="Estado: Monitor detenido | Canciones: 0",
            anchor="w"
        )
        self.status_label.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        # Entrada manual
        self.url_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Pega URL de YouTube aquí"
        )
        self.url_entry.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        
        ctk.CTkButton(
            main_frame,
            text="➕ Añadir Manualmente",
            command=self.add_manual_url
        ).grid(row=5, column=0, sticky="ew", pady=(5, 10))
        
    def cargar_historial(self):
        """Carga el historial desde el archivo JSON"""
        try:
            with open('historial.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def guardar_historial(self):
        """Guarda el historial en el archivo JSON"""
        with open('historial.json', 'w') as f:
            json.dump(self.historial, f, indent=2)
    
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
        """Ejecuta el monitor en segundo plano"""
        for url in iniciar_monitor():
            if not self.monitor_active:
                break
            self.add_song(url)
    
    def add_song(self, url):
        """Añade solo la URL a la lista sin obtener metadatos"""
        if not any(song['url'] == url for song in self.current_songs):
            song_data = {
                'url': url,
                'date': datetime.now().isoformat()
            }
            self.current_songs.append(song_data)
            self.update_song_list()
            self.update_status()

        
    def add_manual_url(self):
        """Añade una URL manualmente"""
        url = self.url_entry.get().strip()
        if url:
            self.add_song(url)
            self.url_entry.delete(0, "end")
    #-------------------------------------------------------

    def update_song_list(self):
    
        try:
            # Destruir el frame existente de manera segura
            for widget in self.song_list.winfo_children():
                try:
                    widget.destroy()
                except:
                    continue
        
            # Crear nuevos elementos
            for idx, song in enumerate(self.current_songs):
                try:
                    frame = ctk.CTkFrame(self.song_list)
                    frame.pack(fill="x", pady=2)
                
                    label = ctk.CTkLabel(frame, text=song['url'], anchor="w")
                    label.pack(side="left", fill="x", expand=True, padx=5)
                
                    btn = ctk.CTkButton(
                        frame,
                        text="✖",
                        width=30,
                        command=lambda i=idx: self.remove_song(i),
                        fg_color="transparent",
                        hover_color="#d9534f",
                        text_color="#d9534f"
                    )
                    btn.pack(side="right", padx=5)
                
                except Exception as e:
                    print(f"Error creando elemento {idx}: {e}")
                    continue
                
        except Exception as e:
            print(f"Error grave al actualizar lista: {e}")

    #-------------------------------------------------------        
    def remove_song(self, index):
        """Elimina una canción de la lista"""
        if 0 <= index < len(self.current_songs):
            self.current_songs.pop(index)
            self.update_song_list()
            self.update_status()
    
    def clear_list(self):
        """Limpia toda la lista de canciones"""
        self.current_songs = []
        self.update_song_list()
        self.update_status()
    #-------------------------------------------------------
    def download_all(self):
        """Versión corregida del método de descarga"""
        if not self.current_songs:
            messagebox.showwarning("Advertencia", "No hay canciones para descargar")
            return
    
        success_count = 0
        download_folder = "downloads"
    
        for song in self.current_songs:
            try:
                # Llamada correcta con un solo argumento (URL)
                archivo = descargar_audio(song['url'])
            
                self.historial.append({
                    'url': song['url'],
                    'nombre': archivo.name,
                    'fecha': datetime.now().isoformat(),
                    'ruta': str(archivo.resolve())
                })
                success_count += 1
            
            except Exception as e:
                print(f"Error al descargar {song['url']}: {e}")
    
        self.guardar_historial()
        self.clear_list()
        messagebox.showinfo(
            "Descarga completada",
            f"Descargadas {success_count}/{len(self.current_songs)} canciones"
        )
    #-------------------------------------------------------

    def update_status(self):
        """Actualiza la barra de estado"""
        status = "Monitor activo" if self.monitor_active else "Monitor detenido"
        self.status_label.configure(
            text=f"Estado: {status} | Canciones en lista: {len(self.current_songs)}"
        )

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()