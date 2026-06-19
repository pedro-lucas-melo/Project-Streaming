# 🎬 Project-Streaming

Servidor de streaming de vídeo local, leve e assíncrono, construído com **Python** e **aiohttp**.
Serve arquivos MP4/MKV com suporte completo a HTTP Range Requests — permitindo seek, pausa e retomada no player.

---

## ✨ Funcionalidades

- ⚡ Streaming assíncrono com suporte a **Range Requests** (seek sem rebuffering)
- 🎥 **Biblioteca de séries** com navegação por série → temporada → episódio
- 🎞️ **Biblioteca de filmes** com rota dedicada
- 🖥️ Interface web com templates **Jinja2** (dark mode)
- ▶️ Player HTML5 com controles customizados (seek ±10s, teclas de atalho)
- 🏠 Página inicial com navegação entre seções

---

## 🛠 Tecnologias

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12+ | Backend |
| aiohttp | 3.9+ | Servidor web assíncrono |
| aiohttp-jinja2 | 1.6+ | Templates |
| Jinja2 | 3.1+ | Renderização HTML |
| python-dotenv | 1.0+ | Configuração por `.env` |
| ffmpeg | — | Conversão de mídia (script separado) |

---

## 📁 Estrutura

```
streaming-server/
├── src/streaming/
│   ├── server.py        # Servidor principal, rotas
│   ├── media.py         # Biblioteca de mídia (scan de diretórios)
│   └── config.py        # Configurações via .env
├── templates/
│   ├── home.html        # Página inicial
│   ├── index.html       # Lista de séries
│   ├── series.html      # Temporadas de uma série
│   ├── season.html      # Episódios de uma temporada
│   ├── movies.html      # Lista de filmes
│   └── player.html      # Player de vídeo
├── scripts/
│   └── convert.py       # Conversor ffmpeg interativo
├── tests/
│   └── test_media.py
├── pyproject.toml
└── .env.example
```

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.12 ou superior
- [Poetry](https://python-poetry.org/docs/#installation)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/pedro-lucas-melo/Project-Streaming.git
cd Project-Streaming/streaming-server

# 2. Instale as dependências com Poetry
poetry install

# 3. Configure o .env
cp .env.example .env
# Edite o .env com seus caminhos de mídia
```

---

## ⚙️ Configuração (`.env`)

```env
# Diretório de séries (estrutura: Serie/Temporada/episodio.mp4)
MEDIA_SERIES_DIR=C:\Users\SeuUsuario\Videos\series

# Diretório de filmes (estrutura: filme.mp4)
MEDIA_MOVIES_DIR=C:\Users\SeuUsuario\Videos\filmes

# Host e porta (padrão: acessível em toda a rede local)
HOST=0.0.0.0
PORT=8080
```

### Estrutura de diretórios esperada

```
Videos/
├── series/
│   ├── Mr Robot/
│   │   ├── Temporada 1/
│   │   │   ├── ep01.mp4
│   │   │   └── ep02.mp4
│   │   └── Temporada 2/
│   └── Breaking Bad/
│       └── Temporada 1/
└── filmes/
    ├── Inception.mp4
    └── Interestellar.mp4
```

---

## ▶️ Executar

```bash
# Via Poetry (recomendado)
poetry run streaming

# Ou diretamente
poetry run python -m streaming.server
```

Acesse em: **http://localhost:8080**

Na rede local (TV, celular): **http://[SEU-IP]:8080**

---

## 🔄 Converter vídeos com ffmpeg

O script `scripts/convert.py` converte MKV e outros formatos para MP4 com `+faststart`
(necessário para streaming eficiente):

```bash
poetry run python scripts/convert.py
```

Menu interativo: escolha séries ou filmes, selecione quais converter.

---

## ⌨️ Atalhos do player

| Tecla | Ação |
|---|---|
| `Espaço` / `K` | Play / Pause |
| `←` | Retroceder 10s |
| `→` | Avançar 10s |
| `F` | Tela cheia |
| `M` | Mudo |
| `Backspace` / `Esc` | Voltar |

---

## 🧪 Testes

```bash
poetry run pytest tests/
```

---

## 📝 Licença

MIT — veja [LICENSE](LICENSE)
