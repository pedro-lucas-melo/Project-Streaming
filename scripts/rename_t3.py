import os

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos\Mr Robot\Temporada 3"

EPISODIOS = {
    1:  "eps3.0_power-saver-mode.mkv",
    2:  "eps3.1_undo.gz",
    3:  "eps3.2_legacy.so",
    4:  "eps3.3_metadata.par2",
    5:  "eps3.4_runtime-error.r00",
    6:  "eps3.5_kill-process.inc",
    7:  "eps3.6_fredrick+tanya.chk",
    8:  "eps3.7_dont-delete-me.ko",
    9:  "eps3.8_stage3.torrent",
    10: "eps3.9_shutdown-r",
}

def main():
    arquivos = sorted([f for f in os.listdir(PASTA) if f.endswith(".mkv")])

    if len(arquivos) != len(EPISODIOS):
        print(f"⚠️  Encontrados {len(arquivos)} arquivos, esperados {len(EPISODIOS)}. Verifique a pasta.")
        for f in arquivos:
            print(f"  - {f}")
        return

    for i, arquivo in enumerate(arquivos, start=1):
        nome_ep = EPISODIOS[i]
        novo_nome = f"E{i:02d} - {nome_ep}.mkv"
        origem = os.path.join(PASTA, arquivo)
        destino = os.path.join(PASTA, novo_nome)

        print(f"  {arquivo}  →  {novo_nome}")
        os.rename(origem, destino)

    print("\n✅ Temporada 3 renomeada!")

if __name__ == "__main__":
    main()