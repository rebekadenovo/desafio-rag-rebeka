"""
Extensão opcional: avaliação simples da recuperação.

Define uma lista de perguntas com a fonte (arquivo) esperada, roda a
busca para cada uma, e verifica se a fonte esperada aparece entre os
top_k resultados. No final, reporta uma taxa de acerto.

Isso NÃO substitui as 3 perguntas obrigatórias da prova -- é uma
extensão opcional que reforça reflexão e evidência de testes.
"""

from busca import buscar
from embeddings import montar_indice

# Cada item: (pergunta, trecho do caminho do arquivo que esperamos ver
# entre os resultados). Ajuste/adicione perguntas à vontade.
CASOS_DE_TESTE = [
    ("Como fazer autenticação básica com httpx?", "authentication"),
    ("Como configurar um timeout nas requisições?", "timeouts"),
    ("Como faço upload de arquivos com httpx?", "quickstart"),
    ("O que é o parâmetro follow_redirects?", "quickstart"),
    ("Como usar httpx de forma assíncrona?", "async"),
    ("Como configurar um proxy no httpx?", "proxies"),
]


def avaliar(chunks, matriz, modelo, top_k: int = 3) -> None:
    acertos = 0

    print(f"Avaliando {len(CASOS_DE_TESTE)} perguntas (top_k={top_k})\n")
    print("-" * 70)

    for pergunta, esperado in CASOS_DE_TESTE:
        resultados = buscar(pergunta, chunks, matriz, modelo, top_k=top_k)
        arquivos_retornados = [r["arquivo"] for r in resultados]

        encontrou = any(esperado in arq for arq in arquivos_retornados)
        if encontrou:
            acertos += 1

        status = "OK" if encontrou else "FALHOU"
        print(f"[{status}] {pergunta}")
        print(f"        esperado: contém '{esperado}'")
        print(f"        retornado: {arquivos_retornados}")
        print()

    total = len(CASOS_DE_TESTE)
    taxa = (acertos / total) * 100
    print("-" * 70)
    print(f"Resultado final: {acertos}/{total} corretos ({taxa:.0f}%)")


if __name__ == "__main__":
    print("Montando índice...")
    chunks, matriz, modelo = montar_indice()
    avaliar(chunks, matriz, modelo)
