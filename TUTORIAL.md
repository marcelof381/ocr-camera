# Tutorial — OCR com Webcam (do zero, sem saber programar)

Este guia foi escrito para quem **nunca programou em Python**. Siga os
passos na ordem, um de cada vez. Sempre que aparecer um bloco cinza com
texto, é um **comando** que você deve copiar e colar no terminal
(Prompt de Comando / PowerShell no Windows).

---

## 1. O que você vai instalar

| Ferramenta | Para que serve |
|---|---|
| Python | A "linguagem" em que o projeto foi escrito |
| Ambiente virtual (venv) | Uma "caixa isolada" para instalar as bibliotecas do projeto, sem bagunçar o resto do seu computador |
| Bibliotecas (opencv, streamlit, rapidocr) | "Ferramentas prontas" que o código usa por baixo dos panos |

---

## 2. Instalando o Python

1. Acesse **https://www.python.org/downloads/**
2. Baixe a versão mais recente (3.10, 3.11 ou 3.12 funcionam bem).
3. Ao instalar no **Windows**, marque a caixinha **"Add Python to PATH"**
   antes de clicar em "Install Now". Isso é essencial — sem ela, os
   comandos abaixo não vão funcionar.
4. Para confirmar que deu certo, abra o **Prompt de Comando** (procure
   por "cmd" no menu iniciar) e digite:

   ```
   python --version
   ```

   Se aparecer algo como `Python 3.11.5`, deu certo!

---

## 3. Organizando a pasta do projeto

1. Crie uma pasta em qualquer lugar do seu computador, por exemplo:
   `C:\Users\SeuNome\Documents\ocr_webcam`
2. Coloque dentro dela os arquivos deste projeto:
   - `config.py`
   - `camera.py`
   - `preprocess.py`
   - `ocr.py`
   - `app.py`
   - `requirements.txt`
3. Abra o **Prompt de Comando** e navegue até essa pasta com o comando
   `cd` (change directory). Exemplo:

   ```
   cd C:\Users\SeuNome\Documents\ocr_webcam
   ```

---

## 4. Criando o Ambiente Virtual (venv)

Um **ambiente virtual** é como uma "caixa separada" só para este
projeto. Assim, as bibliotecas que vamos instalar não interferem em
outros programas Python do seu computador.

1. Dentro da pasta do projeto, digite:

   ```
   python -m venv venv
   ```

   Isso cria uma pastinha chamada `venv` dentro do seu projeto.

2. Agora você precisa **ativar** essa caixa. O comando muda dependendo
   do seu sistema operacional:

   **Windows (Prompt de Comando):**
   ```
   venv\Scripts\activate
   ```

   **Windows (PowerShell):**
   ```
   venv\Scripts\Activate.ps1
   ```

   **Linux / macOS:**
   ```
   source venv/bin/activate
   ```

3. Se der certo, você verá `(venv)` aparecer no início da linha do
   terminal. Isso indica que o ambiente virtual está ativo.

   > ⚠️ Toda vez que você fechar o terminal e quiser rodar o projeto
   > de novo, será necessário repetir o passo 2 (ativar o `venv`).

---

## 5. Instalando as bibliotecas do projeto

Com o `(venv)` ativo, digite:

```
pip install -r requirements.txt
```

Isso vai baixar e instalar automaticamente:
- `opencv-python` (visão computacional)
- `numpy` (matemática/matrizes)
- `streamlit` (interface gráfica)
- `rapidocr-onnxruntime` (motor de OCR)

Esse processo pode demorar alguns minutos, dependendo da sua internet.

> 💡 Se o `rapidocr-onnxruntime` der algum erro na instalação, abra o
> arquivo `requirements.txt`, remova o `#` da linha `# easyocr` e rode
> o comando `pip install -r requirements.txt` novamente. O código do
> projeto já sabe usar o EasyOCR automaticamente como alternativa.

---

## 6. Rodando a aplicação

Ainda no terminal, com o `(venv)` ativo e dentro da pasta do projeto,
digite:

```
streamlit run app.py
```

Depois de alguns segundos, uma aba do seu navegador deve abrir
sozinha, mostrando a interface do projeto. Se isso não acontecer, o
terminal vai mostrar um endereço parecido com:

