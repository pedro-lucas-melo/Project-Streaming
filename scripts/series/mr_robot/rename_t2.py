import os

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_converted\Mr Robot\Temporada 2"

EPISODIOS = {
    1:  "unm4sk-pt1.tc",
    2:  "unm4sk-pt2.tc",
    3:  "k3rnel-pan1c.ksd",
    4:  "init1.asec",
    5:  "logic_b0mb.hc",
    6:  "m4ster_s1ave.aes",
    7:  "h4ndshake.sme",
    8:  "succ3ss0r.p12",
    9:  "init5.fve",
    10: "pyth0n-pt1.p7z",
    11: "pyth0n-pt2.p7z",
    12: "d3bug_like_a_girl.deb",
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

    print("\n✅ Temporada 2 renomeada!")

if __name__ == "__main__":
    main()