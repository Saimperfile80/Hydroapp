import tkinter as tk
from tkinter import ttk
import webbrowser
import os
import tempfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

class HomeWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HydroFlow AI")
        self.geometry("1200x900+100+100")
        
        # Créer un fichier HTML temporaire
        self.html_file = self.create_html_file()
        
        # Démarrer un serveur local
        self.start_local_server()
        
        # Attendre un peu pour que le serveur démarre
        time.sleep(1)
        
        # Ouvrir le navigateur
        webbrowser.open("http://localhost:8000")
        
        # Créer une interface de fermeture
        self.create_gui()
        
        # Créer un fichier HTML temporaire
        self.html_file = self.create_html_file()
        
        # Démarrer un serveur local
        self.start_local_server()
        
        # Attendre un peu pour que le serveur démarre
        time.sleep(1)
        
        # Ouvrir le navigateur
        webbrowser.open("http://localhost:8000")
        
        # Créer une interface de fermeture
        self.create_gui()
        
    def create_html_file(self):
        """Créer un fichier HTML temporaire avec l'interface"""
        html_content = """<!DOCTYPE html>
<html class="light" lang="fr">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>HydroFlow</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#13a4ec",
                        "background-light": "#f6f7f8",
                        "background-dark": "#101c22",
                    },
                    fontFamily: {
                        "display": ["Inter"]
                    },
                    borderRadius: {
                        "DEFAULT": "1rem",
                        "lg": "2rem",
                        "xl": "3rem",
                        "full": "9999px"
                    },
                },
            },
        }
    </script>
    <style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        body {
            min-height: max(884px, 100dvh);
        }
    </style>
</head>
<body class="font-display">
    <div class="relative flex min-h-screen w-full flex-col bg-background-light dark:bg-background-dark">
        <div class="flex-grow">
            <h1 class="font-display tracking-light text-[32px] font-bold leading-tight px-4 text-left pb-3 pt-6 text-[#0d171b] dark:text-slate-50">HydroFlow AI</h1>
            <div class="grid grid-cols-[repeat(auto-fit,minmax(158px,1fr))] gap-4 p-4">
                <div class="flex flex-1 flex-col gap-3 rounded-lg border border-[#e7eff3] dark:border-slate-700 bg-white dark:bg-slate-800 p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow">
                    <span class="material-symbols-outlined text-primary" style="font-size: 28px;">waves</span>
                    <div class="flex flex-col gap-1">
                        <h2 class="text-[#0d171b] dark:text-slate-50 text-base font-bold leading-tight">Pompage</h2>
                        <p class="text-[#4c809a] dark:text-slate-400 text-sm font-normal leading-normal">Analyze and interpret pumping test data.</p>
                    </div>
                </div>
                <div class="flex flex-1 flex-col gap-3 rounded-lg border border-[#e7eff3] dark:border-slate-700 bg-white dark:bg-slate-800 p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow">
                    <span class="material-symbols-outlined text-primary" style="font-size: 28px;">layers</span>
                    <div class="flex flex-col gap-1">
                        <h2 class="text-[#0d171b] dark:text-slate-50 text-base font-bold leading-tight">Perméabilité</h2>
                        <p class="text-[#4c809a] dark:text-slate-400 text-sm font-normal leading-normal">Calculate soil and rock permeability.</p>
                    </div>
                </div>
                <div class="flex flex-1 flex-col gap-3 rounded-lg border border-[#e7eff3] dark:border-slate-700 bg-white dark:bg-slate-800 p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow">
                    <span class="material-symbols-outlined text-primary" style="font-size: 28px;">show_chart</span>
                    <div class="flex flex-col gap-1">
                        <h2 class="text-[#0d171b] dark:text-slate-50 text-base font-bold leading-tight">Piézométrie</h2>
                        <p class="text-[#4c809a] dark:text-slate-400 text-sm font-normal leading-normal">Map and monitor groundwater levels.</p>
                    </div>
                </div>
                <div class="flex flex-1 flex-col gap-3 rounded-lg border border-[#e7eff3] dark:border-slate-700 bg-white dark:bg-slate-800 p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow">
                    <span class="material-symbols-outlined text-primary" style="font-size: 28px;">article</span>
                    <div class="flex flex-col gap-1">
                        <h2 class="text-[#0d171b] dark:text-slate-50 text-base font-bold leading-tight">Rapports</h2>
                        <p class="text-[#4c809a] dark:text-slate-400 text-sm font-normal leading-normal">Generate and manage your analysis reports.</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="fixed bottom-24 right-4 z-10">
            <button class="flex h-14 w-14 cursor-pointer items-center justify-center overflow-hidden rounded-full bg-primary text-white shadow-lg hover:shadow-xl transition-shadow">
                <span class="material-symbols-outlined" style="font-size: 24px;">auto_awesome</span>
            </button>
        </div>
        <div class="sticky bottom-0">
            <div class="flex gap-2 border-t border-[#e7eff3] dark:border-slate-700 bg-background-light dark:bg-background-dark/80 px-4 pb-3 pt-2 backdrop-blur-sm">
                <a class="flex flex-1 flex-col items-center justify-end gap-1 rounded-full text-primary cursor-pointer" href="javascript:void(0);">
                    <div class="flex h-8 items-center justify-center">
                        <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1, 'wght' 400; font-size: 24px;">home</span>
                    </div>
                    <p class="text-xs font-medium leading-normal tracking-[0.015em] text-primary">Home</p>
                </a>
                <a class="flex flex-1 flex-col items-center justify-end gap-1 text-[#4c809a] dark:text-slate-400 cursor-pointer" href="javascript:void(0);">
                    <div class="flex h-8 items-center justify-center">
                        <span class="material-symbols-outlined" style="font-size: 24px;">folder</span>
                    </div>
                    <p class="text-xs font-medium leading-normal tracking-[0.015em]">Projects</p>
                </a>
                <a class="flex flex-1 flex-col items-center justify-end gap-1 text-[#4c809a] dark:text-slate-400 cursor-pointer" href="javascript:void(0);">
                    <div class="flex h-8 items-center justify-center">
                        <span class="material-symbols-outlined" style="font-size: 24px;">account_circle</span>
                    </div>
                    <p class="text-xs font-medium leading-normal tracking-[0.015em]">Profile</p>
                </a>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        # Créer un fichier temporaire
        temp_dir = tempfile.gettempdir()
        html_path = os.path.join(temp_dir, "hydroflow.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def start_local_server(self):
        """Démarrer un serveur HTTP local en arrière-plan"""
        def run_server():
            os.chdir(os.path.dirname(self.html_file))
            handler = SimpleHTTPRequestHandler
            server = HTTPServer(('localhost', 8000), handler)
            self.server = server
            server.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def create_gui(self):
        """Créer l'interface Tkinter"""
        frame = ttk.Frame(self)
        frame.pack(pady=20, padx=20)
        
        label = ttk.Label(frame, text="HydroFlow AI - Interface Web", font=("Arial", 14, "bold"))
        label.pack()
        
        info = ttk.Label(frame, text="L'interface s'ouvre dans votre navigateur par défaut.\nVous pouvez fermer cette fenêtre.", justify="center")
        info.pack(pady=10)
        
        close_btn = ttk.Button(frame, text="Fermer", command=self.quit)
        close_btn.pack(pady=10)