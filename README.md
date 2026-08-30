# Mini-RAG sobre documentação do HTTPX

## Identificação

- Nome do aluno: Rebeka Júlia Araújo
- RGM: 40601447
- Formato da solução: script Python (linha de comando)
- Link do vídeo: _[preencher após gravar]_
- Link do Colab, se aplicável: não se aplica (solução rodou localmente via VSCode)

## Objetivo

O sistema implementa o núcleo de recuperação (retrieval) de um RAG: dada uma pergunta em linguagem natural, ele busca e retorna os trechos mais relevantes da documentação oficial do HTTPX, com a fonte exata de cada trecho. A geração de resposta em linguagem natural não foi implementada nesta entrega — o foco é a busca semântica.

## Arquitetura resumida

```text
httpx/docs/**/*.md → chunks (por seção + tamanho fixo) + metadados
→ embeddings (sentence-transformers) → matriz de embeddings em memória
→ busca por similaridade de cosseno → top_k resultados com trecho, fonte e score
```

## Como executar do zero

1. Ter Python 3.10+ instalado.
2. Criar e ativar um ambiente virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Instalar as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
4. Clonar a documentação do HTTPX no commit fixado pela prova, na mesma pasta do projeto:
   ```powershell
   git clone https://github.com/encode/httpx.git
   cd httpx
   git checkout b5addb64f0161ff6bfe94c124ef76f6a1fba5254
   cd ..
   ```
5. Fazer uma pergunta (três formas possíveis):
   ```powershell
   # pergunta direta
   python busca.py "Como fazer autenticação básica com httpx?"

   # modo interativo
   python busca.py

   # roda as perguntas de teste obrigatórias da prova
   python busca.py --demo
   ```

## Decisões técnicas

### Chunking

- Estratégia: os arquivos Markdown são divididos primeiro por seção (usando os cabeçalhos `#`, `##`, `###` como pontos de corte), e depois cada seção é dividida em blocos de tamanho fixo, para evitar cortar um título no meio da explicação.
- Tamanho aproximado: 80 palavras por chunk.
- Overlap: 15 palavras entre chunks consecutivos da mesma seção.
- Justificativa: 80 palavras ficou dentro da faixa sugerida (60-90) e produziu chunks com contexto suficiente sem ultrapassar o limite de 128 tokens do modelo de embeddings escolhido. Foi adicionado também um filtro que descarta chunks sem conteúdo textual relevante (ex: blocos formados só por `---` ou crases de código vazias), já que esses "chunks de ruído" apareciam com destaque indevido em buscas fora do escopo.

### Embeddings e busca

- Modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — multilíngue, público, roda localmente sem API key, adequado para perguntas em português sobre documentação em inglês.
- Forma de cálculo da similaridade: produto escalar entre embeddings normalizados, que equivale à similaridade de cosseno.
- Valor de `top_k`: 3 por padrão, configurável via argumento `--top_k`.
- Justificativa: por ser público e leve, o modelo atende ao requisito de caminho gratuito sem exigir hardware potente, mantendo boa qualidade de recuperação cross-lingual (pergunta em português, documentos em inglês).

### Metadados e fontes

Cada chunk carrega, desde a criação: o caminho relativo do arquivo de origem, o título da seção onde foi extraído e um identificador único. Esses metadados ficam armazenados junto com o texto (numa estrutura `Chunk`) e permanecem alinhados com a matriz de embeddings pelo índice da lista — por isso, ao recuperar um resultado, é possível voltar exatamente ao arquivo e à seção de onde ele veio.

## Perguntas de teste

### 1. Pergunta com resposta clara

- Pergunta: "Como configurar um timeout nas requisições?"
- Resultado esperado: trechos de `docs/quickstart.md` e `docs/advanced/timeouts.md` sobre configuração de timeout.
- O resultado foi relevante? Sim — os 3 primeiros resultados vieram exatamente dessas seções, com scores altos (0.63-0.69).

### 2. Pergunta ampla ou ambígua

- Pergunta: "Como lidar com erros de rede?"
- Resultado esperado: algo relacionado a exceções e tratamento de falhas de conexão.
- O resultado foi relevante? Parcialmente — trouxe `ConnectError`/`ConnectTimeout` de `advanced/transports.md`, que é pertinente, mas com score mais baixo (0.51) do que perguntas diretas, refletindo a natureza mais aberta da pergunta.

### 3. Pergunta fora do escopo

- Pergunta: "Qual a receita de brigadeiro gourmet?"
- Como o sistema reagiu: retornou os 3 chunks "menos distantes" tecnicamente (scores baixos, entre 0.16 e 0.19), sem nenhuma relação real com a pergunta — o sistema não tem um mecanismo para dizer "não sei".
- Como essa reação poderia melhorar: adicionar um limiar mínimo de score, abaixo do qual o sistema responde explicitamente que não encontrou informação relevante, em vez de sempre devolver os top_k "melhores dentre os piores".

## Limitações conhecidas

- O sistema sempre retorna `top_k` resultados, mesmo quando nenhum é realmente relevante (não há corte por score mínimo) — ficou evidente na pergunta fora do escopo, cujos scores (~0.16-0.19) são bem mais baixos que os de perguntas relevantes (~0.6-0.7), mas ainda assim são exibidos como se fossem resultados válidos.
- Não há etapa de geração de resposta em linguagem natural — apenas recuperação dos trechos e fontes.
- O chunking por contagem de palavras não usa a mesma tokenização do modelo de embeddings, então trechos com muito código podem, em casos raros, se aproximar do limite de 128 tokens do modelo.

## Uso de ferramentas de IA

- Ferramentas utilizadas: Claude (Anthropic).
- Tarefas em que ajudaram: planejamento do pipeline, geração e revisão do código de listagem de arquivos, chunking, geração de embeddings e busca por similaridade, depuração de erros de ambiente (venv, caminho longo do Windows/OneDrive), e estruturação deste README.
- Exemplo representativo de prompt ou orientação: pedido de ajuda para implementar um filtro que descartasse chunks sem conteúdo textual relevante, após observar que blocos vazios (símbolos/formatação) apareciam nos resultados de perguntas fora do escopo.
- O que foi testado, modificado ou validado por você: execução de cada script no VSCode, verificação da contagem de arquivos (23) e de chunks (332 após o filtro), teste manual das perguntas em modo interativo e via `--demo`, e validação de que os scores caem visivelmente em perguntas fora do escopo.

## Referências e código externo

- Documentação oficial do HTTPX: https://github.com/encode/httpx
- Biblioteca `sentence-transformers`: modelo `paraphrase-multilingual-MiniLM-L12-v2`

## Segurança

- [x] Minha solução não usa API key.
