"""
Extensão opcional do pipeline de RAG: geração fundamentada.

Usa os trechos recuperados pela busca por similaridade como contexto e
pede ao Gemini (API gratuita do Google) que responda SOMENTE com base
nesse contexto, citando as fontes e admitindo quando não sabe a resposta.

A chave de API NUNCA fica no código: é lida da variável de ambiente
GOOGLE_API_KEY. Se a chamada à API falhar (sem chave, sem internet,
limite de cota, etc.), a busca (recuperação) continua funcionando
normalmente -- a geração é só uma camada extra por cima.
"""

import os
import sys

from busca import buscar, exibir_resultados
from embeddings import montar_indice

# Verifique em https://ai.google.dev/gemini-api/docs/pricing qual modelo
# está atualmente disponível no nível gratuito e ajuste aqui se necessário.
NOME_MODELO_GEMINI = "gemini-3.6-flash"


def montar_prompt(pergunta: str, resultados: list[dict]) -> str:
    """Monta um prompt que restringe a resposta ao contexto recuperado."""
    contexto = "\n\n".join(
        f"[Fonte {r['posicao']}: {r['arquivo']} | {r['secao']}]\n{r['trecho']}"
        for r in resultados
    )

    return f"""Você é um assistente que responde SOMENTE com base no contexto abaixo,
extraído da documentação oficial do HTTPX (em inglês). Regras:

1. Responda SEMPRE em português do Brasil, mesmo que o contexto esteja em inglês.
2. Responda apenas com informações presentes no contexto.
3. Cite a fonte (o nome do arquivo) de onde tirou cada informação.
4. Se o contexto não contiver a resposta, diga claramente que não encontrou
   essa informação na documentação -- não invente nada.

Contexto:
{contexto}

Pergunta: {pergunta}

Resposta:"""


def gerar_resposta(pergunta: str, resultados: list[dict]) -> str | None:
    """
    Chama a API do Gemini para gerar uma resposta fundamentada.
    Retorna None (em vez de lançar erro) se algo falhar -- a busca
    continua valendo mesmo sem geração.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(
            "\n[Geração desativada: variável de ambiente GOOGLE_API_KEY não definida. "
            "A busca acima continua válida sem a geração.]"
        )
        return None

    try:
        from google import genai

        cliente = genai.Client(api_key=api_key)
        prompt = montar_prompt(pergunta, resultados)
        resposta = cliente.models.generate_content(
            model=NOME_MODELO_GEMINI,
            contents=prompt,
        )
        return resposta.text

    except Exception as erro:
        print(
            f"\n[Geração falhou ({erro}). A busca acima continua válida sem a geração.]"
        )
        return None


def main() -> None:
    if len(sys.argv) < 2:
        print('Uso: python gerar_resposta.py "sua pergunta aqui"')
        sys.exit(1)

    pergunta = sys.argv[1]

    print("Montando índice...")
    chunks, matriz, modelo_embeddings = montar_indice()

    resultados = buscar(pergunta, chunks, matriz, modelo_embeddings, top_k=5)
    exibir_resultados(pergunta, resultados)

    resposta = gerar_resposta(pergunta, resultados)
    if resposta:
        print("\n=== Resposta gerada (fundamentada nos trechos acima) ===")
        print(resposta)


if __name__ == "__main__":
    main()