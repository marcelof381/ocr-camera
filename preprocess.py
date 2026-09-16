# ============================================================
# preprocess.py
# ============================================================
# Este arquivo contém as funções de PRÉ-PROCESSAMENTO da
# imagem: um conjunto de "ajustes" feitos ANTES de enviar a
# imagem para o OCR, para facilitar o trabalho do algoritmo
# de reconhecimento.
#
# CONCEITO SIMPLES:
# Imagine que você vai fotografar um texto com o celular. Se a
# foto estiver escura, tremida ou com sombra, fica mais difícil
# até para uma PESSOA ler. O pré-processamento faz exatamente o
# que você faria manualmente no Photoshop: melhora contraste,
# remove "sujeira" (ruído) e endireita o texto torto — só que
# tudo de forma automática, usando matemática e OpenCV.
#
# As etapas implementadas aqui são:
#   1. Escala de cinza (grayscale)
#   2. CLAHE (melhora de contraste local)
#   3. Remoção de ruído (denoise)
#   4. Correção de inclinação (deskew)
# ============================================================

import cv2               # Biblioteca de visão computacional
import numpy as np       # Biblioteca para trabalhar com números e matrizes (a imagem é uma matriz de pixels)
import config             # Nosso arquivo de configurações


def converter_para_cinza(imagem_bgr):
    """
    Converte uma imagem colorida (BGR) para tons de cinza.

    Por que fazer isso?
    O OCR não precisa da informação de COR para identificar
    letras — ele precisa identificar FORMAS. Trabalhar em
    escala de cinza reduz a quantidade de dados (de 3 canais
    de cor para apenas 1) e deixa o processamento mais rápido
    e, geralmente, mais preciso.

    Parâmetros:
        imagem_bgr (numpy.ndarray): imagem colorida no formato
            BGR (padrão do OpenCV, ou seja, Azul-Verde-Vermelho,
            NÃO é RGB!).

    Retorna:
        numpy.ndarray: imagem em escala de cinza (1 único canal).
    """
    # cv2.COLOR_BGR2GRAY é a "receita" pronta do OpenCV que faz
    # essa conversão de cores para tons de cinza.
    imagem_cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
    return imagem_cinza


def aplicar_clahe(imagem_cinza):
    """
    Aplica o CLAHE (Equalização Adaptativa de Histograma) para
    melhorar o CONTRASTE LOCAL da imagem.

    Por que fazer isso?
    Se parte da imagem está com sombra e outra parte com luz
    forte, uma equalização "global" (a imagem toda de uma vez)
    pode deixar áreas já claras "estouradas" de branco. O CLAHE
    resolve isso melhorando o contraste REGIÃO POR REGIÃO,
    preservando os detalhes em toda a imagem.

    Parâmetros:
        imagem_cinza (numpy.ndarray): imagem em escala de cinza.

    Retorna:
        numpy.ndarray: imagem com contraste melhorado.
    """
    # Criamos o "objeto CLAHE" com os parâmetros definidos em config.py
    clahe = cv2.createCLAHE(
        clipLimit=config.CLAHE_CLIP_LIMIT,
        tileGridSize=config.CLAHE_TILE_GRID_SIZE,
    )

    # .apply() executa de fato o ajuste de contraste na imagem
    imagem_com_clahe = clahe.apply(imagem_cinza)
    return imagem_com_clahe


def remover_ruido(imagem_cinza):
    """
    Remove ruído (pequenas manchas, granulado, "sujeira" digital)
    da imagem, deixando-a mais "limpa" para o OCR.

    Por que fazer isso?
    Câmeras de notebook, principalmente em ambientes com pouca
    luz, geram ruído — pequenas variações aleatórias de brilho
    em cada pixel. Esse ruído pode ser confundido pelo OCR com
    partes de letras, atrapalhando o reconhecimento.

    Parâmetros:
        imagem_cinza (numpy.ndarray): imagem em escala de cinza
            (idealmente já com CLAHE aplicado).

    Retorna:
        numpy.ndarray: imagem com ruído reduzido.
    """
    # fastNlMeansDenoising é um algoritmo do OpenCV especializado
    # em remover ruído mantendo bordas e detalhes importantes.
    # "h" controla a intensidade do efeito (config.DENOISE_STRENGTH).
    imagem_sem_ruido = cv2.fastNlMeansDenoising(
        imagem_cinza,
        None,
        h=config.DENOISE_STRENGTH,
    )
    return imagem_sem_ruido


