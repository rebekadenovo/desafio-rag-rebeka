"""
Backend simples que expõe a busca por similaridade (busca.py) como uma
API HTTP, para o front-end (frontend/) consumir via fetch().

Rodar com: python app.py
Servidor sobe em http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from busca import buscar
from embeddings import montar_indice
from gerar_resposta import gerar_resposta

app = Flask(__name__)
CORS(app)  # permite que o frontend (aberto como arquivo local) chame essa API

print("Carregando índice (modelo + embeddings)... isso roda uma vez só.")
CHUNKS, MATRIZ, MODELO = montar_indice()
print(f"Índice pronto: {len(CHUNKS)} chunks carregados.")


@app.route("/", methods=["GET"])
def status():
    return jsonify({"status": "ok", "total_chunks": len(CHUNKS)})


@app.route("/buscar", methods=["POST"])
def rota_buscar():
    dados = request.get_json(silent=True) or {}
    pergunta = dados.get("pergunta", "")
    top_k = dados.get("top_k", 3)

    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "erro": "top_k inválido."}), 400

    try:
        resultados = buscar(pergunta, CHUNKS, MATRIZ, MODELO, top_k=top_k)
        return jsonify({"ok": True, "resultados": resultados})
    except ValueError as erro:
        return jsonify({"ok": False, "erro": str(erro)}), 400


@app.route("/gerar", methods=["POST"])
def rota_gerar():
    """Busca os trechos e, em cima deles, gera uma resposta em português."""
    dados = request.get_json(silent=True) or {}
    pergunta = dados.get("pergunta", "")
    top_k = dados.get("top_k", 5)

    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "erro": "top_k inválido."}), 400

    try:
        resultados = buscar(pergunta, CHUNKS, MATRIZ, MODELO, top_k=top_k)
    except ValueError as erro:
        return jsonify({"ok": False, "erro": str(erro)}), 400

    resposta = gerar_resposta(pergunta, resultados)  # None se a API falhar
    return jsonify({"ok": True, "resultados": resultados, "resposta": resposta})


if __name__ == "__main__":
    app.run(port=5000, debug=False)