import os

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos\Mr Robot\Temporada 3"

EPISODIOS = {
    1:  "power-saver-mode.mkv",
    2:  "undo.gz",
    3:  "legacy.so",
    4:  "metadata.par2",
    5:  "runtime-error.r00",
    6:  "kill-process.inc",
    7:  "fredrick+tanya.chk",
    8:  "dont-delete-me.ko",
    9:  "stage3.torrent",
    10: "shutdown-r",
}

def main():
    arquivos = sorted([f for f in os.listdir(PASTA) if f.endswith(".mkv")])

    if len(arquivos) != len(EPISODIOS):
        print(f"⚠️  Encontrados {len(arquivos)} arquivos, esperados {len(EPISODIOS)}.")
        for f in arquivos:
            print(f"  - {f}")
        return

    for i, arquivo in enumerate(arquivos, start=1):
        novo_nome = f"E{i:02d} - {EPISODIOS[i]}.mkv"
        origem = os.path.join(PASTA, arquivo)
        destino = os.path.join(PASTA, novo_nome)
        print(f"  {arquivo}  →  {novo_nome}")
        os.rename(origem, destino)

    print("\n✅ Temporada 3 renomeada!")

if __name__ == "__main__":
    main()