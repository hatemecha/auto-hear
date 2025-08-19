import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
from datetime import datetime

# Importar el analizador de música (asumiendo que está en el mismo directorio)
try:
    from music_analyzer import MusicAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class MusicAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 Analizador Musical Avanzado - Key & BPM Detector")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variables
        self.current_file = tk.StringVar()
        self.analysis_results = None
        self.is_analyzing = False
        
        # Configurar estilo
        self.setup_style()
        
        # Crear interfaz
        self.create_widgets()
        
        # Verificar dependencias
        self.check_dependencies()
    
    def setup_style(self):
        """Configurar el estilo visual de la aplicación"""
        self.root.configure(bg='#2b2b2b')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('Title.TLabel', 
                       background='#2b2b2b', 
                       foreground='#ffffff',
                       font=('Helvetica', 16, 'bold'))
        
        style.configure('Header.TLabel',
                       background='#2b2b2b',
                       foreground='#4CAF50',
                       font=('Helvetica', 12, 'bold'))
        
        style.configure('Info.TLabel',
                       background='#2b2b2b',
                       foreground='#ffffff',
                       font=('Helvetica', 10))
        
        style.configure('Result.TLabel',
                       background='#2b2b2b',
                       foreground='#FFC107',
                       font=('Helvetica', 14, 'bold'))
        
        style.configure('Custom.TButton',
                       background='#4CAF50',
                       foreground='white',
                       font=('Helvetica', 10, 'bold'),
                       borderwidth=0)
        
        style.map('Custom.TButton',
                 background=[('active', '#45a049')])
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="🎵 Analizador Musical Avanzado",
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame superior - Selección de archivo
        self.create_file_selection_frame(main_frame)
        
        # Frame central - Notebook con pestañas
        self.create_notebook(main_frame)
        
        # Frame inferior - Controles y progreso
        self.create_controls_frame(main_frame)
    
    def create_file_selection_frame(self, parent):
        """Crear frame para selección de archivos"""
        file_frame = ttk.LabelFrame(parent, text="📁 Selección de Archivo", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame interno para organizar widgets
        inner_frame = ttk.Frame(file_frame)
        inner_frame.pack(fill=tk.X)
        
        # Entry para mostrar archivo seleccionado
        self.file_entry = ttk.Entry(inner_frame, textvariable=self.current_file, 
                                   state='readonly', font=('Helvetica', 10))
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Botón para seleccionar archivo
        select_btn = ttk.Button(inner_frame, text="🔍 Seleccionar Audio",
                               command=self.select_file, style='Custom.TButton')
        select_btn.pack(side=tk.RIGHT)
        
        # Información de formatos soportados
        formats_label = ttk.Label(file_frame,
                                 text="Formatos soportados: MP3, WAV, FLAC, OGG, M4A, AAC",
                                 style='Info.TLabel')
        formats_label.pack(pady=(5, 0))
    
    def create_notebook(self, parent):
        """Crear notebook con pestañas"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Pestaña 1: Resultados
        self.create_results_tab()
        
        # Pestaña 2: Visualizaciones
        self.create_visualization_tab()
        
        # Pestaña 3: Detalles Técnicos
        self.create_details_tab()
        
        # Pestaña 4: Configuración
        self.create_settings_tab()
    
    def create_results_tab(self):
        """Crear pestaña de resultados principales"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Resultados")
        
        # Crear canvas con scrollbar
        canvas = tk.Canvas(results_frame, bg='#2b2b2b')
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenido de resultados
        self.create_results_content(scrollable_frame)
    
    def create_results_content(self, parent):
        """Crear contenido de la pestaña de resultados"""
        # Frame para información del archivo
        file_info_frame = ttk.LabelFrame(parent, text="📄 Información del Archivo", padding=15)
        file_info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_info_text = tk.Text(file_info_frame, height=4, bg='#3b3b3b', 
                                     fg='white', font=('Courier', 10))
        self.file_info_text.pack(fill=tk.X)
        
        # Frame principal de resultados
        main_results_frame = ttk.Frame(parent)
        main_results_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Columna izquierda - BPM
        bpm_frame = ttk.LabelFrame(main_results_frame, text="🥁 Análisis de BPM", padding=15)
        bpm_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.bpm_result_label = ttk.Label(bpm_frame, text="---", style='Result.TLabel')
        self.bpm_result_label.pack(pady=(0, 10))
        
        self.bpm_confidence_label = ttk.Label(bpm_frame, text="Confianza: ---%", style='Info.TLabel')
        self.bpm_confidence_label.pack()
        
        self.bpm_method_label = ttk.Label(bpm_frame, text="Método: ---", style='Info.TLabel')
        self.bpm_method_label.pack()
        
        self.bpm_stability_label = ttk.Label(bpm_frame, text="Estabilidad: ---", style='Info.TLabel')
        self.bpm_stability_label.pack()
        
        # Columna derecha - Key
        key_frame = ttk.LabelFrame(main_results_frame, text="🎵 Análisis de Tonalidad", padding=15)
        key_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.key_result_label = ttk.Label(key_frame, text="---", style='Result.TLabel')
        self.key_result_label.pack(pady=(0, 10))
        
        self.key_confidence_label = ttk.Label(key_frame, text="Confianza: ---%", style='Info.TLabel')
        self.key_confidence_label.pack()
        
        self.key_method_label = ttk.Label(key_frame, text="Método: ---", style='Info.TLabel')
        self.key_method_label.pack()
        
        self.key_changes_label = ttk.Label(key_frame, text="Cambios: ---", style='Info.TLabel')
        self.key_changes_label.pack()
        
        # Frame de silencios
        silence_frame = ttk.LabelFrame(parent, text="🔇 Análisis de Silencios", padding=15)
        silence_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.silence_info_text = tk.Text(silence_frame, height=6, bg='#3b3b3b', 
                                        fg='white', font=('Courier', 9))
        self.silence_info_text.pack(fill=tk.X)
        
        # Frame de acciones
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        export_btn = ttk.Button(actions_frame, text="💾 Exportar Resultados",
                               command=self.export_results, style='Custom.TButton')
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        copy_btn = ttk.Button(actions_frame, text="📋 Copiar al Portapapeles",
                             command=self.copy_to_clipboard, style='Custom.TButton')
        copy_btn.pack(side=tk.LEFT)
    
    def create_visualization_tab(self):
        """Crear pestaña de visualizaciones"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="📈 Visualizaciones")
        
        # Frame para controles de visualización
        controls_frame = ttk.Frame(viz_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Visualización:", style='Header.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.viz_var = tk.StringVar(value="tempo")
        viz_combo = ttk.Combobox(controls_frame, textvariable=self.viz_var,
                                values=["tempo", "chromagram", "onset_strength"],
                                state="readonly", width=20)
        viz_combo.pack(side=tk.LEFT, padx=(0, 10))
        viz_combo.bind('<<ComboboxSelected>>', self.update_visualization)
        
        refresh_viz_btn = ttk.Button(controls_frame, text="🔄 Actualizar",
                                   command=self.update_visualization, style='Custom.TButton')
        refresh_viz_btn.pack(side=tk.LEFT)
        
        # Frame para el plot
        self.plot_frame = ttk.Frame(viz_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inicializar plot vacío
        self.init_empty_plot()
    
    def create_details_tab(self):
        """Crear pestaña de detalles técnicos"""
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text="🔧 Detalles Técnicos")
        
        # Texto con detalles técnicos
        self.details_text = scrolledtext.ScrolledText(details_frame, 
                                                     bg='#3b3b3b', fg='white',
                                                     font=('Courier', 10))
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_settings_tab(self):
        """Crear pestaña de configuración"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Configuración")
        
        # Configuración de análisis
        analysis_frame = ttk.LabelFrame(settings_frame, text="Parámetros de Análisis", padding=15)
        analysis_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Umbral de silencio
        ttk.Label(analysis_frame, text="Umbral de silencio (dB):", style='Info.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.silence_threshold_var = tk.DoubleVar(value=-40)
        silence_scale = ttk.Scale(analysis_frame, from_=-60, to=-20, 
                                 variable=self.silence_threshold_var, orient=tk.HORIZONTAL)
        silence_scale.grid(row=0, column=1, sticky='ew', padx=(0, 10))
        self.silence_value_label = ttk.Label(analysis_frame, text="-40 dB", style='Info.TLabel')
        self.silence_value_label.grid(row=0, column=2)
        silence_scale.configure(command=self.update_silence_label)
        
        # Duración mínima de silencio
        ttk.Label(analysis_frame, text="Duración mín. silencio (s):", style='Info.TLabel').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.min_silence_var = tk.DoubleVar(value=0.5)
        silence_dur_scale = ttk.Scale(analysis_frame, from_=0.1, to=2.0,
                                     variable=self.min_silence_var, orient=tk.HORIZONTAL)
        silence_dur_scale.grid(row=1, column=1, sticky='ew', padx=(0, 10), pady=(10, 0))
        self.silence_dur_label = ttk.Label(analysis_frame, text="0.5 s", style='Info.TLabel')
        self.silence_dur_label.grid(row=1, column=2, pady=(10, 0))
        silence_dur_scale.configure(command=self.update_silence_dur_label)
        
        # Configurar grid weights
        analysis_frame.grid_columnconfigure(1, weight=1)
        
        # Información sobre librerías
        libs_frame = ttk.LabelFrame(settings_frame, text="Estado de Librerías", padding=15)
        libs_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.libs_text = tk.Text(libs_frame, height=8, bg='#3b3b3b', fg='white',
                                font=('Courier', 10), state='disabled')
        self.libs_text.pack(fill=tk.X)
        
        # Botones de ayuda
        help_frame = ttk.Frame(settings_frame)
        help_frame.pack(fill=tk.X, padx=10, pady=10)
        
        help_btn = ttk.Button(help_frame, text="❓ Ayuda",
                             command=self.show_help, style='Custom.TButton')
        help_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        about_btn = ttk.Button(help_frame, text="ℹ️ Acerca de",
                              command=self.show_about, style='Custom.TButton')
        about_btn.pack(side=tk.LEFT)
    
    def create_controls_frame(self, parent):
        """Crear frame de controles inferiores"""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botón de análisis
        self.analyze_btn = ttk.Button(controls_frame, text="🔍 Analizar Audio",
                                     command=self.start_analysis, style='Custom.TButton')
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(controls_frame, variable=self.progress_var,
                                           maximum=100, mode='indeterminate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Label de estado
        self.status_label = ttk.Label(controls_frame, text="Listo para analizar", style='Info.TLabel')
        self.status_label.pack(side=tk.RIGHT)
    
    def init_empty_plot(self):
        """Inicializar plot vacío"""
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#3b3b3b')
        ax.text(0.5, 0.5, 'Selecciona un archivo y analízalo\npara ver las visualizaciones',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, color='white', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        
        self.canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def select_file(self):
        """Seleccionar archivo de audio"""
        filetypes = [
            ("Archivos de Audio", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
            ("MP3", "*.mp3"),
            ("WAV", "*.wav"),
            ("FLAC", "*.flac"),
            ("OGG", "*.ogg"),
            ("M4A", "*.m4a"),
            ("AAC", "*.aac"),
            ("Todos los archivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=filetypes
        )
        
        if filename:
            self.current_file.set(filename)
            self.reset_results()
            self.status_label.config(text=f"Archivo seleccionado: {os.path.basename(filename)}")
            # Iniciar el análisis automáticamente tras seleccionar el archivo
            # para evitar que el usuario tenga que hacer un paso adicional.
            # Esto soluciona el problema reportado donde no ocurría nada al
            # elegir un audio.
            self.start_analysis()
    
    def start_analysis(self):
        """Iniciar análisis en hilo separado"""
        if not self.current_file.get():
            messagebox.showwarning("Advertencia", "Selecciona primero un archivo de audio")
            return
        
        if not ANALYZER_AVAILABLE:
            messagebox.showerror("Error", "El módulo de análisis no está disponible.\nAsegúrate de tener music_analyzer.py en el mismo directorio.")
            return
        
        if self.is_analyzing:
            return
        
        self.is_analyzing = True
        self.analyze_btn.config(state='disabled', text="⏳ Analizando...")
        self.progress_bar.start()
        self.status_label.config(text="Analizando audio...")
        
        # Ejecutar análisis en hilo separado
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()
    
    def run_analysis(self):
        """Ejecutar análisis de audio"""
        try:
            # Crear analizador con configuración personalizada
            analyzer = MusicAnalyzer()
            analyzer.silence_threshold = self.silence_threshold_var.get()
            analyzer.min_silence_duration = self.min_silence_var.get()
            
            # Realizar análisis
            self.analysis_results = analyzer.analyze_song(self.current_file.get(), verbose=False)
            
            # Actualizar UI en hilo principal
            self.root.after(0, self.analysis_complete)
            
        except Exception as e:
            error_msg = f"Error durante el análisis: {str(e)}"
            self.root.after(0, lambda: self.analysis_error(error_msg))
    
    def analysis_complete(self):
        """Callback cuando el análisis se completa exitosamente"""
        self.is_analyzing = False
        self.analyze_btn.config(state='normal', text="🔍 Analizar Audio")
        self.progress_bar.stop()
        self.status_label.config(text="Análisis completado")
        
        if self.analysis_results and 'error' not in self.analysis_results:
            self.update_results_display()
            self.update_visualization()
            self.update_details_display()
            messagebox.showinfo("Éxito", "Análisis completado exitosamente!")
        else:
            error = self.analysis_results.get('error', 'Error desconocido') if self.analysis_results else 'Error desconocido'
            self.analysis_error(error)
    
    def analysis_error(self, error_msg):
        """Callback cuando ocurre un error en el análisis"""
        self.is_analyzing = False
        self.analyze_btn.config(state='normal', text="🔍 Analizar Audio")
        self.progress_bar.stop()
        self.status_label.config(text="Error en análisis")
        messagebox.showerror("Error", error_msg)
    
    def update_results_display(self):
        """Actualizar la visualización de resultados"""
        if not self.analysis_results:
            return
        
        # Información del archivo
        file_info = f"""Archivo: {os.path.basename(self.analysis_results['file_path'])}
Duración: {self.analysis_results['duration']:.2f} segundos
Sample Rate: {self.analysis_results['audio_info']['sample_rate']} Hz
Muestras: {self.analysis_results['audio_info']['samples']:,}"""
        
        self.file_info_text.delete(1.0, tk.END)
        self.file_info_text.insert(tk.END, file_info)
        
        # Resultados BPM
        bpm_data = self.analysis_results['bpm_analysis']
        self.bpm_result_label.config(text=f"{bpm_data['bpm']:.1f} BPM")
        self.bpm_confidence_label.config(text=f"Confianza: {bpm_data['confidence']*100:.1f}%")
        self.bpm_method_label.config(text=f"Método: {bpm_data['method']}")
        
        stability = bpm_data.get('tempo_stability')
        if stability is not None:
            stability_text = "Estable" if stability < 0.2 else "Variable" if stability < 0.4 else "Muy Variable"
            self.bpm_stability_label.config(text=f"Tempo: {stability_text} ({stability:.2f})")
        else:
            self.bpm_stability_label.config(text="Tempo: No evaluado")
        
        # Resultados Key
        key_data = self.analysis_results['key_analysis']
        self.key_result_label.config(text=f"{key_data['key']} {key_data['scale'].title()}")
        self.key_confidence_label.config(text=f"Confianza: {key_data['confidence']*100:.1f}%")
        self.key_method_label.config(text=f"Método: {key_data['method']}")
        
        changes = "Detectados" if key_data.get('key_changes_detected', False) else "No detectados"
        self.key_changes_label.config(text=f"Cambios: {changes}")
        
        # Información de silencios
        silence_data = self.analysis_results['silence_analysis']
        silence_info = f"Segmentos de silencio encontrados: {silence_data['segments_found']}\n"
        silence_info += f"Duración total de silencios: {silence_data['total_silence_duration']:.2f}s\n\n"
        
        if silence_data['segments']:
            silence_info += "Ubicación de silencios:\n"
            for i, (start, end, duration) in enumerate(silence_data['segments'][:10]):  # Mostrar máximo 10
                silence_info += f"  {i+1:2d}. {start:6.2f}s - {end:6.2f}s ({duration:.2f}s)\n"
            if len(silence_data['segments']) > 10:
                silence_info += f"  ... y {len(silence_data['segments'])-10} más\n"
        else:
            silence_info += "No se encontraron silencios significativos."
        
        self.silence_info_text.delete(1.0, tk.END)
        self.silence_info_text.insert(tk.END, silence_info)
    
    def update_visualization(self, event=None):
        """Actualizar visualización según la opción seleccionada"""
        if not self.analysis_results:
            return
        
        # Limpiar plot anterior
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        try:
            import librosa
            y, sr = librosa.load(self.current_file.get(), sr=22050)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#3b3b3b')
            
            viz_type = self.viz_var.get()
            
            if viz_type == "tempo":
                # Visualizar beats y tempo
                beats = self.analysis_results['bpm_analysis'].get('beats', [])
                if len(beats) > 0:
                    times = librosa.frames_to_time(beats, sr=sr)
                    ax.vlines(times, 0, 1, color='#4CAF50', alpha=0.8, linewidth=2, label='Beats detectados')
                
                # Agregar líneas de tiempo
                duration = len(y) / sr
                time_markers = np.arange(0, duration, 10)  # Cada 10 segundos
                ax.vlines(time_markers, 0, 1, color='white', alpha=0.3, linewidth=0.5)
                
                ax.set_ylim(0, 1)
                ax.set_xlim(0, duration)
                ax.set_xlabel('Tiempo (s)', color='white')
                ax.set_ylabel('Beats', color='white')
                ax.set_title(f'Detección de Beats - BPM: {self.analysis_results["bpm_analysis"]["bpm"]:.1f}', 
                           color='white', fontsize=14)
                
            elif viz_type == "chromagram":
                # Chromagram para análisis tonal
                chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
                times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=sr)
                
                im = ax.imshow(chroma, aspect='auto', origin='lower', 
                             extent=[times[0], times[-1], 0, 12], cmap='plasma')
                ax.set_xlabel('Tiempo (s)', color='white')
                ax.set_ylabel('Clases de Tono', color='white')
                ax.set_title(f'Chromagram - Key: {self.analysis_results["key_analysis"]["key"]} {self.analysis_results["key_analysis"]["scale"]}', 
                           color='white', fontsize=14)
                
                # Etiquetas de notas
                note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                ax.set_yticks(range(12))
                ax.set_yticklabels(note_names)
                
                plt.colorbar(im, ax=ax)
                
            elif viz_type == "onset_strength":
                # Onset strength para análisis rítmico
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)
                
                ax.plot(times, onset_env, color='#FFC107', linewidth=1)
                ax.fill_between(times, onset_env, alpha=0.3, color='#FFC107')
                
                ax.set_xlabel('Tiempo (s)', color='white')
                ax.set_ylabel('Onset Strength', color='white')
                ax.set_title('Strength de Onsets - Análisis Rítmico', color='white', fontsize=14)
            
            # Configurar colores de ejes
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.tight_layout()
            
            # Integrar plot en tkinter
            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            # Plot de error
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#3b3b3b')
            ax.text(0.5, 0.5, f'Error generando visualización:\n{str(e)}',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color='red', fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            
            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_details_display(self):
        """Actualizar la visualización de detalles técnicos"""
        if not self.analysis_results:
            return
        
        details = "=== DETALLES TÉCNICOS DEL ANÁLISIS ===\n\n"
        
        # Información general
        details += f"Archivo: {self.analysis_results['file_path']}\n"
        details += f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        details += f"Duración: {self.analysis_results['duration']:.3f} segundos\n"
        details += f"Sample Rate: {self.analysis_results['audio_info']['sample_rate']} Hz\n"
        details += f"Total de muestras: {self.analysis_results['audio_info']['samples']:,}\n\n"
        
        # Análisis BPM detallado
        bpm_data = self.analysis_results['bpm_analysis']
        details += "=== ANÁLISIS BPM ===\n"
        details += f"BPM Final: {bpm_data['bpm']:.2f}\n"
        details += f"Confianza: {bpm_data['confidence']:.4f} ({bpm_data['confidence']*100:.1f}%)\n"
        details += f"Método principal: {bpm_data['method']}\n"
        details += f"Beats detectados: {bpm_data['beats_detected']}\n"

        if 'tempo_stability' in bpm_data and bpm_data['tempo_stability'] is not None:
            details += f"Estabilidad del tempo: {bpm_data['tempo_stability']:.4f}\n"
            if bpm_data['tempo_stability'] < 0.2:
                details += "  -> Tempo muy estable\n"
            elif bpm_data['tempo_stability'] < 0.4:
                details += "  -> Tempo moderadamente variable\n"
            else:
                details += "  -> Tempo muy variable (cambios frecuentes)\n"

        details += "\nTodas las estimaciones BPM:\n"
        for i, est in enumerate(bpm_data.get('all_estimates', []), 1):
            details += f"  {i}. {est['bpm']:.2f} BPM (confianza: {est['confidence']:.3f}, método: {est['method']})\n"
        
        # Análisis de tonalidad detallado
        key_data = self.analysis_results['key_analysis']
        details += "\n=== ANÁLISIS DE TONALIDAD ===\n"
        details += f"Tonalidad: {key_data['key']} {key_data['scale']}\n"
        details += f"Confianza: {key_data['confidence']:.4f} ({key_data['confidence']*100:.1f}%)\n"
        details += f"Método: {key_data['method']}\n"
        
        if 'key_stability' in key_data and key_data['key_stability'] is not None:
            details += f"Estabilidad tonal: {key_data['key_stability']:.4f}\n"
            if key_data['key_stability'] > 0.8:
                details += "  -> Tonalidad muy consistente\n"
            elif key_data['key_stability'] > 0.6:
                details += "  -> Tonalidad moderadamente consistente\n"
            else:
                details += "  -> Tonalidad variable (posibles modulaciones)\n"
        
        if key_data.get('key_changes_detected', False):
            details += "ADVERTENCIA: Se detectaron cambios de tonalidad en la canción\n"
        
        # Análisis de silencios
        silence_data = self.analysis_results['silence_analysis']
        details += "\n=== ANÁLISIS DE SILENCIOS ===\n"
        details += f"Umbral utilizado: {self.silence_threshold_var.get()} dB\n"
        details += f"Duración mínima: {self.min_silence_var.get()} segundos\n"
        details += f"Segmentos encontrados: {silence_data['segments_found']}\n"
        details += f"Tiempo total de silencio: {silence_data['total_silence_duration']:.3f}s\n"
        details += f"Porcentaje de silencio: {(silence_data['total_silence_duration']/self.analysis_results['duration'])*100:.1f}%\n"
        
        if silence_data['segments']:
            details += "\nDetalle de segmentos silenciosos:\n"
            for i, (start, end, duration) in enumerate(silence_data['segments'], 1):
                details += f"  {i:2d}. {start:7.3f}s - {end:7.3f}s (duración: {duration:.3f}s)\n"
        
        # Información técnica adicional
        details += "\n=== CONFIGURACIÓN TÉCNICA ===\n"
        details += f"Hop length: 512 samples\n"
        details += f"Frame length: 2048 samples\n"
        details += f"Ventana de análisis: ~93ms por frame\n"
        details += f"Resolución temporal: ~23ms entre frames\n"
        
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, details)
        self.details_text.config(state='disabled')
    
    def export_results(self):
        """Exportar resultados a archivo JSON"""
        if not self.analysis_results:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        filename = filedialog.asksavfilename(
            title="Guardar resultados",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Texto", "*.txt"), ("Todos", "*.*")]
        )
        
        if filename:
            try:
                # Preparar datos para exportación
                export_data = {
                    "metadata": {
                        "export_date": datetime.now().isoformat(),
                        "analyzer_version": "1.0",
                        "file_analyzed": self.analysis_results['file_path']
                    },
                    "results": self.analysis_results
                }
                
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    # Exportar como texto
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("RESULTADOS DEL ANÁLISIS MUSICAL\n")
                        f.write("=" * 50 + "\n\n")
                        
                        f.write(f"Archivo: {os.path.basename(self.analysis_results['file_path'])}\n")
                        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Duración: {self.analysis_results['duration']:.2f}s\n\n")
                        
                        f.write("RESULTADOS PRINCIPALES:\n")
                        f.write(f"BPM: {self.analysis_results['bpm_analysis']['bpm']:.1f}\n")
                        f.write(f"Tonalidad: {self.analysis_results['key_analysis']['key']} {self.analysis_results['key_analysis']['scale']}\n\n")
                        
                        f.write("DETALLES COMPLETOS:\n")
                        f.write(json.dumps(self.analysis_results, indent=2, ensure_ascii=False))
                
                messagebox.showinfo("Éxito", f"Resultados exportados a:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def copy_to_clipboard(self):
        """Copiar resultados principales al portapapeles"""
        if not self.analysis_results:
            messagebox.showwarning("Advertencia", "No hay resultados para copiar")
            return
        
        try:
            bpm_data = self.analysis_results['bpm_analysis']
            key_data = self.analysis_results['key_analysis']

            clipboard_text = f"""Análisis Musical - {os.path.basename(self.analysis_results['file_path'])}

BPM: {bpm_data['bpm']:.1f} (confianza: {bpm_data['confidence']*100:.1f}%)
Tonalidad: {key_data['key']} {key_data['scale']} (confianza: {key_data['confidence']*100:.1f}%)
Duración: {self.analysis_results['duration']:.2f}s

Método BPM: {bpm_data['method']}
Método Key: {key_data['method']}"""
            
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
            messagebox.showinfo("Éxito", "Resultados copiados al portapapeles")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar: {str(e)}")
    
    def update_silence_label(self, value):
        """Actualizar label del umbral de silencio"""
        self.silence_value_label.config(text=f"{float(value):.0f} dB")
    
    def update_silence_dur_label(self, value):
        """Actualizar label de duración mínima de silencio"""
        self.silence_dur_label.config(text=f"{float(value):.1f} s")
    
    def reset_results(self):
        """Resetear todos los resultados mostrados"""
        self.analysis_results = None

        # Resetear labels de resultados
        self.bpm_result_label.config(text="---")
        self.bpm_confidence_label.config(text="Confianza: ---%")
        self.bpm_method_label.config(text="Método: ---")
        self.bpm_stability_label.config(text="Estabilidad: ---")
        
        self.key_result_label.config(text="---")
        self.key_confidence_label.config(text="Confianza: ---%")
        self.key_method_label.config(text="Método: ---")
        self.key_changes_label.config(text="Cambios: ---")
        
        # Limpiar textos
        self.file_info_text.delete(1.0, tk.END)
        self.silence_info_text.delete(1.0, tk.END)
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state='disabled')
        
        # Resetear visualización
        self.init_empty_plot()
    
    def check_dependencies(self):
        """Verificar estado de las dependencias"""
        libs_status = []
        
        # Verificar librerías principales
        try:
            import librosa  # noqa: F401
            libs_status.append("✅ librosa: Disponible")
        except ImportError:
            libs_status.append("❌ librosa: NO disponible")

        try:
            import essentia  # noqa: F401
            libs_status.append("✅ essentia: Disponible")
        except ImportError:
            libs_status.append("❌ essentia: NO disponible")

        try:
            import madmom  # noqa: F401
            libs_status.append("✅ madmom: Disponible (recomendado para BPM)")
        except ImportError:
            libs_status.append("⚠️ madmom: NO disponible (opcional pero recomendado)")

        try:
            import matplotlib  # noqa: F401
            libs_status.append("✅ matplotlib: Disponible")
        except ImportError:
            libs_status.append("❌ matplotlib: NO disponible")
        
        # Verificar analizador principal
        if ANALYZER_AVAILABLE:
            libs_status.append("✅ music_analyzer: Disponible")
        else:
            libs_status.append("❌ music_analyzer: NO disponible")
        
        # Actualizar display
        libs_text = "\n".join(libs_status)
        libs_text += "\n\nPara instalar las dependencias faltantes:\n"
        libs_text += "pip install librosa essentia-tensorflow madmom matplotlib scipy soundfile\n\n"
        libs_text += "Nota: madmom es opcional pero proporciona mejor precisión en BPM\n"
        libs_text += "para canciones con tempo variable."
        
        self.libs_text.config(state='normal')
        self.libs_text.delete(1.0, tk.END)
        self.libs_text.insert(tk.END, libs_text)
        self.libs_text.config(state='disabled')
    
    def show_help(self):
        """Mostrar ventana de ayuda"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Ayuda - Analizador Musical")
        help_window.geometry("600x500")
        help_window.configure(bg='#2b2b2b')
        
        help_text = scrolledtext.ScrolledText(help_window, bg='#3b3b3b', fg='white',
                                            font=('Arial', 10), wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """GUÍA DE USO - ANALIZADOR MUSICAL AVANZADO

🎵 FUNCIONALIDADES PRINCIPALES:
• Detección precisa de BPM (tempo)
• Análisis de tonalidad (key y escala)
• Detección de silencios
• Visualizaciones interactivas
• Exportación de resultados

📁 FORMATOS SOPORTADOS:
MP3, WAV, FLAC, OGG, M4A, AAC

🔍 CÓMO USAR:
1. Haz clic en "Seleccionar Audio" para elegir tu archivo
2. Ajusta la configuración si es necesario (pestaña Configuración)
3. Haz clic en "Analizar Audio" 
4. Revisa los resultados en las diferentes pestañas

📊 PESTAÑAS:

• Resultados: Muestra BPM, tonalidad y análisis de silencios
• Visualizaciones: Gráficos de beats, chromagram y onset strength
• Detalles Técnicos: Información completa del análisis
• Configuración: Ajustes y estado de librerías

🎯 INTERPRETACIÓN DE RESULTADOS:

BPM (Beats Per Minute):
- Confianza >80%: Muy confiable
- Confianza 60-80%: Confiable
- Confianza <60%: Revisar manualmente

Tonalidad:
- Confianza >70%: Muy probable
- Confianza 50-70%: Probable
- Confianza <50%: Incierta

⚙️ CONFIGURACIÓN:

Umbral de Silencio:
- -60 dB: Muy sensible (detecta susurros)
- -40 dB: Normal (recomendado)
- -20 dB: Poco sensible (solo silencios obvios)

Duración Mínima de Silencio:
- 0.1s: Detecta pausas muy breves
- 0.5s: Normal (recomendado)
- 2.0s: Solo silencios largos

🔬 ALGORITMOS UTILIZADOS:

• madmom: RNN + DBN para BPM preciso con tempo variable
• Essentia: Análisis tonal avanzado por segmentos
• librosa: Análisis espectral y procesamiento de audio

⚠️ NOTAS IMPORTANTES:

• El análisis puede tomar varios segundos para archivos largos
• Canciones con tempo muy variable pueden ser más difíciles de analizar
• La calidad del archivo de audio afecta la precisión
• Géneros electrónicos suelen tener mejor precisión en BPM
• Música clásica puede tener mayor variabilidad temporal

💡 CONSEJOS:

• Para mejor precisión, usa archivos de alta calidad
• Si el BPM parece incorrecto, puede ser la mitad o el doble del real
• Las modulaciones pueden afectar la detección de tonalidad
• Revisa las visualizaciones para validar los resultados

🆘 SOLUCIÓN DE PROBLEMAS:

• Error al cargar archivo: Verifica el formato
• Resultados inconsistentes: Revisa la calidad del audio
• Análisis lento: Archivos muy largos tardan más
• Librerías faltantes: Instala las dependencias"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state='disabled')
    
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """🎵 Analizador Musical Avanzado v1.0

Desarrollado para análisis preciso de música con:
• Detección avanzada de BPM y tempo variable
• Análisis tonal por segmentos
• Detección inteligente de silencios
• Visualizaciones interactivas

Librerías utilizadas:
• madmom (RNN + DBN beat tracking)
• Essentia (análisis tonal avanzado)  
• librosa (procesamiento de audio)
• matplotlib (visualizaciones)

Características:
✅ Manejo de tempo variable
✅ Detección de cambios tonales
✅ Análisis robusto de silencios
✅ Exportación de resultados
✅ Interfaz gráfica moderna

Compatible con: MP3, WAV, FLAC, OGG, M4A, AAC

Para más información y actualizaciones, visita el repositorio del proyecto."""
        
        messagebox.showinfo("Acerca de", about_text)

def main():
    """Función principal"""
    root = tk.Tk()
    app = MusicAnalyzerGUI(root)
    
    # Configurar cierre de aplicación
    def on_closing():
        if app.is_analyzing:
            if messagebox.askyesno("Confirmación", "Hay un análisis en curso. ¿Deseas salir?"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Iniciar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()