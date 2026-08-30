"""
Passo 2 do pipeline de RAG: dividir os documentos em chunks com metadados.

Cada chunk guarda: texto, arquivo de origem, título/seção e um id único.
Isso é o que permite, depois, rastrear cada resultado de busca até a
sua origem exata na documentação.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from listar_docs import listar_arquivos_markdown, DOCS_PATH

TAMANHO_CHUNK_PALAVRAS = 80  # ponto de partida sugerido: 60 a 90 palavras
SOBREPOSICAO_PALAVRAS = 15
MINIMO_PALAVRAS_COM_LETRAS = 5  # abaixo disso, o chunk é considerado "ruído"


def tem_conteudo_relevante(texto: str) -> bool:
    """
    Filtra chunks que são só símbolos/formatação Markdown (ex: '---', crases
    de bloco de código vazias), sem texto explicativo de verdade.
    """
    palavras_com_letras = [p for p in texto.split() if re.search(r"[A-Za-zÀ-ÿ]", p)]
    return len(palavras_com_letras) >= MINIMO_PALAVRAS_COM_LETRAS


@dataclass
class Chunk:
    texto: str
    arquivo: str
    titulo_secao: str
    chunk_id: str


def dividir_em_secoes(conteudo: str) -> list[tuple[str, str]]:
    """
    Divide o conteúdo de um arquivo Markdown em (titulo_secao, texto),
    usando cabeçalhos (#, ##, ###...) como pontos de corte.
    """
    linhas = conteudo.splitlines()
    secoes = []
    titulo_atual = "Introdução"
    texto_atual = []

    for linha in linhas:
        if re.match(r"^#{1,6}\s+", linha):
            if texto_atual:
                secoes.append((titulo_atual, "\n".join(texto_atual)))
            titulo_atual = linha.lstrip("#").strip()
            texto_atual = []
        else:
            texto_atual.append(linha)

    if texto_atual:
        secoes.append((titulo_atual, "\n".join(texto_atual)))

    return secoes


def dividir_em_chunks(
    texto: str,
    tamanho: int = TAMANHO_CHUNK_PALAVRAS,
    sobreposicao: int = SOBREPOSICAO_PALAVRAS,
) -> list[str]:
    """Divide um texto em blocos de `tamanho` palavras, com sobreposição."""
    palavras = texto.split()
    if not palavras:
        return []

    chunks = []
    inicio = 0
    while inicio < len(palavras):
        fim = inicio + tamanho
        bloco = " ".join(palavras[inicio:fim])
        if bloco.strip():
            chunks.append(bloco)
        inicio += tamanho - sobreposicao

    return chunks


def processar_arquivo(caminho: Path, docs_path: Path) -> list[Chunk]:
    """Lê um arquivo, divide em seções e depois em chunks, com metadados."""
    conteudo = caminho.read_text(encoding="utf-8")
    caminho_relativo = str(caminho.relative_to(docs_path.parent))

    chunks_do_arquivo = []
    for titulo_secao, texto_secao in dividir_em_secoes(conteudo):
        blocos = dividir_em_chunks(texto_secao)
        for i, bloco in enumerate(blocos):
            if not tem_conteudo_relevante(bloco):
                continue
            chunk_id = f"{caminho.stem}::{titulo_secao[:30]}::{i}"
            chunks_do_arquivo.append(
                Chunk(
                    texto=bloco,
                    arquivo=caminho_relativo,
                    titulo_secao=titulo_secao,
                    chunk_id=chunk_id,
                )
            )

    return chunks_do_arquivo


def montar_todos_os_chunks(docs_path: Path = DOCS_PATH) -> list[Chunk]:
    """Percorre todos os arquivos .md e retorna a lista completa de chunks."""
    arquivos = listar_arquivos_markdown(docs_path)
    todos_chunks = []
    for arquivo in arquivos:
        todos_chunks.extend(processar_arquivo(arquivo, docs_path))
    return todos_chunks


if __name__ == "__main__":
    chunks = montar_todos_os_chunks()

    print(f"Total de chunks gerados: {len(chunks)}\n")
    print("Exemplo do primeiro chunk:")
    print(f"  arquivo: {chunks[0].arquivo}")
    print(f"  seção:   {chunks[0].titulo_secao}")
    print(f"  id:      {chunks[0].chunk_id}")
    print(f"  texto:   {chunks[0].texto[:150]}...")
