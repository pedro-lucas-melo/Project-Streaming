# 🎬 Project-Streaming

Servidor de streaming de vídeo local, leve e assíncrono, construído com **Python** e **aiohttp**.
Serve arquivos MP4/MKV com suporte completo a HTTP Range Requests — seek, pausa e retomada no player.
Inclui app instalável para **Samsung Smart TV (Tizen)**.

---

## ✨ Funcionalidades

- ⚡ Streaming assíncrono com suporte a **Range Requests** (seek sem rebuffering)
- 👤 **Múltiplos perfis** — cada usuário tem seu histórico e watchlist independente
- 📺 **Continue assistindo** — retoma de onde parou, com barra de progresso
- 🎥 **Biblioteca de séries** com navegação por série → temporada → episódio
- 🎞️ **Biblioteca de filmes** com rota dedicada
- 🖼️ **Integração TMDB** — pôsteres e metadados automáticos para séries e filmes
- 📋 **Watchlist** — salve títulos para assistir depois
- 💡 **Sugestões via Telegram** — envie sugestões de filmes/séries para um bot Telegram
- 🖥️ Interface web com templates **Jinja2** (dark mode)
- ▶️ Player HTML5 com controles customizados (seek ±10s, teclas de atalho)
- 📱 **App Tizen** — instalável em Samsung Smart TV sem loja de apps

---

## 🛠 Tecnologias

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12+ | Backend |
| aiohttp | 3.9+ | Servidor web assíncrono |
| aiohttp-jinja2 | 1.6+ | Templates |
| Jinja2 | 3.1+ | Renderização HTML |
| aiosqlite | 0.22+ | Banco de dados (perfis, progresso, watchlist) |
| python-dotenv | 1.0+ | Configuração por `.env` |
| ffmpeg | — | Conversão de mídia (script separado) |

---

## 📁 Estrutura

```
streaming-server/
├── src/streaming/
│   ├── server.py        # Servidor principal, rotas
│   ├── media.py         # Biblioteca de mídia (scan de diretórios)
│   ├── database.py      # SQLite: perfis, progresso, watchlist
│   ├── tmdb.py          # Integração com a API do TMDB
│   └── config.py        # Configurações via .env
├── templates/
│   ├── profiles.html    # Seleção de perfil
│   ├── home.html        # Página inicial (continue assistindo + watchlist)
│   ├── index.html       # Lista de séries
│   ├── series.html      # Temporadas de uma série
│   ├── season.html      # Episódios de uma temporada
│   ├── movies.html      # Lista de filmes
│   └── player.html      # Player de vídeo
├── StreamingTV/         # App Tizen para Samsung Smart TV
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

# Token de leitura da API do TMDB (para pôsteres e metadados)
# Crie em: https://www.themoviedb.org/settings/api
TMDB_API_READ_TOKEN=

# Bot do Telegram para receber sugestões de filmes/séries (opcional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
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
    └── Interstellar.mp4
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

## 👤 Perfis

Na primeira tela, selecione um perfil. Cada perfil tem:
- Histórico de progresso independente (retoma de onde parou)
- Watchlist própria
- O banco de dados (`streaming.db`) é criado automaticamente na primeira execução

Para adicionar ou remover perfis, edite diretamente a tabela `profiles` em `streaming.db` ou modifique `_SEED` em `database.py`.

---

## 📺 App Samsung Smart TV (Tizen)

O diretório `StreamingTV/` contém um app web instalável em TVs Samsung (Tizen OS, modelos 2017+) **sem precisar da loja de apps**.

Veja as instruções completas em [StreamingTV/README.md](StreamingTV/README.md).

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
