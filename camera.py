# ============================================================
# camera.py
# ============================================================
# Este arquivo cuida de UMA responsabilidade só: conversar com
# a webcam do notebook. Ele não sabe nada sobre OCR, filtros ou
# interface gráfica — só sabe "ligar a câmera" e "tirar uma
# foto (frame)". Isso deixa o código mais fácil de entender e
# de reaproveitar.
#
# CONCEITO SIMPLES:
# Uma webcam gera continuamente "fotos" chamadas de FRAMES.
# O OpenCV consegue se conectar à câmera e, a cada chamada de
# cap.read(), pega o frame mais recente disponível.
# ============================================================

import cv2       # Biblioteca de visão computacional usada no projeto inteiro
import config    # Nosso arquivo central de configurações


def abrir_webcam():
    """
    Abre a conexão com a webcam do notebook e devolve o objeto
    de captura já configurado com a resolução desejada.

    cv2.CAP_DSHOW é um "backend" (motor interno) específico do
    Windows. Ele evita travamentos comuns ao abrir a câmera
    nesse sistema operacional. Em Linux ou macOS esse parâmetro
    simplesmente é ignorado, sem causar erro.

    Retorna:
        cap (cv2.VideoCapture): objeto que representa a câmera aberta.
    """
    # Cria a conexão com a câmera usando o índice definido em config.py
    cap = cv2.VideoCapture(config.WEBCAM_INDEX, cv2.CAP_DSHOW)

    # Pedimos à câmera para usar a resolução configurada.
    # Isso é apenas um "pedido": algumas câmeras ignoram e usam
    # a resolução padrão delas.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.WEBCAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.WEBCAM_HEIGHT)

    return cap


def camera_esta_aberta(cap):
    """
    Verifica se a webcam foi aberta com sucesso.

    Parâmetros:
        cap (cv2.VideoCapture): objeto retornado por abrir_webcam()

    Retorna:
        bool: True se a câmera está pronta para uso, False caso contrário.
    """
    # cap.isOpened() é um método pronto do OpenCV que responde
    # exatamente essa pergunta.
    return cap.isOpened()


def capturar_frame(cap):
    """
    Pede UM frame (uma "foto" do instante atual) para a webcam
    já aberta.

    Parâmetros:
        cap (cv2.VideoCapture): objeto retornado por abrir_webcam()

    Retorna:
        sucesso (bool): True se a captura funcionou, False se falhou.
        frame (numpy.ndarray ou None): a imagem capturada, no
            formato BGR (Azul-Verde-Vermelho), que é o padrão
            usado internamente pelo OpenCV.
    """
    sucesso, frame = cap.read()
    return sucesso, frame


def fechar_webcam(cap):
    """
    Libera a webcam para que ela possa ser usada por outros
    programas depois. É uma boa prática sempre "desligar" o
    que foi "ligado".

    Parâmetros:
        cap (cv2.VideoCapture): objeto retornado por abrir_webcam()
    """
    cap.release()
