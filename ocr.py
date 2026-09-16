# ============================================================
# ocr.py
# ============================================================
# Este arquivo contém tudo relacionado ao "cérebro" do projeto:
# o motor de OCR (Optical Character Recognition), que é o
# modelo de Inteligência Artificial responsável por OLHAR para
# a imagem e dizer QUAIS letras/números/palavras existem nela.
#
# CONCEITO SIMPLES:
# O OCR funciona em duas partes internas:
#   - DETECÇÃO: encontra ONDE estão os textos na imagem
#     (desenha uma "caixa" ao redor de cada palavra).
#   - RECONHECIMENTO: identifica QUAIS caracteres formam
#     aquele texto dentro de cada caixa.
#
# Usamos a biblioteca RapidOCR como opção principal (é leve e
# roda bem em CPU). Se ela não estiver instalada, o código
# tenta automaticamente usar o EasyOCR como alternativa
# ("fallback"). Assim, o projeto funciona mesmo que você tenha
# instalado apenas uma das duas bibliotecas.
# ============================================================

import config   # Nosso arquivo de configurações


class OCREngine:
    """
    Esta classe representa o "motor de OCR" do projeto.

    Uma CLASSE, em Python, é como uma "receita" para criar um
    objeto que guarda dados (o modelo de IA carregado) e sabe
    executar ações (reconhecer texto). Usamos uma classe aqui
    porque carregar o modelo de IA é uma operação "pesada" que
    queremos fazer APENAS UMA VEZ (não a cada frame capturado).
    """

    def __init__(self):
        # Guardamos aqui o "motor" de fato (RapidOCR ou EasyOCR)
        self._motor = None

        # Guardamos qual biblioteca foi carregada, só para
        # mostrarmos essa informação na interface (curiosidade)
        self.engine_name = None

    def load(self):
        """
        Carrega o modelo de OCR na memória.

        Tentamos primeiro o RapidOCR (mais leve e rápido em
        CPU). Se ele não estiver instalado, tentamos o EasyOCR.
        Se nenhum dos dois estiver disponível, avisamos o
        usuário com uma mensagem de erro clara.
        """
        # --- Tentativa 1: RapidOCR ---
        try:
            from rapidocr_onnxruntime import RapidOCR

            self._motor = RapidOCR()
            self.engine_name = "RapidOCR"
            return
        except ImportError:
            # A biblioteca não está instalada — seguimos para
            # a próxima tentativa, sem quebrar o programa.
            pass

        # --- Tentativa 2: EasyOCR ---
        try:
            import easyocr

            self._motor = easyocr.Reader(
                config.LANGUAGES,
                gpu=config.USE_GPU,
            )
            self.engine_name = "EasyOCR"
            return
        except ImportError:
            pass

        # Se chegamos até aqui, nenhuma biblioteca de OCR foi
        # encontrada. Avisamos o usuário com uma mensagem clara.
        raise RuntimeError(
            "Nenhum motor de OCR foi encontrado. Instale uma das "
            "opções com:\n"
            "  pip install rapidocr-onnxruntime\n"
            "ou\n"
            "  pip install easyocr"
        )

    def recognize(self, imagem, confidence_threshold=None):
        """
        Executa o reconhecimento de texto em uma imagem.

        Parâmetros:
            imagem (numpy.ndarray): imagem (colorida ou em
                escala de cinza) na qual queremos encontrar texto.
            confidence_threshold (float ou None): confiança
                mínima (0 a 1) para aceitar uma palavra. Se None,
                usamos o valor padrão definido em config.py.

        Retorna:
            list[dict]: uma lista de "palavras encontradas".
                Cada palavra é um dicionário com as chaves:
                    "text"       -> o texto reconhecido (str)
                    "confidence" -> a confiança do modelo (0 a 1)
                    "box"        -> os 4 cantos (x, y) da caixa
                                     delimitadora da palavra
                    "cx", "cy"   -> o centro (x, y) da caixa,
                                     usado depois para ordenar
                                     as palavras na leitura
        """
        if self._motor is None:
            raise RuntimeError(
                "O motor de OCR ainda não foi carregado. "
                "Chame engine.load() antes de engine.recognize()."
            )

        if confidence_threshold is None:
            confidence_threshold = config.DEFAULT_CONFIDENCE

        # Cada motor (RapidOCR / EasyOCR) tem um formato de
        # resposta ligeiramente diferente. As funções abaixo
        # "traduzem" cada formato para o nosso padrão comum.
        if self.engine_name == "RapidOCR":
            palavras_brutas = self._reconhecer_com_rapidocr(imagem)
        else:
            palavras_brutas = self._reconhecer_com_easyocr(imagem)

        # Filtramos apenas as palavras com confiança suficiente
        palavras_filtradas = [
            palavra
            for palavra in palavras_brutas
            if palavra["confidence"] >= confidence_threshold
        ]

        return palavras_filtradas

    def _reconhecer_com_rapidocr(self, imagem):
        """
        Executa o RapidOCR e converte o resultado para o nosso
        formato padrão. (Função "privada": só é usada aqui dentro).
        """
        # O RapidOCR retorna uma tupla: (resultado, tempo_gasto)
        resultado, _tempo_gasto = self._motor(imagem)

        palavras = []

        # Se não encontrou nada, resultado pode vir como None
        if resultado is None:
            return palavras

        # Cada item de "resultado" é: [caixa, texto, confianca]
        for caixa, texto, confianca in resultado:
            palavras.append(self._montar_palavra(caixa, texto, confianca))

        return palavras

    def _reconhecer_com_easyocr(self, imagem):
        """
        Executa o EasyOCR e converte o resultado para o nosso
        formato padrão.
        """
        # readtext devolve uma lista de tuplas: (caixa, texto, confianca)
        resultado = self._motor.readtext(imagem)

        palavras = []
        for caixa, texto, confianca in resultado:
            palavras.append(self._montar_palavra(caixa, texto, confianca))

        return palavras

    def _montar_palavra(self, caixa, texto, confianca):
        """
        Monta o dicionário padrão de uma palavra reconhecida,
        já calculando o centro (cx, cy) da caixa delimitadora.

        "caixa" é uma lista de 4 pontos [x, y], representando
        os 4 cantos do retângulo (ou polígono) ao redor da palavra.
        """
        xs = [ponto[0] for ponto in caixa]
        ys = [ponto[1] for ponto in caixa]

        centro_x = sum(xs) / len(xs)
        centro_y = sum(ys) / len(ys)

        return {
            "text": texto,
            "confidence": float(confianca),
            "box": caixa,
            "cx": centro_x,
            "cy": centro_y,
        }


