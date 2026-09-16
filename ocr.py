# ============================================================
# ocr.py
# ============================================================

import config

class OCREngine:
    def __init__(self):
        self._motor = None
        self.engine_name = None

    def load(self):
        # --- Tentativa 1: EasyOCR (Prioridade para Português) ---
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

        # --- Tentativa 2: RapidOCR (Fallback) ---
        try:
            from rapidocr_onnxruntime import RapidOCR
            self._motor = RapidOCR()
            self.engine_name = "RapidOCR"
            return
        except ImportError:
            pass

        raise RuntimeError(
            "Nenhum motor de OCR foi encontrado. Instale o EasyOCR com:\n"
            "  pip install easyocr"
        )

    def recognize(self, imagem, confidence_threshold=None):
        if self._motor is None:
            raise RuntimeError("Chame engine.load() antes de engine.recognize().")

        if confidence_threshold is None:
            confidence_threshold = config.DEFAULT_CONFIDENCE

        if self.engine_name == "RapidOCR":
            palavras_brutas = self._reconhecer_com_rapidocr(imagem)
        else:
            palavras_brutas = self._reconhecer_com_easyocr(imagem)

        palavras_filtradas = [
            palavra for palavra in palavras_brutas
            if palavra["confidence"] >= confidence_threshold
        ]

        return palavras_filtradas

    def _reconhecer_com_rapidocr(self, imagem):
        resultado, _tempo_gasto = self._motor(imagem)
        palavras = []
        if resultado is None:
            return palavras
        for caixa, texto, confianca in resultado:
            palavras.append(self._montar_palavra(caixa, texto, confianca))
        return palavras

    def _reconhecer_com_easyocr(self, imagem):
        resultado = self._motor.readtext(imagem)
        palavras = []
        for caixa, texto, confianca in resultado:
            palavras.append(self._montar_palavra(caixa, texto, confianca))
        return palavras

    def _montar_palavra(self, caixa, texto, confianca):
        xs = [ponto[0] for ponto in caixa]
        ys = [ponto[1] for ponto in caixa]
        return {
            "text": texto,
            "confidence": float(confianca),
            "box": caixa,
            "cx": sum(xs) / len(xs),
            "cy": sum(ys) / len(ys),
        }

def build_sentence(palavras):
    if not palavras:
        return ""

    palavras_ordenadas = sorted(palavras, key=lambda p: p["cy"])
    
    alturas = []
    for palavra in palavras_ordenadas:
        ys = [ponto[1] for ponto in palavra["box"]]
        alturas.append(max(ys) - min(ys))
    altura_media = sum(alturas) / len(alturas) if alturas else 20

    limite_linha = altura_media * config.ROW_HEIGHT_FACTOR

    linhas = []
    linha_atual = [palavras_ordenadas[0]]
    y_referencia = palavras_ordenadas[0]["cy"]

    for palavra in palavras_ordenadas[1:]:
        if abs(palavra["cy"] - y_referencia) <= limite_linha:
            linha_atual.append(palavra)
        else:
            linhas.append(linha_atual)
            linha_atual = [palavra]
            y_referencia = palavra["cy"]
    linhas.append(linha_atual)

    texto_final_linhas = []
    for linha in linhas:
        linha_ordenada = sorted(linha, key=lambda p: p["cx"])
        textos_da_linha = [palavra["text"] for palavra in linha_ordenada]
        texto_final_linhas.append(" ".join(textos_da_linha))

    return "\n".join(texto_final_linhas)