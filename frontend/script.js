const API_URL = "http://127.0.0.1:5000";

const form = document.getElementById("form-busca");
const input = document.getElementById("input-pergunta");
const selectTopK = document.getElementById("select-topk");
const statusEl = document.getElementById("status-conexao");
const resultadosEl = document.getElementById("resultados");
const respostaEl = document.getElementById("resposta-gerada");

function definirStatus(tipo, texto) {
  statusEl.textContent = texto;
  statusEl.className = `status status--${tipo}`;
}

async function checarServidor() {
  try {
    const resp = await fetch(API_URL + "/");
    if (!resp.ok) throw new Error("resposta não ok");
    const dados = await resp.json();
    definirStatus("ok", `conectado · ${dados.total_chunks} chunks`);
  } catch (erro) {
    definirStatus("erro", "servidor offline — rode: python app.py");
  }
}

function limparResultados() {
  resultadosEl.innerHTML = "";
}

function mostrarMensagem(texto, classe) {
  limparResultados();
  const p = document.createElement("p");
  p.className = classe;
  p.textContent = texto;
  resultadosEl.appendChild(p);
}

function mostrarRespostaGerada(texto) {
  if (!texto) {
    respostaEl.hidden = true;
    respostaEl.textContent = "";
    return;
  }
  respostaEl.hidden = false;
  respostaEl.innerHTML = "";

  const label = document.createElement("span");
  label.className = "resposta-gerada-label";
  label.textContent = "resposta gerada, com base nos trechos abaixo";

  const corpo = document.createElement("div");
  corpo.textContent = texto;

  respostaEl.appendChild(label);
  respostaEl.appendChild(corpo);
}

function renderizarResultados(resultados) {
  limparResultados();

  if (resultados.length === 0) {
    mostrarMensagem("Nenhum resultado encontrado.", "dica");
    return;
  }

  const scoreMaximo = Math.max(...resultados.map((r) => r.score));

  resultados.forEach((r) => {
    const item = document.createElement("article");
    item.className = "resultado";

    const cabecalho = document.createElement("div");
    cabecalho.className = "resultado-cabecalho";

    const fonte = document.createElement("span");
    fonte.className = "resultado-fonte";
    fonte.textContent = `[${r.posicao}] ${r.arquivo}`;

    const score = document.createElement("span");
    score.className = "resultado-score";
    score.textContent = `score ${r.score.toFixed(3)}`;

    cabecalho.appendChild(fonte);
    cabecalho.appendChild(score);

    const secao = document.createElement("p");
    secao.className = "resultado-secao";
    secao.textContent = r.secao;

    const barra = document.createElement("div");
    barra.className = "barra-score";
    const preenchida = document.createElement("div");
    preenchida.className = "barra-score-preenchida";
    const largura = scoreMaximo > 0 ? (r.score / scoreMaximo) * 100 : 0;
    preenchida.style.width = `${largura}%`;
    barra.appendChild(preenchida);

    const trecho = document.createElement("p");
    trecho.className = "resultado-trecho";
    trecho.textContent = r.trecho;

    item.appendChild(cabecalho);
    item.appendChild(secao);
    item.appendChild(barra);
    item.appendChild(trecho);

    resultadosEl.appendChild(item);
  });
}

async function buscarEGerar(pergunta, topK) {
  mostrarRespostaGerada(null);
  mostrarMensagem("Buscando e gerando resposta…", "dica");

  try {
    const resp = await fetch(API_URL + "/gerar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pergunta, top_k: topK }),
    });

    const dados = await resp.json();

    if (!resp.ok || !dados.ok) {
      mostrarMensagem(dados.erro || "Erro ao buscar.", "erro-busca");
      return;
    }

    mostrarRespostaGerada(dados.resposta);
    renderizarResultados(dados.resultados);
  } catch (erro) {
    mostrarMensagem(
      "Não consegui falar com o servidor local. Confira se o backend (python app.py) está rodando.",
      "erro-busca"
    );
  }
}

form.addEventListener("submit", (evento) => {
  evento.preventDefault();
  const pergunta = input.value.trim();
  if (!pergunta) return;

  const topK = parseInt(selectTopK.value, 10);
  buscarEGerar(pergunta, topK);
});

checarServidor();