def build_sentence(palavras):
    """
    Organiza uma lista de palavras reconhecidas (fora de ordem)
    em um texto legível, respeitando a ordem natural de leitura:
    de cima para baixo, e da esquerda para a direita dentro de
    cada linha.

    Como funciona (em linguagem simples)?
    1. Ordenamos todas as palavras pela posição vertical (Y).
    2. Agrupamos em "linhas" as palavras cujo centro Y está
       próximo (dentro de uma faixa de tolerância).
    3. Dentro de cada linha, ordenamos as palavras da esquerda
       para a direita (posição X).
    4. Juntamos tudo em um texto final, com quebras de linha
       entre os grupos.

    Parâmetros:
        palavras (list[dict]): lista no formato retornado por
            OCREngine.recognize().

    Retorna:
        str: o texto final, organizado como um parágrafo legível.
    """
    if not palavras:
        return ""

    # Passo 1: ordenar todas as palavras pela posição vertical (cy)
    palavras_ordenadas = sorted(palavras, key=lambda p: p["cy"])

    # Calculamos uma altura média aproximada das caixas, para
    # decidir o quão "perto" duas palavras precisam estar
    # verticalmente para serem consideradas da mesma linha.
    alturas = []
    for palavra in palavras_ordenadas:
        ys = [ponto[1] for ponto in palavra["box"]]
        alturas.append(max(ys) - min(ys))
    altura_media = sum(alturas) / len(alturas) if alturas else 20

    limite_linha = altura_media * config.ROW_HEIGHT_FACTOR

    # Passo 2: agrupar as palavras em linhas
    linhas = []          # lista de linhas; cada linha é uma lista de palavras
    linha_atual = [palavras_ordenadas[0]]
    y_referencia = palavras_ordenadas[0]["cy"]

    for palavra in palavras_ordenadas[1:]:
        if abs(palavra["cy"] - y_referencia) <= limite_linha:
            # Está perto o suficiente: pertence à mesma linha
            linha_atual.append(palavra)
        else:
            # Está longe: fechamos a linha atual e começamos uma nova
            linhas.append(linha_atual)
            linha_atual = [palavra]
            y_referencia = palavra["cy"]

    # Não esquecer de guardar a última linha em construção
    linhas.append(linha_atual)

    # Passo 3 e 4: ordenar cada linha da esquerda para a direita
    # e juntar tudo em um texto final
    texto_final_linhas = []
    for linha in linhas:
        linha_ordenada = sorted(linha, key=lambda p: p["cx"])
        textos_da_linha = [palavra["text"] for palavra in linha_ordenada]
        texto_final_linhas.append(" ".join(textos_da_linha))

    return "\n".join(texto_final_linhas)