def corrigir_inclinacao(imagem_cinza):
    """
    Detecta se o texto na imagem está "torto" (inclinado) e,
    se estiver, rotaciona a imagem para deixá-lo na horizontal.
    Essa técnica é chamada de "deskew".

    Por que fazer isso?
    Se você fotografar uma folha de papel um pouco torta, o
    texto também sai torto. Um OCR lê muito melhor um texto
    alinhado horizontalmente do que um texto inclinado.

    Como funciona (em linguagem simples)?
    1. Encontramos todos os pixels "escuros" (que provavelmente
       são texto) na imagem.
    2. Calculamos o menor retângulo que envolve esses pixels
       (mesmo que ele esteja rotacionado) usando minAreaRect.
    3. O ângulo desse retângulo nos diz o quanto o texto está
       inclinado.
    4. Rotacionamos a imagem inteira nesse ângulo, na direção
       contrária, para "endireitar" o texto.

    Parâmetros:
        imagem_cinza (numpy.ndarray): imagem em escala de cinza.

    Retorna:
        numpy.ndarray: imagem corrigida (ou a mesma imagem, se
            a inclinação já era pequena o suficiente).
    """
    # np.where(imagem_cinza < 200) encontra as posições (linha, coluna)
    # de todos os pixels "escuros" (valor menor que 200), que
    # tendem a ser o texto sobre um fundo mais claro.
    coordenadas = np.column_stack(np.where(imagem_cinza < 200))

    # Se não encontramos pixels escuros suficientes, não há o
    # que corrigir — devolvemos a imagem original sem mexer.
    if coordenadas.shape[0] < 10:
        return imagem_cinza

    # minAreaRect calcula o menor retângulo (podendo estar
    # rotacionado) que envolve todos esses pontos. O último
    # valor retornado ([-1]) é o ângulo de rotação desse retângulo.
    angulo = cv2.minAreaRect(coordenadas)[-1]

    # O ângulo retornado pelo OpenCV pode vir em uma escala um
    # pouco confusa (de -90 a 0 graus). Este ajuste converte
    # para um ângulo mais intuitivo de correção.
    if angulo < -45:
        angulo = -(90 + angulo)
    else:
        angulo = -angulo

    # Se a inclinação for muito pequena, não vale a pena rotacionar
    # (evita "mexer" na imagem à toa e perder qualidade).
    if abs(angulo) < config.DESKEW_MIN_ANGLE:
        return imagem_cinza

    # Pegamos a altura (h) e largura (w) da imagem para calcular
    # o centro, que será o "eixo" da rotação.
    altura, largura = imagem_cinza.shape[:2]
    centro = (largura // 2, altura // 2)

    # getRotationMatrix2D cria a "matriz de rotação": uma receita
    # matemática que descreve como girar a imagem em torno do centro.
    matriz_rotacao = cv2.getRotationMatrix2D(centro, angulo, 1.0)

    # warpAffine aplica de fato a rotação na imagem, usando a
    # matriz calculada acima.
    imagem_corrigida = cv2.warpAffine(
        imagem_cinza,
        matriz_rotacao,
        (largura, altura),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )

    return imagem_corrigida


def pre_processar_imagem(imagem_bgr, aplicar_deskew=True):
    """
    Função "principal" deste arquivo: executa TODO o pipeline
    de pré-processamento, na ordem correta, e devolve a imagem
    pronta para ser lida pelo OCR.

    Ordem das etapas (importante!):
        1. Escala de cinza     -> reduz para 1 canal de cor
        2. CLAHE                -> melhora contraste local
        3. Remoção de ruído     -> "limpa" a imagem
        4. Correção de inclinação (opcional) -> endireita o texto

    Parâmetros:
        imagem_bgr (numpy.ndarray): imagem original capturada
            da webcam, no formato BGR.
        aplicar_deskew (bool): se True, tenta corrigir a
            inclinação do texto. Pode ser desativado se você
            sabe que a imagem já está bem alinhada.

    Retorna:
        numpy.ndarray: imagem pré-processada, pronta para o OCR.
    """
    # Etapa 1: escala de cinza
    imagem = converter_para_cinza(imagem_bgr)

    # Etapa 2: CLAHE (melhora contraste local)
    imagem = aplicar_clahe(imagem)

    # Etapa 3: remoção de ruído
    imagem = remover_ruido(imagem)

    # Etapa 4 (opcional): correção de inclinação
    if aplicar_deskew:
        imagem = corrigir_inclinacao(imagem)

    return imagem
