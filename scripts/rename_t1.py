import os

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_converted\Mr Robot\Temporada 1"

EPISODIOS = {
    1:  "eps1.0_hellofriend.mov",
    2:  "eps1.1_ones-and-zer0es.mpeg",
    3:  "eps1.2_d3bug.mkv",
    4:  "eps1.3_da3m0ns.mp4",
    5:  "eps1.4_3xpl0its.wmv",
    6:  "eps1.5_br4ve-trave1er.asf",
    7:  "eps1.6_v1ew-s0urce.flv",
    8:  "eps1.7_wh1ter0se.m4v",
    9:  "eps1.8_m1rr0r1ng.qt",
    10: "eps1.9_zer0-day.avi",
}

def main():
    arquivos = sorted([f for f in os.listdir(PASTA) if f.endswith(".mp4")])

    if len(arquivos) != len(EPISODIOS):
        print(f"⚠️  Encontrados {len(arquivos)} arquivos, esperados {len(EPISODIOS)}. Verifique a pasta.")
        for f in arquivos:
            print(f"  - {f}")
        return

    for i, arquivo in enumerate(arquivos, start=1):
        nome_ep = EPISODIOS[i]
        novo_nome = f"E{i:02d} - {nome_ep}.mp4"
        origem = os.path.join(PASTA, arquivo)
        destino = os.path.join(PASTA, novo_nome)

        print(f"  {arquivo}  →  {novo_nome}")
        os.rename(origem, destino)

    print("\n✅ Temporada 1 renomeada!")

if __name__ == "__main__":
    main()