import customtkinter as ctk
import yt_dlp
from yt_dlp.utils import download_range_func # <-- NOVO IMPORT MÁGICO
import threading
import os
import re

# Configuração visual geral
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cortador de Vídeos Pro ✂️")
        self.geometry("1150x800")
        self.configure(fg_color="#1E1E2E") 

        # Título principal
        self.lbl_titulo = ctk.CTkLabel(self, text="⚡ Baixador e Organizador de Trechos ⚡", font=("Arial", 28, "bold"), text_color="#00E676")
        self.lbl_titulo.pack(pady=(20, 10))

        # Campo do Link
        self.frame_link = ctk.CTkFrame(self, fg_color="#282A36", corner_radius=15)
        self.frame_link.pack(pady=10, padx=20, fill="x")
        
        self.url_label = ctk.CTkLabel(self.frame_link, text="Link do YouTube:", font=("Arial", 14, "bold"), text_color="#8BE9FD")
        self.url_label.pack(side="left", padx=(20, 10), pady=20)
        
        self.url_entry = ctk.CTkEntry(self.frame_link, width=450, placeholder_text="Cole o link aqui...", border_color="#6272A4")
        self.url_entry.pack(side="left", padx=10, pady=20)

        # Frame rolável para as 10 opções
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#282A36", corner_radius=15, label_text="Configure seus Cortes", label_font=("Arial", 16, "bold"), label_text_color="#FF79C6")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.linhas = []
        
        # Cabeçalhos
        ctk.CTkLabel(self.scroll_frame, text="Início", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(self.scroll_frame, text="Fim", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(self.scroll_frame, text="Título do Corte", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(self.scroll_frame, text="Descrição / Legenda", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(self.scroll_frame, text="Progresso", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkLabel(self.scroll_frame, text="Status", font=("Arial", 12, "bold")).grid(row=0, column=5, padx=5, pady=5)

        # Gerando as 10 linhas
        for i in range(1, 11):
            ent_inicio = ctk.CTkEntry(self.scroll_frame, width=70, placeholder_text="00:00", justify="center")
            ent_inicio.grid(row=i, column=0, padx=5, pady=10)
            
            ent_fim = ctk.CTkEntry(self.scroll_frame, width=70, placeholder_text="00:00", justify="center")
            ent_fim.grid(row=i, column=1, padx=5, pady=10)
            
            ent_titulo = ctk.CTkEntry(self.scroll_frame, width=180, placeholder_text=f"Corte {i}")
            ent_titulo.grid(row=i, column=2, padx=5, pady=10)
            
            ent_desc = ctk.CTkEntry(self.scroll_frame, width=250, placeholder_text="Hashtags ou legenda...")
            ent_desc.grid(row=i, column=3, padx=5, pady=10)
            
            progresso = ctk.CTkProgressBar(self.scroll_frame, width=120, progress_color="#F1FA8C", mode="indeterminate")
            progresso.grid(row=i, column=4, padx=10, pady=10)
            progresso.set(0) # Inicia zerada
            
            lbl_status = ctk.CTkLabel(self.scroll_frame, text="Aguardando...", text_color="#6272A4", width=100)
            lbl_status.grid(row=i, column=5, padx=5, pady=10)
            
            self.linhas.append({
                "inicio": ent_inicio, 
                "fim": ent_fim, 
                "titulo": ent_titulo,
                "descricao": ent_desc,
                "progresso": progresso, 
                "status": lbl_status
            })

        # Botão e Status Geral
        self.btn_download = ctk.CTkButton(self, text="🚀 Iniciar Downloads", font=("Arial", 16, "bold"), height=40, command=self.preparar_download, fg_color="#50FA7B", text_color="#282A36", hover_color="#38E563")
        self.btn_download.pack(pady=(10, 5))

        self.status_geral = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.status_geral.pack(pady=(0, 20))

    def limpar_nome_arquivo(self, nome):
        return re.sub(r'[\\/*?:"<>|]', "", nome)

    # NOVO: Função para converter "01:30" em 90 segundos
    def tempo_para_segundos(self, tempo_str):
        try:
            partes = tempo_str.split(':')
            segundos = 0
            for parte in partes:
                segundos = segundos * 60 + float(parte)
            return segundos
        except Exception:
            return 0

    def preparar_download(self):
        url = self.url_entry.get()
        if not url:
            self.status_geral.configure(text="Por favor, insira um link primeiro!", text_color="#FF5555")
            return

        self.btn_download.configure(state="disabled", text="⏳ Processando...")
        self.status_geral.configure(text="Buscando informações do vídeo...", text_color="#F1FA8C")
        
        threading.Thread(target=self.iniciar_downloads_em_lote, args=(url,)).start()

    def iniciar_downloads_em_lote(self, url):
        try:
            ydl_opts_info = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                titulo_video = info.get('title', 'Video_Sem_Titulo')
            
            nome_pasta = self.limpar_nome_arquivo(titulo_video)
            
            if not os.path.exists(nome_pasta):
                os.makedirs(nome_pasta)
            
            self.status_geral.configure(text=f"Pasta '{nome_pasta}' criada. Baixando...", text_color="#8BE9FD")

            for i, linha in enumerate(self.linhas, start=1):
                inicio = linha["inicio"].get()
                fim = linha["fim"].get()
                
                if inicio and fim:
                    threading.Thread(target=self.baixar_trecho, args=(url, inicio, fim, i, nome_pasta, linha)).start()
            
            self.btn_download.configure(state="normal", text="🚀 Iniciar Downloads")

        except Exception as e:
            self.status_geral.configure(text=f"Erro ao ler o vídeo: {e}", text_color="#FF5555")
            self.btn_download.configure(state="normal", text="🚀 Iniciar Downloads")

    def baixar_trecho(self, url, inicio, fim, index, pasta, linha_ui):
        linha_ui["status"].configure(text="Baixando...", text_color="#F1FA8C")
        linha_ui["progresso"].start()

        titulo_corte = linha_ui["titulo"].get()
        descricao_corte = linha_ui["descricao"].get()

        if titulo_corte.strip():
            nome_base = self.limpar_nome_arquivo(titulo_corte)
        else:
            nome_base = f'Trecho_{index}_{inicio.replace(":","")}_a_{fim.replace(":","")}'

        caminho_video = os.path.join(pasta, f'{nome_base}.mp4')
        caminho_texto = os.path.join(pasta, f'{nome_base}.txt')

        # Convertendo o tempo para a nova regra do yt-dlp
        inicio_sec = self.tempo_para_segundos(inicio)
        fim_sec = self.tempo_para_segundos(fim)

        # === CONFIGURAÇÃO CORRIGIDA PARA 1080P COM ÁUDIO ===
        ydl_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best', 
            'merge_output_format': 'mp4',         
            'outtmpl': caminho_video,
            # Usa a função nativa de ranges em vez de forçar o FFmpeg cru
            'download_ranges': download_range_func(None, [(inicio_sec, fim_sec)]),
            'force_keyframes_at_cuts': True, # Garante um corte perfeito
            'quiet': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if descricao_corte.strip():
                with open(caminho_texto, "w", encoding="utf-8") as f:
                    f.write(descricao_corte)
            
            linha_ui["progresso"].stop()
            linha_ui["progresso"].set(1)
            linha_ui["progresso"].configure(progress_color="#50FA7B")
            linha_ui["status"].configure(text="Concluído!", text_color="#50FA7B")
            
        except Exception as e:
            linha_ui["progresso"].stop()
            linha_ui["progresso"].configure(progress_color="#FF5555")
            linha_ui["status"].configure(text="Erro!", text_color="#FF5555")
            print(f"Erro na linha {index}: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
