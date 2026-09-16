# ============================================================
# config.py
# ============================================================
# Este arquivo guarda TODAS as configurações do projeto em um
# único lugar. A ideia é simples: se você quiser mudar algum
# valor (idioma do OCR, resolução da webcam, força do filtro
# de ruído, etc.), você mexe SÓ AQUI, sem precisar entender ou
# alterar o resto do código.
#
# Cada variável abaixo tem um comentário explicando o que ela
# faz e por que o valor escolhido é razoável.
# ============================================================

# ------------------------------------------------------------
# Configurações da CÂMERA (webcam do notebook)
# ------------------------------------------------------------

# Índice da webcam. Praticamente todo notebook tem a webcam
# interna no índice 0. Se você tiver mais de uma câmera
# conectada (ex.: uma USB), pode ser necessário trocar para 1.
WEBCAM_INDEX = 0

# Resolução (largura x altura) que vamos PEDIR para a webcam.
# Nem toda câmera aceita exatamente esse valor, mas o OpenCV
# tenta chegar o mais perto possível.
WEBCAM_WIDTH = 1280
WEBCAM_HEIGHT = 720


# ------------------------------------------------------------
# Configurações do PRÉ-PROCESSAMENTO de imagem
# ------------------------------------------------------------

# CLAHE = Contrast Limited Adaptive Histogram Equalization.
# Em português: "Equalização Adaptativa de Histograma com
# Contraste Limitado". Serve para melhorar o contraste da
# imagem REGIÃO POR REGIÃO (e não a imagem toda de uma vez),
# o que ajuda muito quando há sombra ou iluminação desigual.
#
# clipLimit: quanto maior, mais contraste é aplicado (mas
# valores muito altos podem gerar ruído). 2.0 é um valor
# equilibrado e muito usado na prática.
CLAHE_CLIP_LIMIT = 2.0

# tileGridSize: o CLAHE divide a imagem em uma "grade" de
# blocos (tiles) e equaliza cada bloco separadamente.
# (8, 8) significa uma grade de 8 colunas por 8 linhas.
CLAHE_TILE_GRID_SIZE = (8, 8)

# Força da remoção de ruído (fastNlMeansDenoising). Quanto
# maior o valor de "h", mais "borrada"/suavizada fica a
# imagem (remove mais ruído, mas pode perder detalhes finos).
# h = 10 é um valor padrão recomendado pela documentação do
# OpenCV para fotos com ruído comum de câmera.
DENOISE_STRENGTH = 10

# Ângulo mínimo (em graus) para considerarmos que a imagem
# está "torta" e precisa ser corrigida (deskew). Abaixo desse
# valor, a inclinação é tão pequena que não vale a pena mexer.
DESKEW_MIN_ANGLE = 0.5


# ------------------------------------------------------------
# Configurações do OCR (reconhecimento de texto)
# ------------------------------------------------------------

# Idiomas que o motor de OCR deve tentar reconhecer.
# "pt" = português, "en" = inglês. Você pode adicionar outros
# códigos de idioma suportados pela biblioteca escolhida.
LANGUAGES = ["pt", "en"]

# Confiança mínima padrão (varia de 0 a 1) para uma palavra
# ser aceita como "válida". Esse valor aparece pré-selecionado
# no slider da interface, mas o usuário pode ajustá-lo.
DEFAULT_CONFIDENCE = 0.40

# Se True, tenta usar a GPU (placa de vídeo) para acelerar o
# OCR. Deixamos False porque nem todo notebook tem GPU
# configurada corretamente — assim o projeto funciona em
# qualquer computador, usando apenas o processador (CPU).
USE_GPU = False


# ------------------------------------------------------------
# Configurações do PÓS-PROCESSAMENTO (organização do texto)
# ------------------------------------------------------------

# Fator usado para decidir se duas palavras estão na "mesma
# linha" de texto. Multiplicamos a altura média das palavras
# por esse fator para criar uma "faixa de tolerância" vertical.
ROW_HEIGHT_FACTOR = 1.2
