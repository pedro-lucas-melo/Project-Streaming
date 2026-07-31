import os
import re

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_unconverted\series\Marvel - O Justiceiro\Temporada 1"

EPISODIOS = {
    1: "Três da Madrugada",
    2: "Dois Homens Mortos",
    3: "Kandahar",
    4: "Reabastecimento",
    5: "Gunner",
    6: "O Infiltrado",
    7: "Na Mira",
    8: "Aço Resfriado",
    9: "Este Lado Para o Inimigo",
    10: "Virtude dos Maus",
    11: "Perigo Próximo",
    12: "Lar",
    13: "Memento Mori",
}

EXTENSOES = (".mkv", ".mp4")
PADRAO = re.compile(r"S01E(\d{2})", re.IGNORECASE)

def main():
    arquivos = [f for f in os.listdir(PASTA) if f.lower().endswith(EXTENSOES)]

    if len(arquivos) != len(EPISODIOS):
        print(f"⚠️  Encontrados {len(arquivos)} arquivos, esperados {len(EPISODIOS)}.")
        for f in arquivos:
            print(f"  - {f}")
        return

    for arquivo in arquivos:
        m = PADRAO.search(arquivo)
        if not m:
            print(f"⚠️  Sem SxxExx: {arquivo} — abortado.")
            return
        ep = int(m.group(1))
        if ep not in EPISODIOS:
            print(f"⚠️  Episódio {ep} fora do mapa: {arquivo} — abortado.")
            return
        ext = os.path.splitext(arquivo)[1].lower()
        novo_nome = f"E{ep:02d} - {EPISODIOS[ep]}{ext}"
        print(f"  {arquivo}  →  {novo_nome}")
        os.rename(os.path.join(PASTA, arquivo), os.path.join(PASTA, novo_nome))

    print("\n✅ Temporada 1 renomeada!")

if __name__ == "__main__":
    main()
