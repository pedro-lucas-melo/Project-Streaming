from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

SOURCE_SERIES_DIR = os.getenv("SOURCE_SERIES_DIR")
SOURCE_MOVIES_DIR = os.getenv("SOURCE_MOVIES_DIR")
OUTPUT_SERIES_DIR = os.getenv("MEDIA_SERIES_DIR")
OUTPUT_MOVIES_DIR = os.getenv("MEDIA_MOVIES_DIR")


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

        print("Opção inválida, tente novamente.")


def convert_video(input_path, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        print(f"  ⏭  Pulando (já existe): {os.path.basename(output_path)}")
        return

    print(f"  🔄 Convertendo: {os.path.basename(input_path)}")

    command = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    if result.returncode == 0:
        print(f"  ✅ Concluído: {os.path.basename(output_path)}")
    else:
        print(f"  ❌ Erro ao converter: {os.path.basename(input_path)}")


def arquivos_video(pasta):
    return sorted([
        f for f in os.listdir(pasta)
        if f.lower().endswith((".mkv", ".mp4"))
    ])


# ──────────────────────────────────────────
# Fluxo Séries
# ──────────────────────────────────────────

def converter_series():
    if not SOURCE_SERIES_DIR or not os.path.exists(SOURCE_SERIES_DIR):
        print("❌ SOURCE_SERIES_DIR não definido ou não existe no .env")
        return

    series = sorted([
        d for d in os.listdir(SOURCE_SERIES_DIR)
        if os.path.isdir(os.path.join(SOURCE_SERIES_DIR, d))
    ])

    if not series:
        print("Nenhuma série encontrada.")
        return

    serie = escolher_opcao(series, "📺 Qual série?")

    serie_source = os.path.join(SOURCE_SERIES_DIR, serie)
    serie_output = os.path.join(OUTPUT_SERIES_DIR, serie)

    temporadas = sorted([
        d for d in os.listdir(serie_source)
        if os.path.isdir(os.path.join(serie_source, d))
    ])

    if not temporadas:
        print("Nenhuma temporada encontrada.")
        return

    temporada = escolher_opcao(temporadas, "📂 Qual temporada?", permitir_todos=True)

    temporadas_para_converter = temporadas if temporada is None else [temporada]

    for temp in temporadas_para_converter:
        temp_source = os.path.join(serie_source, temp)
        temp_output = os.path.join(serie_output, temp)

        episodios = arquivos_video(temp_source)

        if not episodios:
            print(f"\nNenhum episódio encontrado em {temp}.")
            continue

        if len(temporadas_para_converter) == 1:
            # Pergunta sobre episódio específico apenas quando é 1 temporada
            episodio = escolher_opcao(episodios, f"🎬 Qual episódio de {temp}?", permitir_todos=True)
            episodios_para_converter = episodios if episodio is None else [episodio]
        else:
            print(f"\n📂 Convertendo toda a {temp}...")
            episodios_para_converter = episodios

        for ep in episodios_para_converter:
            input_path = os.path.join(temp_source, ep)
            output_file = ep.rsplit(".", 1)[0] + ".mp4"
            output_path = os.path.join(temp_output, output_file)
            convert_video(input_path, output_path)

    print("\n✅ Conversão de séries finalizada!")


# ──────────────────────────────────────────
# Fluxo Filmes
# ──────────────────────────────────────────

def converter_filmes():
    if not SOURCE_MOVIES_DIR or not os.path.exists(SOURCE_MOVIES_DIR):
        print("❌ SOURCE_MOVIES_DIR não definido ou não existe no .env")
        return

    filmes = arquivos_video(SOURCE_MOVIES_DIR)

    if not filmes:
        print("Nenhum filme encontrado.")
        return

    filme = escolher_opcao(filmes, "🎥 Qual filme?", permitir_todos=True)

    filmes_para_converter = filmes if filme is None else [filme]

    for f in filmes_para_converter:
        input_path = os.path.join(SOURCE_MOVIES_DIR, f)
        output_file = f.rsplit(".", 1)[0] + ".mp4"
        output_path = os.path.join(OUTPUT_MOVIES_DIR, output_file)
        convert_video(input_path, output_path)

    print("\n✅ Conversão de filmes finalizada!")


# ──────────────────────────────────────────
# Main
# ──────────────────────────────────────────

def main():
    print("=" * 40)
    print("       🎬 Conversor de Vídeos")
    print("=" * 40)

    tipos = ["Séries", "Filmes"]
    tipo = escolher_opcao(tipos, "O que deseja converter?")

    if tipo == "Séries":
        converter_series()
    elif tipo == "Filmes":
        converter_filmes()


if __name__ == "__main__":
    main()