import os
import importlib.util

# ──────────────────────────────────────────
# Config
# ──────────────────────────────────────────

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
SERIES_DIR  = os.path.join(SCRIPTS_DIR, "scripts", "series")
MOVIES_DIR  = os.path.join(SCRIPTS_DIR, "scripts", "movies")


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def listar_opcoes(itens, titulo):
    print(f"\n{titulo}")
    for i, item in enumerate(itens, 1):
        print(f"  {i}. {item}")


def escolher_opcao(itens, titulo, permitir_todos=False):
    listar_opcoes(itens, titulo)

    if permitir_todos:
        print(f"  0. Todos")

    while True:
        entrada = input("\nEscolha: ").strip()

        if permitir_todos and entrada == "0":
            return None  # None = todos

        if entrada.isdigit():
            idx = int(entrada) - 1
            if 0 <= idx < len(itens):
                return itens[idx]

        print("  ⚠️  Opção inválida, tente novamente.")


def carregar_modulo(caminho):
    """Importa um arquivo .py como módulo e retorna suas variáveis."""
    spec   = importlib.util.spec_from_file_location("modulo_rename", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def numero_temporada(nome_script):
    """Extrai o número de 'rename_t3.py' → 3."""
    try:
        return int(nome_script.replace("rename_t", "").replace(".py", ""))
    except ValueError:
        return 0


def descobrir_series():
    if not os.path.exists(SERIES_DIR):
        return []
    return sorted([
        d for d in os.listdir(SERIES_DIR)
        if os.path.isdir(os.path.join(SERIES_DIR, d))
    ])


def descobrir_temporadas(serie):
    pasta = os.path.join(SERIES_DIR, serie)
    scripts = sorted(
        [f for f in os.listdir(pasta) if f.startswith("rename_t") and f.endswith(".py")],
        key=numero_temporada
    )
    return scripts  # ex: ["rename_t1.py", "rename_t2.py"]


def label_temporada(nome_script):
    """'rename_t2.py' → 'Temporada 2'"""
    n = numero_temporada(nome_script)
    return f"Temporada {n}"


# ──────────────────────────────────────────
# Execução do rename
# ──────────────────────────────────────────

def executar_rename(script_path, episodios_escolhidos=None):
    """
    Carrega o módulo de rename, lista os episódios,
    pede confirmação e executa os renames.

    episodios_escolhidos: None = todos | int = número do episódio específico
    """
    modulo = carregar_modulo(script_path)

    pasta     = modulo.PASTA
    episodios = modulo.EPISODIOS  # dict {int: str}

    if not os.path.exists(pasta):
        print(f"\n  ❌ Pasta não encontrada: {pasta}")
        return

    arquivos = sorted([f for f in os.listdir(pasta) if f.endswith(".mp4")])

    if len(arquivos) != len(episodios):
        print(f"\n  ⚠️  Arquivos encontrados: {len(arquivos)} | Esperados: {len(episodios)}")
        print("  Verifique se todos os episódios estão na pasta e tente novamente.")
        for f in arquivos:
            print(f"    - {f}")
        return

    # Monta os pares (arquivo_atual → nome_novo)
    pares = {}
    for i, arquivo in enumerate(arquivos, start=1):
        novo_nome = f"E{i:02d} - {episodios[i]}.mp4"
        pares[i]  = (arquivo, novo_nome)

    # Filtra episódios escolhidos
    if episodios_escolhidos is not None:
        pares = {k: v for k, v in pares.items() if k in episodios_escolhidos}

    if not pares:
        print("\n  ⚠️  Nenhum episódio para renomear.")
        return

    # Preview
    print("\n  📋 Preview do rename:")
    for i, (origem, destino) in pares.items():
        print(f"    E{i:02d}  {origem}  →  {destino}")

    # Confirmação
    print()
    confirmacao = input("  ❓ Confirmar rename? (s/N): ").strip().lower()
    if confirmacao != "s":
        print("  ⏭  Operação cancelada.")
        return

    # Executa
    for i, (origem, destino) in pares.items():
        origem_path  = os.path.join(pasta, origem)
        destino_path = os.path.join(pasta, destino)

        if os.path.exists(destino_path):
            print(f"  ⏭  Pulando (já existe): {destino}")
            continue

        os.rename(origem_path, destino_path)
        print(f"  ✅ {origem}  →  {destino}")


# ──────────────────────────────────────────
# Fluxo Séries
# ──────────────────────────────────────────

def renomear_series():
    series = descobrir_series()

    if not series:
        print("  ❌ Nenhuma série encontrada em scripts/series/")
        return

    # Formata os nomes para exibição (snake_case → título)
    labels_series = [s.replace("_", " ").title() for s in series]
    label_escolhido = escolher_opcao(labels_series, "📺 Qual série?")
    serie = series[labels_series.index(label_escolhido)]

    # Temporadas
    scripts_temp = descobrir_temporadas(serie)

    if not scripts_temp:
        print(f"  ❌ Nenhum script de rename encontrado para {serie}.")
        return

    labels_temp = [label_temporada(s) for s in scripts_temp]
    label_temp  = escolher_opcao(labels_temp, "📂 Qual temporada?", permitir_todos=True)

    if label_temp is None:
        temporadas_para_renomear = scripts_temp
    else:
        temporadas_para_renomear = [scripts_temp[labels_temp.index(label_temp)]]

    for script in temporadas_para_renomear:
        script_path = os.path.join(SERIES_DIR, serie, script)
        modulo      = carregar_modulo(script_path)
        episodios   = modulo.EPISODIOS

        print(f"\n{'─'*40}")
        print(f"  📂 {serie.replace('_', ' ').title()} — {label_temporada(script)}")

        # Lista de episódios para escolher
        labels_ep = [f"E{i:02d} - {titulo}" for i, titulo in episodios.items()]
        ep_label  = escolher_opcao(labels_ep, "🎬 Qual episódio?", permitir_todos=True)

        if ep_label is None:
            eps_escolhidos = None  # todos
        else:
            idx_ep        = labels_ep.index(ep_label) + 1  # episódios são 1-indexed
            eps_escolhidos = {idx_ep}

        executar_rename(script_path, eps_escolhidos)

    print("\n✅ Operação de rename finalizada!")


# ──────────────────────────────────────────
# Fluxo Filmes (reservado para o futuro)
# ──────────────────────────────────────────

def renomear_filmes():
    print("\n  🚧 Rename de filmes ainda não implementado.")
    print("     Crie os scripts em scripts/movies/ e atualize esta função.")


# ──────────────────────────────────────────
# Main
# ──────────────────────────────────────────

def main():
    print("=" * 40)
    print("       🎬 Renomeador de Mídia")
    print("=" * 40)

    tipos = ["Séries", "Filmes"]
    tipo  = escolher_opcao(tipos, "O que deseja renomear?")

    if tipo == "Séries":
        renomear_series()
    elif tipo == "Filmes":
        renomear_filmes()


if __name__ == "__main__":
    main()