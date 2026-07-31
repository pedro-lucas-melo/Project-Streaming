import os
import re

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_unconverted\series\Marvel - O Justiceiro\Temporada 2"

EPISODIOS = {
    1: "Briga de Bar",
    2: "Lutar ou Fugir",
    3: "Agitar a Água",
    4: "Cicatrizes do Passado",
    5: "O Jogo",
    6: "Nakazat",
    7: "Um Dia Ruim",
    8: "O Protetor do Meu Irmão",
    9: "A Recompensa",
    10: "Coração Sombrio",
    11: "O Abismo",
    12: "Rota de Colisão",
    13: "A Tormenta",
}

EXTENSOES = (".mkv", ".mp4")
PADRAO = re.compile(r"S02E(\d{2})", re.IGNORECASE)

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

    print("\n✅ Temporada 2 renomeada!")

if __name__ == "__main__":
    main()
