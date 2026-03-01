import streamlit as st
import yt_dlp
import os
import re
import tempfile
import subprocess

st.set_page_config(page_title="Cortador Pro ✂️", page_icon="⚡", layout="centered")

def limpar_nome_arquivo(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome)

def tempo_para_segundos(tempo_str):
    try:
        partes = tempo_str.split(':')
        segundos = 0
        for parte in partes:
            segundos = segundos * 60 + float(parte)
        return segundos
    except Exception:
        return 0

st.title("⚡ Baixador de Trechos Pro")
st.markdown("Cole o link, defina os tempos e baixe direto no seu celular!")

url = st.text_input("Link do YouTube:", placeholder="https://www.youtube.com/...")

st.markdown("### ✂️ Configure seus Cortes")

cortes_config = []

for i in range(1, 11):
    with st.expander(f"📌 Corte {i}", expanded=(i == 1)):
        col1, col2 = st.columns(2)
        inicio = col1.text_input(f"Início (ex: 00:15)", key=f"inicio_{i}")
        fim = col2.text_input(f"Fim (ex: 01:30)", key=f"fim_{i}")
        
        titulo = st.text_input(f"Título do Arquivo", placeholder=f"Trecho_{i}", key=f"tit_{i}")
        descricao = st.text_area(f"Legenda / Hashtags", height=68, key=f"desc_{i}")
        
        cortes_config.append({
            "index": i, "inicio": inicio, "fim": fim, 
            "titulo": titulo, "descricao": descricao
        })

if st.button("🚀 Processar Downloads", type="primary", use_container_width=True):
    if not url:
        st.error("⚠️ Por favor, cole um link do YouTube primeiro!")
    else:
        cortes_validos = [c for c in cortes_config if c["inicio"] and c["fim"]]
        
        if not cortes_validos:
            st.warning("⚠️ Preencha pelo menos o Início e o Fim de um corte!")
        else:
            with st.spinner("Preparando o vídeo base (Disfarce de Celular Ativado)..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        
                        # === DISFARCE SUPREMO PARA BURLAR O ERRO 403 ===
                        ydl_opts_base = {
                            'format': 'best',
                            'outtmpl': os.path.join(tmpdirname, 'video_completo.%(ext)s'),
                            'quiet': True,
                            'noplaylist': True,
                            'extractor_args': {'youtube': ['player_client=android']}, # Finge ser o App do Android!
                            'http_headers': {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36'}
                        }
                        
                        with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
                            info = ydl.extract_info(url, download=True)
                            ext = info.get('ext', 'mp4')
                            titulo_video = info.get('title', 'Video_Sem_Titulo')
                            video_completo_path = os.path.join(tmpdirname, f'video_completo.{ext}')
                        
                        st.success(f"✅ Vídeo base baixado! Cortando os trechos...")
                        
                        for corte in cortes_validos:
                            st.write(f"⏳ Finalizando **Corte {corte['index']}**...")
                            
                            inicio_sec = tempo_para_segundos(corte['inicio'])
                            fim_sec = tempo_para_segundos(corte['fim'])
                            
                            nome_base = limpar_nome_arquivo(corte['titulo']) if corte['titulo'].strip() else f"Trecho_{corte['index']}"
                            caminho_video = os.path.join(tmpdirname, f"{nome_base}.mp4")
                            
                            comando = [
                                'ffmpeg', '-y', '-i', video_completo_path,
                                '-ss', str(inicio_sec), '-to', str(fim_sec),
                                '-c:v', 'copy', '-c:a', 'copy', caminho_video
                            ]
                            
                            resultado = subprocess.run(comando, capture_output=True, text=True)
                            
                            if resultado.returncode == 0 and os.path.exists(caminho_video):
                                st.success(f"✅ Corte {corte['index']} concluído!")
                                
                                with open(caminho_video, "rb") as file:
                                    st.download_button(
                                        label=f"📥 Baixar Vídeo ({nome_base}.mp4)",
                                        data=file,
                                        file_name=f"{nome_base}.mp4",
                                        mime="video/mp4",
                                        key=f"dl_vid_{corte['index']}"
                                    )
                                
                                if corte['descricao'].strip():
                                    st.download_button(
                                        label=f"📝 Baixar Legenda (.txt)",
                                        data=corte['descricao'],
                                        file_name=f"{nome_base}.txt",
                                        mime="text/plain",
                                        key=f"dl_txt_{corte['index']}"
                                    )
                                st.divider()
                            else:
                                st.error(f"❌ Falha ao cortar o trecho {corte['index']}.")
                                
                except Exception as e:
                    st.error(f"❌ Erro crítico: {e}")
