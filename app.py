# ============================================================
# app.py
# ============================================================
# Este é o arquivo PRINCIPAL do projeto: a interface gráfica,
# construída com Streamlit. É aqui que juntamos as peças que
# criamos nos outros arquivos:
#
#   camera.py     -> liga a webcam e captura um frame
#   preprocess.py -> melhora a qualidade da imagem
#   ocr.py        -> reconhece o texto na imagem (Inteligência Artificial)
#   config.py     -> valores de configuração usados em todo o projeto
#
# PIPELINE COMPLETO (o "caminho" que a imagem percorre):
#
#   Webcam -> Captura -> Pré-processamento -> OCR -> Interface
#
# Para rodar esta aplicação, use o comando (com o ambiente
# virtual ativado):
#
#       streamlit run app.py
#
# ============================================================

import io                    # Usado para criar o arquivo .txt em memória (para o botão de download)
import cv2                   # Biblioteca de visão computacional
import streamlit as st       # Biblioteca que cria a interface gráfica no navegador

import config                # Nossas configurações
import camera                # Funções de captura da webcam
import preprocess            # Funções de pré-processamento de imagem
from ocr import OCREngine, build_sentence   # Motor de OCR e organizador de texto


# ------------------------------------------------------------
# 1) CONFIGURAÇÃO GERAL DA PÁGINA
# ------------------------------------------------------------
# st.set_page_config define o título da aba do navegador, o
# ícone e o layout (aqui usamos "wide" para aproveitar melhor
# a largura da tela).
st.set_page_config(
    page_title="OCR com Webcam - Senai Cimatec",
    page_icon="🔎",
    layout="wide",
)


# ------------------------------------------------------------
# 2) CARREGAMENTO DO MOTOR DE OCR (feito apenas UMA VEZ)
# ------------------------------------------------------------
# @st.cache_resource é uma "decoração" do Streamlit que diz:
# "execute esta função só na primeira vez; nas próximas, reuse
# o resultado já calculado". Isso é essencial aqui, pois
# carregar o modelo de IA é uma operação lenta — não queremos
# repeti-la toda vez que o usuário clicar em um botão.
@st.cache_resource(show_spinner="Carregando o motor de OCR (isso só acontece uma vez)...")
def carregar_motor_ocr():
    motor = OCREngine()
    motor.load()
    return motor


# ------------------------------------------------------------
# 3) "MEMÓRIA" DA APLICAÇÃO (session_state)
# ------------------------------------------------------------
# O Streamlit executa o script de cima a baixo TODA VEZ que o
# usuário interage com algo (clica em um botão, move um
# slider...). Para "lembrar" de valores entre uma execução e
# outra (como a webcam já aberta, ou o último texto lido),
# usamos o st.session_state — um dicionário que persiste
# durante toda a sessão do usuário no navegador.
if "webcam_aberta" not in st.session_state:
    st.session_state.webcam_aberta = False
if "objeto_camera" not in st.session_state:
    st.session_state.objeto_camera = None
if "texto_extraido" not in st.session_state:
    st.session_state.texto_extraido = ""


# ------------------------------------------------------------
# 4) BARRA LATERAL (sidebar) — controles do usuário
# ------------------------------------------------------------
st.sidebar.title("⚙️ Controles")

# Slider de confiança: o usuário escolhe o quão "rigoroso" o
# OCR deve ser ao aceitar uma palavra como válida.
confianca_minima = st.sidebar.slider(
    "Confiança mínima do OCR",
    min_value=0.0,
    max_value=1.0,
    value=config.DEFAULT_CONFIDENCE,
    step=0.05,
    help=(
        "Cada palavra reconhecida vem com uma 'nota de confiança' "
        "de 0 a 1. Palavras com confiança ABAIXO deste valor são "
        "descartadas, para evitar erros."
    ),
)

# Checkbox para ativar/desativar a correção de inclinação (deskew)
usar_deskew = st.sidebar.checkbox(
    "Corrigir inclinação do texto (deskew)",
    value=True,
    help="Endireita o texto automaticamente, caso a foto esteja torta.",
)

st.sidebar.markdown("---")

# Botão para ligar/desligar a webcam
if not st.session_state.webcam_aberta:
    if st.sidebar.button("📷 Ligar webcam", use_container_width=True):
        st.session_state.objeto_camera = camera.abrir_webcam()
        if camera.camera_esta_aberta(st.session_state.objeto_camera):
            st.session_state.webcam_aberta = True
        else:
            st.sidebar.error(
                "Não foi possível abrir a webcam. Verifique se ela "
                "está conectada e se nenhum outro programa está usando-a."
            )
else:
    if st.sidebar.button("⏹️ Desligar webcam", use_container_width=True):
        camera.fechar_webcam(st.session_state.objeto_camera)
        st.session_state.objeto_camera = None
        st.session_state.webcam_aberta = False

st.sidebar.markdown("---")
st.sidebar.caption(
    "Pipeline: Webcam → Pré-processamento → OCR (IA) → Interface"
)


# ------------------------------------------------------------
# 5) CABEÇALHO PRINCIPAL
# ------------------------------------------------------------
st.title("🔎 Reconhecimento Óptico de Caracteres (OCR) com Webcam")
st.write(
    "Este projeto captura uma imagem da webcam do seu notebook, "
    "melhora a qualidade dela e usa um modelo de Inteligência "
    "Artificial para transformar o texto da imagem em texto "
    "editável."
)


