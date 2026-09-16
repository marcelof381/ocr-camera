# ============================================================
# config.py
# ============================================================
# Este arquivo guarda TODAS as configurações do projeto em um
# único lugar. A ideia é simples: se você quiser mudar algum
# valor (idioma do OCR, força do filtro de ruído, etc.), 
# você mexe SÓ AQUI, sem precisar entender ou alterar o resto.
# ============================================================


# ------------------------------------------------------------
# Configurações do PRÉ-PROCESSAMENTO de imagem
# ------------------------------------------------------------

# CLAHE = Contrast Limited Adaptive Histogram Equalization.
# Serve para melhorar o contraste da imagem REGIÃO POR REGIÃO,
# o que ajuda muito quando há sombra ou iluminação desigual.
# clipLimit: quanto maior, mais contraste é aplicado. 
CLAHE_CLIP_LIMIT = 2.0

# tileGridSize: o CLAHE divide a imagem em uma "grade" de
# blocos (tiles) e equaliza cada bloco separadamente.
CLAHE_TILE_GRID_SIZE = (8, 8)

# Força da remoção de ruído (fastNlMeansDenoising). Quanto
# maior o valor de "h", mais suavizada fica a imagem.
DENOISE_STRENGTH = 10

# Ângulo mínimo (em graus) para considerarmos que a imagem
# está "torta" e precisa ser corrigida (deskew).
DESKEW_MIN_ANGLE = 0.5


# ------------------------------------------------------------
# Configurações do OCR (reconhecimento de texto)
# ------------------------------------------------------------

# Idiomas que o motor de OCR deve tentar reconhecer.
# O "pt" deve vir primeiro para forçar o motor a buscar
# acentuações corretas (ex: "você", "história").
LANGUAGES = ["pt", "en"]

# Confiança mínima padrão (varia de 0 a 1) para uma palavra
# ser aceita como "válida".
DEFAULT_CONFIDENCE = 0.40

# Se True, tenta usar a GPU (placa de vídeo) para acelerar o OCR.
USE_GPU = False


# ------------------------------------------------------------
# Configurações do PÓS-PROCESSAMENTO (organização do texto)
# ------------------------------------------------------------

# Fator usado para decidir se duas palavras estão na "mesma
# linha" de texto. Multiplicamos a altura média das palavras
# por esse fator para criar uma "faixa de tolerância" vertical.
ROW_HEIGHT_FACTOR = 1.2