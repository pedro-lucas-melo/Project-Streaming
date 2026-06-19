import os

PASTA = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_converted\series\Mr Robot\Temporada 4"

EPISODIOS = {
    1:  "401-unauthorized.mp4",
    2:  "402-payment-required.mp4",
    3:  "403-forbidden.mp4",
    4:  "404-not-found.mp4",
    5:  "405-method-not-allowed.mp4",
    6:  "406-not-acceptable.mp4",
    7:  "407-proxy-authentication-required.mp4",
    8:  "408-request-timeout.mp4",
    9:  "409-conflict.mp4",
    10: "410-gone.mp4",
    11: "411-length-required.mp4",
    12: "412-precondition-failed.mp4",
    13: "eXit.mp4",
}

def main():
    arquivos = sorted([f for f in os.listdir(PASTA) if f.endswith(".mp4")])

    if len(arquivos) != len(EPISODIOS):
        print(f"⚠️  Encontrados {len(arquivos)} arquivos, esperados {len(EPISODIOS)}.")
        for f in arquivos:
            print(f"  - {f}")
        return

    for i, arquivo in enumerate(arquivos, start=1):
        novo_nome = f"E{i:02d} - {EPISODIOS[i]}"
        origem = os.path.join(PASTA, arquivo)
        destino = os.path.join(PASTA, novo_nome)
        print(f"  {arquivo}  →  {novo_nome}")
        os.rename(origem, destino)

    print("\n✅ Temporada 4 renomeada!")

if __name__ == "__main__":
    main()