# ------------------------------------------------------------
# 6) BOTÃO PRINCIPAL: CAPTURAR E RECONHECER
# ------------------------------------------------------------
botao_capturar = st.button(
    "📸 Capturar frame e reconhecer texto",
    type="primary",
    disabled=not st.session_state.webcam_aberta,
)

if not st.session_state.webcam_aberta:
    st.info("👈 Clique em **Ligar webcam**, na barra lateral, para começar.")

# Este bloco só executa quando o usuário clica no botão acima
if botao_capturar and st.session_state.webcam_aberta:

    # --- ETAPA 1: CAPTURA -------------------------------------------------
    # Pedimos um frame novo à webcam já aberta.
    sucesso, frame_bgr = camera.capturar_frame(st.session_state.objeto_camera)

    if not sucesso:
        st.error("Não foi possível capturar a imagem da webcam. Tente novamente.")
    else:
        # --- ETAPA 2: PRÉ-PROCESSAMENTO ------------------------------------
        # Aplicamos escala de cinza + CLAHE + remoção de ruído + (opcional) deskew
        imagem_processada = preprocess.pre_processar_imagem(
            frame_bgr,
            aplicar_deskew=usar_deskew,
        )

        # --- ETAPA 3: RECONHECIMENTO (OCR / IA) ----------------------------
        motor_ocr = carregar_motor_ocr()
        with st.spinner("Reconhecendo texto..."):
            palavras_encontradas = motor_ocr.recognize(
                imagem_processada,
                confidence_threshold=confianca_minima,
            )

        # --- ETAPA 4: MONTAGEM DO TEXTO FINAL -------------------------------
        texto_final = build_sentence(palavras_encontradas)
        st.session_state.texto_extraido = texto_final

        # --- "MONITOR SERIAL" (Terminal) ------------------------------------
        # Além de mostrar na tela, também imprimimos no terminal/console,
        # como pedido no projeto (parecido com o Monitor Serial do Arduino).
        print("\n===== TEXTO RECONHECIDO =====")
        print(texto_final if texto_final else "(nenhum texto encontrado)")
        print("==============================\n")

        # --- DESENHAR AS CAIXAS DELIMITADORAS (bounding boxes) --------------
        # Fazemos uma cópia da imagem original para desenhar por cima,
        # sem estragar o frame original.
        imagem_com_caixas = frame_bgr.copy()
        for palavra in palavras_encontradas:
            # "box" tem 4 pontos [x, y]; convertemos para inteiros,
            # pois o OpenCV precisa de coordenadas de pixel inteiras.
            pontos = [(int(x), int(y)) for x, y in palavra["box"]]

            # Desenha o retângulo/polígono verde ao redor da palavra
            for i in range(len(pontos)):
                ponto_inicial = pontos[i]
                ponto_final = pontos[(i + 1) % len(pontos)]
                cv2.line(imagem_com_caixas, ponto_inicial, ponto_final, (0, 255, 0), 2)

            # Escreve o texto reconhecido acima da caixa
            texto_label = f'{palavra["text"]} ({palavra["confidence"]:.2f})'
            posicao_texto = (pontos[0][0], max(pontos[0][1] - 8, 0))
            cv2.putText(
                imagem_com_caixas,
                texto_label,
                posicao_texto,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

        # --- ETAPA 5: EXIBIÇÃO NA INTERFACE ---------------------------------
        st.markdown("### 🖼️ Imagens")
        coluna_1, coluna_2 = st.columns(2)

        with coluna_1:
            st.caption("Imagem original + caixas delimitadoras")
            # O OpenCV usa BGR, mas o Streamlit espera RGB — por isso convertemos
            imagem_rgb = cv2.cvtColor(imagem_com_caixas, cv2.COLOR_BGR2RGB)
            st.image(imagem_rgb, use_container_width=True)

        with coluna_2:
            st.caption("Imagem pré-processada (o que o OCR realmente 'vê')")
            st.image(imagem_processada, use_container_width=True, channels="GRAY")

        st.markdown("### 📝 Texto extraído")
        if texto_final:
            st.text_area(
                "Resultado do OCR",
                value=texto_final,
                height=150,
            )
            st.caption(
                f"{len(palavras_encontradas)} palavra(s) reconhecida(s) "
                f"com confiança mínima de {confianca_minima:.2f}."
            )
        else:
            st.warning(
                "Nenhum texto foi encontrado com o nível de confiança "
                "escolhido. Tente diminuir o slider de confiança na "
                "barra lateral ou aproximar o texto da câmera."
            )


# ------------------------------------------------------------
# 7) BOTÃO DE DOWNLOAD (sempre visível, se já houver texto)
# ------------------------------------------------------------
if st.session_state.texto_extraido:
    st.markdown("---")
    # io.BytesIO cria um "arquivo" em memória, sem precisar
    # salvar nada no disco do computador.
    conteudo_arquivo = io.BytesIO(st.session_state.texto_extraido.encode("utf-8"))

    st.download_button(
        label="⬇️ Baixar texto reconhecido (.txt)",
        data=conteudo_arquivo,
        file_name="texto_reconhecido.txt",
        mime="text/plain",
    )