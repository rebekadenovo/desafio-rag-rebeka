"""
Passo 3 do pipeline de RAG: gerar embeddings dos chunks.

Usa o modelo multilíngue sugerido pelo professor, que roda localmente
e funciona bem para perguntas em português sobre documentação em inglês.
Os embeddings são normalizados para que o produto escalar equivalha
à similaridade de cosseno na etapa de busca.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from chunking import Chunk, montar_todos_os_chunks

NOME_MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def carregar_modelo() -> SentenceTransformer:
    print(f"Carregando modelo '{NOME_MODELO}'... (pode demorar na primeira vez)")
    return SentenceTransformer(NOME_MODELO)


def gerar_embeddings(chunks: list[Chunk], modelo: SentenceTransformer) -> np.ndarray:
    """Gera uma matriz de embeddings normalizados, alinhada com a lista de chunks."""
    textos = [chunk.texto for chunk in chunks]
    embeddings = modelo.encode(
        textos,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return np.array(embeddings)


def montar_indice():
    """
    Monta o índice completo: chunks + matriz de embeddings alinhada.
    Retorna (chunks, matriz_embeddings, modelo) para uso na busca.
    """
    chunks = montar_todos_os_chunks()
    modelo = carregar_modelo()
    matriz = gerar_embeddings(chunks, modelo)
    return chunks, matriz, modelo


if __name__ == "__main__":
    chunks, matriz, modelo = montar_indice()

    print(f"\nTotal de chunks: {len(chunks)}")
    print(f"Formato da matriz de embeddings: {matriz.shape}")
    print(f"Dimensão de cada embedding: {matriz.shape[1]}")