"""
Passo 4 do pipeline de RAG: busca por similaridade, com interface de linha
de comando (não exige alterar o código principal para fazer uma pergunta).

Modos de uso:
  python busca.py "sua pergunta aqui"        -> busca direta via argumento
  python busca.py                            -> modo interativo (digite no terminal)
  python busca.py --demo                     -> roda as perguntas obrigatórias da prova
  python busca.py "pergunta" --top_k 5       -> controla quantos resultados retornar
"""

import argparse

import numpy as np

from embeddings import montar_indice


def buscar(
    pergunta: str,
    chunks: list,
    matriz_embeddings: np.ndarray,
    modelo,
    top_k: int = 3,
) -> list[dict]:
    """
    Busca os `top_k` chunks mais relevantes para `pergunta`.

    Retorna uma lista de dicts com: posicao, score, trecho, arquivo, secao.
    Levanta ValueError para entradas inválidas (tratadas no chamador).
    """
    if not pergunta or not pergunta.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    if not chunks or matriz_embeddings.size == 0:
        raise ValueError("O corpus está vazio — não há chunks para buscar.")

    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError(f"top_k inválido: {top_k}. Deve ser um inteiro positivo.")

    top_k = min(top_k, len(chunks))  # não pedir mais resultados do que existem

    embedding_pergunta = modelo.encode([pergunta], normalize_embeddings=True)[0]

    # Produto escalar == similaridade de cosseno, pois os vetores são normalizados
    scores = matriz_embeddings @ embedding_pergunta

    indices_ordenados = np.argsort(scores)[::-1][:top_k]

    resultados = []
    for posicao, idx in enumerate(indices_ordenados, start=1):
        chunk = chunks[idx]
        resultados.append(
            {
                "posicao": posicao,
                "score": float(scores[idx]),
                "trecho": chunk.texto,
                "arquivo": chunk.arquivo,
                "secao": chunk.titulo_secao,
            }
        )

    return resultados


def exibir_resultados(pergunta: str, resultados: list[dict]) -> None:
    print(f"\nPergunta: {pergunta}")
    print("-" * 60)
    for r in resultados:
        print(f"[{r['posicao']}] score={r['score']:.4f}")
        print(f"    fonte: {r['arquivo']} | seção: {r['secao']}")
        print(f"    trecho: {r['trecho'][:200]}...")
        print()


def rodar_demo(chunks, matriz, modelo) -> None:
    """Roda as 3 perguntas obrigatórias da prova + os testes de erro."""
    perguntas_teste = [
        # resposta clara na documentação
        "Como fazer autenticação básica com httpx?",
        "Como configurar um timeout nas requisições?",
        # ampla / ambígua
        "O que é uma boa prática ao usar essa biblioteca?",
        "Como lidar com erros de rede?",
        # fora do assunto
        "Qual a receita de brigadeiro gourmet?",
        "Quem ganhou a Copa do Mundo de 2022?",
    ]

    for pergunta in perguntas_teste:
        try:
            resultados = buscar(pergunta, chunks, matriz, modelo, top_k=3)
            exibir_resultados(pergunta, resultados)
        except ValueError as erro:
            print(f"\nErro ao buscar '{pergunta}': {erro}")

    print("\n=== Testando tratamento de erros ===")
    for caso, kwargs in [
        ("pergunta vazia", dict(pergunta="", chunks=chunks, matriz_embeddings=matriz, modelo=modelo)),
        ("top_k inválido", dict(pergunta="teste", chunks=chunks, matriz_embeddings=matriz, modelo=modelo, top_k=-1)),
        ("corpus vazio", dict(pergunta="teste", chunks=[], matriz_embeddings=np.array([]), modelo=modelo)),
    ]:
        try:
            buscar(**kwargs)
        except ValueError as erro:
            print(f"[{caso}] tratado corretamente: {erro}")


def rodar_interativo(chunks, matriz, modelo, top_k: int) -> None:
    """Loop interativo: digite perguntas até digitar 'sair'."""
    print("\nModo interativo. Digite sua pergunta (ou 'sair' para encerrar).")
    while True:
        pergunta = input("\n> ")
        if pergunta.strip().lower() in ("sair", "exit", "quit"):
            print("Encerrando.")
            break
        try:
            resultados = buscar(pergunta, chunks, matriz, modelo, top_k=top_k)
            exibir_resultados(pergunta, resultados)
        except ValueError as erro:
            print(f"Erro: {erro}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Busca por similaridade na documentação do httpx (núcleo de RAG)."
    )
    parser.add_argument(
        "pergunta",
        nargs="?",
        default=None,
        help="Pergunta a buscar. Se omitida, entra em modo interativo.",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=3,
        help="Quantidade de resultados a retornar (padrão: 3).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Roda as 3 perguntas obrigatórias da prova + testes de tratamento de erro.",
    )
    args = parser.parse_args()

    print("Montando índice (isso carrega o modelo e gera os embeddings)...")
    chunks, matriz, modelo = montar_indice()

    if args.demo:
        rodar_demo(chunks, matriz, modelo)
    elif args.pergunta:
        try:
            resultados = buscar(args.pergunta, chunks, matriz, modelo, top_k=args.top_k)
            exibir_resultados(args.pergunta, resultados)
        except ValueError as erro:
            print(f"Erro: {erro}")
    else:
        rodar_interativo(chunks, matriz, modelo, top_k=args.top_k)


if __name__ == "__main__":
    main()
