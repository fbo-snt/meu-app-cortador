import streamlit as st
import yt_dlp
from yt_dlp.utils import download_range_func
import os
import re
import tempfile

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
st.markdown("Cole o link, defina os tempos e baixe direto no seu celular/PC!")

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
            with st.spinner("Buscando informações do vídeo..."):
                try:
                    ydl_opts_info = {'quiet': True}
                    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                        info = ydl.extract_info(url, download=False)
                        titulo_video = info.get('title', 'Video_Sem_Titulo')
                    
                    st.success(f"Vídeo encontrado: **{titulo_video}**")
                    
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        for corte in cortes_validos:
                            st.write(f"⏳ Processando **Corte {corte['index']}** ({corte['inicio']} até {corte['fim']})...")
                            
                            inicio_sec = tempo_para_segundos(corte['inicio'])
                            fim_sec = tempo_para_segundos(corte['fim'])
                            
                            nome_base = limpar_nome_arquivo(corte['titulo']) if corte['titulo'].strip() else f"Trecho_{corte['index']}"
                            caminho_video = os.path.join(tmpdirname, f"{nome_base}.mp4")
                            
                            ydl_opts = {
                                'format': 'best',
                                'outtmpl': caminho_video,
                                'download_ranges': download_range_func(None, [(inicio_sec, fim_sec)]),
                                'force_keyframes_at_cuts': True,
                                'quiet': True,
                                'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
                                'external_downloader_args': {'ffmpeg': ['-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '5']}
                            }
                            
                            try:
                                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                    ydl.download([url])
                                
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
                                
                            except Exception as e:
                                st.error(f"❌ Erro no Corte {corte['index']}: {e}")
                                
                except Exception as e:

                    st.error(f"❌ Erro ao acessar o link: {e}")