```
Local URL: http://localhost:8501
```

Copie esse endereço e cole na barra do seu navegador.

---

## 7. Usando a interface

1. Na barra lateral esquerda, clique em **"📷 Ligar webcam"**.
   (O Windows pode pedir permissão para o programa usar a câmera —
   aceite.)
2. Aponte a webcam para o texto que você quer reconhecer (um livro,
   uma etiqueta, um cartaz...).
3. Clique no botão **"📸 Capturar frame e reconhecer texto"**.
4. Aguarde alguns segundos — o modelo de IA está analisando a imagem.
5. O resultado aparece:
   - As duas imagens lado a lado (original com caixas verdes, e a
     versão pré-processada em tons de cinza).
   - O texto reconhecido, em uma caixa de texto.
6. Use o **slider "Confiança mínima do OCR"**, na barra lateral, para
   ajustar o quão "rigoroso" o reconhecimento deve ser. Valores mais
   baixos aceitam mais palavras (inclusive algumas erradas); valores
   mais altos são mais seletivos.
7. Clique em **"⬇️ Baixar texto reconhecido (.txt)"** para salvar o
   resultado em um arquivo no seu computador.
8. Ao terminar, clique em **"⏹️ Desligar webcam"** na barra lateral.

---

## 8. Entendendo o pipeline (o "caminho" da imagem)

```
Webcam  →  Captura  →  Pré-processamento  →  OCR (IA)  →  Interface
```

| Etapa | O que acontece | Onde está no código |
|---|---|---|
| **1. Captura da Webcam** | O OpenCV pede um "frame" (uma foto) para a câmera do notebook | `camera.py` |
| **2. Pré-processamento** | A imagem é convertida para tons de cinza, tem o contraste melhorado (CLAHE), o ruído removido, e a inclinação corrigida (deskew) | `preprocess.py` |
| **3. Reconhecimento (OCR / IA)** | Um modelo de rede neural encontra ONDE está o texto e QUAIS caracteres formam cada palavra | `ocr.py` |
| **4. Exibição / Monitor Serial** | O texto aparece na tela (Streamlit) e também é impresso no terminal, como um "Monitor Serial" | `app.py` |

### Por que pré-processar a imagem antes do OCR?

Pense em ler um texto com os próprios olhos: se a foto estiver escura,
tremida ou fora de foco, você também tem dificuldade. O
pré-processamento faz exatamente esse "ajuste" — só que
automaticamente, usando matemática — para deixar o trabalho do modelo
de IA mais fácil e o resultado mais preciso.

### Por que existe um "limiar de confiança"?

Todo resultado do OCR vem acompanhado de uma "nota" de 0 a 1, dizendo
o quão confiante o modelo está de que aquele texto foi lido
corretamente. Se aceitássemos TODAS as palavras, mesmo as de baixa
confiança, o texto final ficaria cheio de erros. O slider de confiança
permite que você escolha o equilíbrio entre "aceitar mais palavras" e
"aceitar só as mais certas".

---

## 9. Problemas comuns (e como resolver)

| Problema | Possível causa | Solução |
|---|---|---|
| `python` não é reconhecido como comando | Python não foi adicionado ao PATH | Reinstale o Python marcando "Add Python to PATH" |
| A webcam não abre | Outro programa (Zoom, Teams, câmera do Windows) está usando a câmera | Feche esses programas e tente novamente |
| Erro ao instalar `rapidocr-onnxruntime` | Alguma incompatibilidade de versão do Python | Ative o EasyOCR no `requirements.txt` (veja passo 5) |
| A imagem fica muito escura ou clara | Iluminação ruim no ambiente | Aproxime uma fonte de luz do texto antes de capturar |
| Nenhuma palavra é encontrada | Confiança mínima está alta demais, ou o texto está longe/desfocado | Diminua o slider de confiança e aproxime a câmera |

---

## 10. Próximos passos (opcional)

- Experimente trocar os valores em `config.py` (por exemplo,
  `CLAHE_CLIP_LIMIT`) e observe como o resultado muda.
- Tente desativar o "deskew" na barra lateral e veja a diferença ao
  fotografar um texto torto.
- Leia os comentários dentro de `preprocess.py` e `ocr.py` — cada
  função tem uma explicação detalhada do que faz e por quê.
