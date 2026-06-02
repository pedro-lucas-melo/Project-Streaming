# 🎬 Project-Streaming

Um servidor de streaming de vídeo leve e eficiente, construído com Python e aiohttp, capaz de servir mídia com suporte a streaming por chunks (HTTP Range Requests).

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias](#tecnologias)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Testes](#testes)
- [Contribuindo](#contribuindo)

---

## Sobre o Projeto

O **Project-Streaming** é um servidor web assíncrono focado em entrega eficiente de conteúdo de vídeo. Utilizando `aiohttp` e templates `Jinja2`, o projeto oferece uma interface web simples para navegar e assistir vídeos diretamente no navegador, com suporte a seek (avanço/retrocesso) via HTTP Range Requests.

### ✨ Funcionalidades

- ⚡ Streaming assíncrono de vídeo com suporte a Range Requests
- 🎯 Controles de seek (avançar/retroceder) no player
- 🎞️ Rota dedicada para biblioteca de filmes
- 🖥️ Interface web com templates Jinja2
- 📁 Gerenciamento de biblioteca de mídia local

---

## Tecnologias

| Tecnologia | Descrição |
|---|---|
| **Python 3.10+** | Linguagem principal |
| **aiohttp** | Servidor web assíncrono |
| **Jinja2** | Engine de templates HTML |
| **pyproject.toml** | Gerenciamento de dependências |

---

## Estrutura do Projeto

```
Project-Streaming/
├── scripts/          # Scripts auxiliares (renomear arquivos de mídia, etc.)
├── src/
│   └── streaming/    # Código-fonte principal (rotas, handlers, lógica de streaming)
├── templates/        # Templates HTML (Jinja2) para a interface web
├── tests/            # Testes automatizados
├── .env.example      # Exemplo de variáveis de ambiente
├── .gitignore
├── pyproject.toml    # Configuração do projeto e dependências
└── README.md
```

---

## Pré-requisitos

- Python **3.10** ou superior
- `pip` ou gerenciador de pacotes compatível com `pyproject.toml` (ex: `uv`, `poetry`)

---

## Instalação

1. **Clone o repositório:**

```bash
git clone https://github.com/pedro-lucas-melo/Project-Streaming.git
cd Project-Streaming
```

2. **Crie e ative um ambiente virtual:**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**

```bash
pip install -e .
```

---

## Configuração

1. Copie o arquivo de exemplo de variáveis de ambiente:

```bash
cp .env.example .env
```

2. Edite o `.env` com o caminho da sua biblioteca de mídia:

```env
MEDIA_DIR=/caminho/para/seus/videos
```

---

## Como Usar

Inicie o servidor:

```bash
python -m src.streaming
```

Acesse no navegador:

```
http://localhost:8080
```

Navegue pela biblioteca de filmes em:

```
http://localhost:8080/movies
```

---

## Testes

Execute os testes com:

```bash
python -m pytest tests/
```

---

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

1. Faça um fork do projeto
2. Crie sua branch: `git checkout -b feat/minha-feature`
3. Commit suas mudanças: `git commit -m 'feat: minha nova feature'`
4. Push para a branch: `git push origin feat/minha-feature`
5. Abra um Pull Request

---

<p align="center">Feito com ☕ e Python</p>
