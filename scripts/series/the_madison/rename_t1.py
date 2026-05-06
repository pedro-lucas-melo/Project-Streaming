import os

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_converted\The Madison\Temporada 1"

EPISODIOS = {
    1: "Pilot",
    2: "Let the Land Hold Me",
    3: "Watch Her Fall",
    4: "Tomorrow Is Goodbye",
    5: "No Name and a New Dream",
    6: "I Give Me Permission",
}

def main():
    arquivos = sorted([f for f in os.listdir(PASTA) if f.endswith(".mp4")])

    if len(arquivos) != len(EPISODIOS):
        print(f"⚠️  Encontrados {len(arquivos)} arquivos, esperados {len(EPISODIOS)}.")
        for f in arquivos:
            print(f"  - {f}")
        return

    for i, arquivo in enumerate(arquivos, start=1):
        novo_nome = f"E{i:02d} - {EPISODIOS[i]}.mp4"
        origem = os.path.join(PASTA, arquivo)
        destino = os.path.join(PASTA, novo_nome)
        print(f"  {arquivo}  →  {novo_nome}")
        os.rename(origem, destino)

    print("\n✅ Temporada 1 renomeada!")

if __name__ == "__main__":
    main()