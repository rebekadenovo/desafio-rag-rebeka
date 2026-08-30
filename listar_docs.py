"""
Passo 1 do pipeline de RAG: encontrar os arquivos Markdown da documentação.

Este script percorre recursivamente a pasta httpx/docs/ e lista todos os
arquivos .md encontrados. No commit fixado pela prova, o resultado esperado
é 23 arquivos -- use essa contagem apenas para confirmar que o caminho
está correto.
"""

from pathlib import Path

# O script fica ao lado da pasta "httpx" clonada do repositório
DOCS_PATH = Path("httpx/docs")


def listar_arquivos_markdown(pasta: Path) -> list[Path]:
    """Retorna todos os arquivos .md dentro de `pasta`, incluindo subpastas."""
    if not pasta.exists():
        raise FileNotFoundError(
            f"Pasta não encontrada: {pasta.resolve()}. "
            "Confirme se o repositório httpx foi clonado ao lado deste script."
        )

    arquivos = sorted(pasta.rglob("*.md"))
    return arquivos


if __name__ == "__main__":
    arquivos = listar_arquivos_markdown(DOCS_PATH)

    print(f"Encontrados {len(arquivos)} arquivos Markdown em '{DOCS_PATH}':\n")
    for caminho in arquivos:
        print(f" - {caminho}")
