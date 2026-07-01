import os
import re

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_unconverted\series\Lioness\Temporada 1"

EPISODIOS = {
    1: "Soldados Para Sacrifício",
    2: "A Surra",
    3: "Contusão em Forma de Punho",
    4: "A Escolha do Fracasso",
    5: "A Verdade é a Mentira Mais Astuta",
    6: "A Mentira é a Verdade",
    7: "Desejo Que a Luta Acabe",
    8: "Partir é a Ilusão da Ordem",
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
