import os

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_converted\Mr Robot\Temporada 1"

EPISODIOS = {
    1:  "hellofriend.mov",
    2:  "ones-and-zer0es.mpeg",
    3:  "d3bug.mkv",
    4:  "da3m0ns.mp4",
    5:  "3xpl0its.wmv",
    6:  "br4ve-trave1er.asf",
    7:  "v1ew-s0urce.flv",
    8:  "wh1ter0se.m4v",
    9:  "m1rr0r1ng.qt",
    10: "zer0-day.avi",
}

def main():
    arquivos = sorted([f for f in os.listdir(PASTA) if f.endswith(".mp4")])

    if len(arquivos) != len(EPISODIOS):
        print(f"⚠️  Encontrados {len(arquivos)} arquivos, esperados {len(EPISODIOS)}.")
        for f in arquivos:
            print(f"  - {f}")
        return

    # Passo 1 — renomeia tudo para temporário (evita conflito)
    for i, arquivo in enumerate(arquivos, start=1):
        os.rename(
            os.path.join(PASTA, arquivo),
            os.path.join(PASTA, f"temp_{i:02d}.mp4")
        )

    # Passo 2 — renomeia do temporário para o nome final
    for i in range(1, len(EPISODIOS) + 1):
        novo_nome = f"E{i:02d} - {EPISODIOS[i]}.mp4"
        os.rename(
            os.path.join(PASTA, f"temp_{i:02d}.mp4"),
            os.path.join(PASTA, novo_nome)
        )
        print(f"  E{i:02d} - {EPISODIOS[i]}.mp4")

    print("\n✅ Temporada 1 renomeada!")

if __name__ == "__main__":
    main()