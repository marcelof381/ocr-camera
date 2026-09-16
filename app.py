# ============================================================
# app.py
# ============================================================

import io
import cv2
import numpy as np
import streamlit as st

import config
import preprocess
from ocr import OCREngine, build_sentence

st.set_page_config(
    page_title="OCR com Webcam - Senai Cimatec",
    page_icon="🔎",
    layout="wide",
)

@st.cache_resource(show_spinner="Carregando o motor de OCR (isso só acontece uma vez)...")
def carregar_motor_ocr():
    motor = OCREngine()
    motor.load()
    return motor

if "texto_extraido" not in st.session_state:
    st.session_state.texto_extraido = ""

# --- BARRA LATERAL ---
st.sidebar.title("⚙️ Controles")
confianca_minima = st.sidebar.slider(
    "Confiança mínima do OCR", 0.0, 1.0, config.DEFAULT_CONFIDENCE, 0.05
)
usar_deskew = st.sidebar.checkbox(
    "Corrigir inclinação do texto (deskew)", value=True
)
st.sidebar.markdown("---")
st.sidebar.caption("Pipeline: Webcam → Pré-processamento → OCR (IA) → Interface")

# --- CABEÇALHO ---
st.title("🔎 Reconhecimento Óptico de Caracteres (OCR) com Webcam")
st.write("Visualize o texto na câmera abaixo e capture a imagem para extrair o texto.")

# --- PREVIEW DA CÂMERA (STREAMLIT NATIVO) ---
foto_capturada = st.camera_input("📸 Capture a imagem para análise")

if foto_capturada is not None:
    # A foto capturada é um arquivo em memória. Convertendo para padrão OpenCV (Matriz BGR)
    bytes_data = foto_capturada.getvalue()
    frame_bgr = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Pré-Processamento
    imagem_processada = preprocess.pre_processar_imagem(frame_bgr, aplicar_deskew=usar_deskew)

    # OCR
    motor_ocr = carregar_motor_ocr()
    with st.spinner("Reconhecendo texto e ajustando leitura..."):
        palavras_encontradas = motor_ocr.recognize(imagem_processada, confidence_threshold=confianca_minima)

    # Montagem do Texto
    texto_final = build_sentence(palavras_encontradas)
    st.session_state.texto_extraido = texto_final

    print("\n===== TEXTO RECONHECIDO =====")
    print(texto_final if texto_final else "(nenhum texto encontrado)")
    print("==============================\n")

    # Desenho das Caixas
    imagem_com_caixas = frame_bgr.copy()
    for palavra in palavras_encontradas:
        pontos = [(int(x), int(y)) for x, y in palavra["box"]]
        for i in range(len(pontos)):
            ponto_inicial = pontos[i]
            ponto_final = pontos[(i + 1) % len(pontos)]
            cv2.line(imagem_com_caixas, ponto_inicial, ponto_final, (0, 255, 0), 2)
        
        posicao_texto = (pontos[0][0], max(pontos[0][1] - 8, 0))
        cv2.putText(
            imagem_com_caixas, f'{palavra["text"]}', posicao_texto,
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA
        )

    # Exibição
    st.markdown("### 🖼️ Imagens Processadas")
    coluna_1, coluna_2 = st.columns(2)

    with coluna_1:
        st.caption("Imagem original + caixas delimitadoras")
        imagem_rgb = cv2.cvtColor(imagem_com_caixas, cv2.COLOR_BGR2RGB)
        st.image(imagem_rgb, use_container_width=True)

    with coluna_2:
        st.caption("Imagem pré-processada (o que o OCR realmente 'vê')")
        st.image(imagem_processada, use_container_width=True, channels="GRAY")

    st.markdown("### 📝 Texto extraído")
    if texto_final:
        st.text_area("Resultado do OCR", value=texto_final, height=200)
        st.caption(f"{len(palavras_encontradas)} palavra(s) reconhecida(s).")
    else:
        st.warning("Nenhum texto foi encontrado. Ajuste a confiança ou a iluminação.")

if st.session_state.texto_extraido:
    st.markdown("---")
    conteudo_arquivo = io.BytesIO(st.session_state.texto_extraido.encode("utf-8"))
    st.download_button(
        label="⬇️ Baixar texto reconhecido (.txt)",
        data=conteudo_arquivo,
        file_name="texto_reconhecido.txt",
        mime="text/plain",
    )