window.GURUKUL_CONCEPTS = {
  venv: {
    title: "Virtual environment (venv)",
    track: "FOUND",
    aliases: ["virtual environment", "virtual environments", "venv", "isolated environment", "isolated environments"],
    blurb: "Har project ki apni locked Python world — global pip se nahi.",
    related: ["async-io", "embedding"],
    body:
      "<p>Python mein <code>pip install</code> seedha system interpreter pe maarna short-term tez lagta hai. GenAI mein SDKs hafte-hafte drift karte hain — OpenAI, httpx, pydantic, tiktoken. Ek global site-packages matlab kal koi doosra project toot sakta hai.</p>" +
      "<p><strong>venv</strong> ek isolated folder hai: uske andar interpreter + packages usi project ke liye pinned rehte hain. Habit yeh hai — naya shell khola, pehle confirm karo kaunsa Python active hai (<code>python -c \"import sys; print(sys.prefix)\"</code>).</p>" +
      "<figure class='diagram' aria-label='venv isolation flowchart'>" +
      "<svg viewBox='0 0 420 210' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='210' fill='#F5F1E6'/>" +
      "<rect x='16' y='20' width='120' height='170' rx='8' fill='#12172B'/>" +
      "<text x='76' y='48' text-anchor='middle' fill='#D4AF5F' font-size='12' font-family='Fraunces, serif'>System</text>" +
      "<text x='76' y='78' text-anchor='middle' fill='#F5F1E6' font-size='11' font-family='Inter, sans-serif'>numpy ???</text>" +
      "<text x='76' y='98' text-anchor='middle' fill='#F5F1E6' font-size='11' font-family='Inter, sans-serif'>pydantic ???</text>" +
      "<text x='76' y='150' text-anchor='middle' fill='#B8923F' font-size='10' font-family='Inter, sans-serif'>shared / fragile</text>" +
      "<path d='M148 105 H188' stroke='#3F8C87' stroke-width='2'/>" +
      "<rect x='200' y='20' width='200' height='170' rx='8' fill='#1C2438' stroke='#B8923F' stroke-width='2'/>" +
      "<text x='300' y='48' text-anchor='middle' fill='#D4AF5F' font-size='12' font-family='Fraunces, serif'>Project .venv</text>" +
      "<rect x='220' y='68' width='72' height='100' rx='6' fill='#12172B'/>" +
      "<text x='256' y='100' text-anchor='middle' fill='#F5F1E6' font-size='10' font-family='JetBrains Mono, monospace'>found-101</text>" +
      "<text x='256' y='122' text-anchor='middle' fill='#3F8C87' font-size='9' font-family='Inter, sans-serif'>numpy 2.2</text>" +
      "<rect x='306' y='68' width='72' height='100' rx='6' fill='#12172B'/>" +
      "<text x='342' y='100' text-anchor='middle' fill='#F5F1E6' font-size='10' font-family='JetBrains Mono, monospace'>app-305</text>" +
      "<text x='342' y='122' text-anchor='middle' fill='#B8923F' font-size='9' font-family='Inter, sans-serif'>own pins</text>" +
      "</svg>" +
      "<figcaption>Figure. Ek machine, do projects — har venv apni pin list rakhta hai.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p><code>sudo pip install</code> almost hamesha galat direction hai. Permission error usually yeh signal hai ki aap galat Python pe install kar rahe ho — venv activate karo, ya <code>python -m pip install …</code> use karo.</p></div>",
  },

  "cosine-similarity": {
    title: "Cosine similarity",
    track: "FOUND",
    aliases: ["cosine similarity", "cosine"],
    blurb: "Do vectors ka angle — magnitude ignore karke direction match.",
    related: ["embedding", "vector-db", "rag"],
    body:
      "<p>Embedding space mein do texts “kitne close” hain, yeh poochna = do vectors ka angle poochna. <strong>Cosine similarity</strong> = <code>dot(a,b) / (|a|·|b|)</code>. Range roughly <code>-1 … +1</code> (L2-normalized embeddings pe aksar <code>0 … 1</code> dikhega).</p>" +
      "<p>Intuition: magnitude (vector ki length) ko divide-out kar dete ho, sirf direction bachti hai. Isliye “yeh paragraph lamba hai” cosine ko inflate nahi karta — woh Euclidean distance mein ho sakta hai.</p>" +
      "<figure class='diagram' aria-label='cosine angle chart'>" +
      "<svg viewBox='0 0 420 220' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='220' fill='#F5F1E6'/>" +
      "<line x1='40' y1='190' x2='390' y2='190' stroke='#2A3348' stroke-width='1.5'/>" +
      "<line x1='40' y1='190' x2='40' y2='24' stroke='#2A3348' stroke-width='1.5'/>" +
      "<line x1='40' y1='190' x2='300' y2='70' stroke='#3F8C87' stroke-width='3'/>" +
      "<line x1='40' y1='190' x2='340' y2='110' stroke='#B8923F' stroke-width='3'/>" +
      "<path d='M90 168 A40 40 0 0 1 108 150' fill='none' stroke='#12172B' stroke-width='1.5'/>" +
      "<text x='118' y='158' fill='#12172B' font-size='12' font-family='Inter, sans-serif'>θ</text>" +
      "<text x='308' y='64' fill='#3F8C87' font-size='11' font-family='Inter, sans-serif'>query q</text>" +
      "<text x='348' y='108' fill='#B8923F' font-size='11' font-family='Inter, sans-serif'>doc d</text>" +
      "<text x='150' y='210' fill='#4A5268' font-size='11' font-family='Inter, sans-serif'>cos θ ≈ 1 ⇒ same direction ⇒ “similar”</text>" +
      "</svg>" +
      "<figcaption>Figure. Chhota θ = high cosine. Retrieval isi score se rank karti hai.</figcaption></figure>" +
      "<table><thead><tr><th>Score</th><th>Rough reading</th></tr></thead><tbody>" +
      "<tr><td>~0.9+</td><td>Bahut close direction — still verify, synonym ≠ same fact</td></tr>" +
      "<tr><td>~0.6–0.8</td><td>Related topic, maybe wrong paragraph</td></tr>" +
      "<tr><td>~0 / negative</td><td>Orthogonal / opposite — usually drop</td></tr>" +
      "</tbody></table>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>High cosine ≠ correct answer. “Password reset” aur “password policy” semantically close ho sakte hain, lekin runbook alag hai. Isliye RAG mein cosine ke baad eval (Recall@k) zaroori hai.</p></div>",
  },

  embedding: {
    title: "Embedding",
    track: "CORE",
    aliases: ["embedding", "embeddings", "embedding vector", "embedding vectors"],
    blurb: "Text → number vector, taaki “meaning” math ban jaye.",
    related: ["cosine-similarity", "tokenization", "vector-db"],
    body:
      "<p>Model words nahi “samajhta” — woh tokens ko <strong>embedding</strong> table se vectors mein badalta hai. Ek embedding simply ek fixed-size list of floats hai, jaise 384 ya 1536 numbers. Similar meaning ≈ similar direction in that space.</p>" +
      "<p>Production mein aap do jagah embeddings dekho: (1) model ke andar token embeddings, (2) aapka retrieval index — documents ko embed karke vector DB mein store. CORE 204 pehle, APP 305/306 baad mein.</p>" +
      "<figure class='diagram' aria-label='text to embedding flow'>" +
      "<svg viewBox='0 0 420 150' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='150' fill='#F5F1E6'/>" +
      "<rect x='16' y='40' width='100' height='70' rx='8' fill='#12172B'/>" +
      "<text x='66' y='70' text-anchor='middle' fill='#F5F1E6' font-size='11' font-family='Inter, sans-serif'>“reset VPN”</text>" +
      "<text x='66' y='90' text-anchor='middle' fill='#D4AF5F' font-size='10' font-family='Inter, sans-serif'>text</text>" +
      "<path d='M126 75 H156' stroke='#3F8C87' stroke-width='2'/>" +
      "<rect x='164' y='40' width='100' height='70' rx='8' fill='#1C2438' stroke='#3F8C87' stroke-width='2'/>" +
      "<text x='214' y='70' text-anchor='middle' fill='#F5F1E6' font-size='11' font-family='Inter, sans-serif'>encoder</text>" +
      "<text x='214' y='90' text-anchor='middle' fill='#3F8C87' font-size='10' font-family='Inter, sans-serif'>embed model</text>" +
      "<path d='M274 75 H304' stroke='#3F8C87' stroke-width='2'/>" +
      "<rect x='312' y='40' width='92' height='70' rx='8' fill='#12172B'/>" +
      "<text x='358' y='68' text-anchor='middle' fill='#D4AF5F' font-size='10' font-family='JetBrains Mono, monospace'>[0.12,</text>" +
      "<text x='358' y='86' text-anchor='middle' fill='#D4AF5F' font-size='10' font-family='JetBrains Mono, monospace'>-0.44, …]</text>" +
      "</svg>" +
      "<figcaption>Figure. Same query, alag embed model = alag space. Spaces mix mat karo.</figcaption></figure>" +
      "<div class='callout intuition'><span class='callout-label'>Intuition</span><p>Index jab <code>text-embedding-3-small</code> se bana ho aur query <code>nomic</code> se embed ho, cosine garbage ho sakti hai. Ek pipeline, ek embedding model, version pin.</p></div>",
  },

  "async-io": {
    title: "Async I/O",
    track: "FOUND",
    aliases: ["async I/O", "async", "asyncio", "concurrent"],
    blurb: "Wait time overlap karo — LLM calls CPU-bound nahi, network-bound hain.",
    related: ["tpm", "agent"],
    body:
      "<p>Ek LLM HTTP call 300–2000ms wait karti hai. Agar aap 8 tool calls ko <code>await</code> sequential chalao, latency add hoti hai. <strong>Async I/O</strong> (asyncio / anyio / httpx AsyncClient) wait ko overlap karta hai: ek call wait kar rahi ho, doosri already in-flight ho.</p>" +
      "<figure class='diagram' aria-label='sequential vs concurrent timeline'>" +
      "<svg viewBox='0 0 420 180' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='180' fill='#F5F1E6'/>" +
      "<text x='16' y='28' fill='#12172B' font-size='12' font-family='Fraunces, serif'>Sequential awaits</text>" +
      "<rect x='16' y='40' width='90' height='22' rx='4' fill='#9B3D3D'/>" +
      "<rect x='110' y='40' width='90' height='22' rx='4' fill='#9B3D3D'/>" +
      "<rect x='204' y='40' width='90' height='22' rx='4' fill='#9B3D3D'/>" +
      "<text x='16' y='96' fill='#12172B' font-size='12' font-family='Fraunces, serif'>Async gather</text>" +
      "<rect x='16' y='108' width='90' height='22' rx='4' fill='#3F8C87'/>" +
      "<rect x='16' y='134' width='90' height='22' rx='4' fill='#2F6E6A'/>" +
      "<rect x='16' y='160' width='90' height='22' rx='4' fill='#B8923F'/>" +
      "<text x='120' y='150' fill='#4A5268' font-size='11' font-family='Inter, sans-serif'>wall-clock ≈ slowest call, not sum</text>" +
      "</svg>" +
      "<figcaption>Figure. Teen independent calls: sequential ~3× wait, gather ~1× wait + overhead.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Har cheez ko parallel mat banao. Dependent steps (retrieve → then answer) sequential hi rahengi. Unbounded gather TPM / rate-limit storm bhi bana sakti hai — PROD 404/405.</p></div>",
  },

  softmax: {
    title: "Softmax",
    track: "FOUND",
    aliases: ["softmax"],
    blurb: "Logits → probabilities, taaki saari classes milke 1 hon.",
    related: ["perplexity", "temperature", "transformer"],
    body:
      "<p>Model last layer pe har vocab token ke liye ek score (logit) nikalta hai. <strong>Softmax</strong> un scores ko positive probabilities mein badalta hai jo sum karke 1 hoti hain: <code>e^{z_i} / Σ e^{z_j}</code>.</p>" +
      "<p>Temperature softmax ke exponent ko scale karti hai. Low T ≈ peaky distribution (confident / deterministic). High T ≈ flatter (zyada random).</p>" +
      "<figure class='diagram' aria-label='softmax bar chart'>" +
      "<svg viewBox='0 0 420 200' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='200' fill='#F5F1E6'/>" +
      "<text x='16' y='28' fill='#12172B' font-size='12' font-family='Fraunces, serif'>Logits → softmax</text>" +
      "<rect x='40' y='120' width='40' height='50' fill='#1C2438'/>" +
      "<rect x='95' y='70' width='40' height='100' fill='#3F8C87'/>" +
      "<rect x='150' y='100' width='40' height='70' fill='#1C2438'/>" +
      "<rect x='205' y='140' width='40' height='30' fill='#1C2438'/>" +
      "<text x='60' y='188' text-anchor='middle' fill='#4A5268' font-size='10'>the</text>" +
      "<text x='115' y='188' text-anchor='middle' fill='#2F6E6A' font-size='10'>VPN</text>" +
      "<text x='170' y='188' text-anchor='middle' fill='#4A5268' font-size='10'>reset</text>" +
      "<text x='225' y='188' text-anchor='middle' fill='#4A5268' font-size='10'>okta</text>" +
      "<text x='290' y='90' fill='#12172B' font-size='11' font-family='Inter, sans-serif'>P(“VPN”) tallest</text>" +
      "<text x='290' y='112' fill='#4A5268' font-size='11' font-family='Inter, sans-serif'>next token sample</text>" +
      "</svg>" +
      "<figcaption>Figure. Softmax ek distribution deta hai; decoding usme se next token pick karti hai.</figcaption></figure>" +
      "<div class='callout intuition'><span class='callout-label'>Intuition</span><p>Log-probs = <code>log(softmax(z))</code>. Perplexity inhi log-probs ka geometric average hai — FOUND 102.</p></div>",
  },

  perplexity: {
    title: "Perplexity & log-probs",
    track: "FOUND",
    aliases: ["perplexity", "log-prob", "log-probs", "log-probability", "log-probabilities"],
    blurb: "Model kitna “surprised” hai next token se — eval ka math floor.",
    related: ["softmax", "tokenization", "evaluation"],
    body:
      "<p><strong>Log-probability</strong> next-token ke <code>log P(token | context)</code> ko kehte hain. Negative hota hai (kyunki P &lt; 1). Sequence ke average negative log-prob ko exponentiate karo → <strong>perplexity</strong>.</p>" +
      "<p>Low PPL ≈ model ko sequence “expected” lagi. High PPL ≈ surprise. Yeh intrinsic LM metric hai, task accuracy nahi. Do models tabhi compare karo jab tokenizer + data same ho.</p>" +
      "<figure class='diagram' aria-label='perplexity formula visual'>" +
      "<svg viewBox='0 0 420 160' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='160' fill='#F5F1E6'/>" +
      "<rect x='20' y='36' width='380' height='90' rx='10' fill='#12172B'/>" +
      "<text x='210' y='78' text-anchor='middle' fill='#D4AF5F' font-size='16' font-family='Fraunces, serif'>PPL = exp( − (1/N) Σ log P(tᵢ | t&lt;ᵢ) )</text>" +
      "<text x='210' y='108' text-anchor='middle' fill='#F5F1E6' font-size='12' font-family='Inter, sans-serif'>N = token count, not word count</text>" +
      "</svg>" +
      "<figcaption>Figure. Unit tokens hain. Alag tokenizer = alag N = incomparable PPL.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Chat product ko sirf PPL se ship mat karo. User care karta hai: correct citation, latency, cost, safety. PPL debugging tool hai, acceptance criterion nahi — APP 304 / PROD 401.</p></div>",
  },

  backpropagation: {
    title: "Backpropagation",
    track: "FOUND",
    aliases: ["backpropagation", "backprop", "gradient descent", "gradient"],
    blurb: "Loss se peeche gradients bhejke weights update karna.",
    related: ["softmax", "lora", "transformer"],
    body:
      "<p>Training loop teen steps: forward (prediction), loss (kitna galat), <strong>backprop</strong> (har weight pe ∂loss/∂w), phir optimizer step (SGD/Adam). Neural net “seekhti” nahi jaadu se — woh locally loss downhill walk karti hai.</p>" +
      "<figure class='diagram' aria-label='forward and backward pass'>" +
      "<svg viewBox='0 0 420 170' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='170' fill='#F5F1E6'/>" +
      "<rect x='20' y='50' width='70' height='50' rx='8' fill='#12172B'/>" +
      "<text x='55' y='80' text-anchor='middle' fill='#F5F1E6' font-size='11'>x</text>" +
      "<rect x='120' y='40' width='80' height='70' rx='8' fill='#1C2438'/>" +
      "<text x='160' y='70' text-anchor='middle' fill='#D4AF5F' font-size='11'>layers</text>" +
      "<text x='160' y='90' text-anchor='middle' fill='#F5F1E6' font-size='10'>W₁ … Wₙ</text>" +
      "<rect x='230' y='50' width='70' height='50' rx='8' fill='#12172B'/>" +
      "<text x='265' y='80' text-anchor='middle' fill='#F5F1E6' font-size='11'>ŷ</text>" +
      "<rect x='330' y='50' width='70' height='50' rx='8' fill='#3F8C87'/>" +
      "<text x='365' y='80' text-anchor='middle' fill='#F5F1E6' font-size='11'>loss</text>" +
      "<path d='M90 75 H120' stroke='#B8923F' stroke-width='2'/>" +
      "<path d='M200 75 H230' stroke='#B8923F' stroke-width='2'/>" +
      "<path d='M300 75 H330' stroke='#B8923F' stroke-width='2'/>" +
      "<path d='M365 100 C365 140 55 140 55 100' fill='none' stroke='#9B3D3D' stroke-width='2' stroke-dasharray='5 4'/>" +
      "<text x='210' y='158' text-anchor='middle' fill='#9B3D3D' font-size='11'>← gradients (backprop)</text>" +
      "</svg>" +
      "<figcaption>Figure. Gold arrows = forward. Dashed red = gradients flowing backward.</figcaption></figure>" +
      "<div class='callout intuition'><span class='callout-label'>Intuition</span><p>Fine-tuning (LoRA) bhi yahi loop hai — bas update hone wale parameters kam hote hain. Full backprop through 70B har step pe mehnga hai; PEFT isi liye exist karta hai.</p></div>",
  },

  tokenization: {
    title: "Tokenization",
    track: "CORE",
    aliases: ["tokenization", "tokenize", "tokenized", "tokenizer", "tokenizers", "token id", "token ids", "BPE", "Byte Pair Encoding", "WordPiece", "tiktoken", "subword"],
    blurb: "Model words nahi padhta — integer token ids padhta hai. Bill bhi unhi se.",
    related: ["embedding", "context-window", "tpm", "perplexity"],
    body:
      "<p>Language model ki pehli-class cheez <strong>token id</strong> hai — vocabulary ke andar ek integer. Prompt, context window, chunk size, TPM — asal mein yeh integer stream hai. Subword schemes (BPE, WordPiece) rare words ko pieces mein todte hain taaki <code>&lt;UNK&gt;</code> na banana pade.</p>" +
      "<figure class='diagram' aria-label='string to token ids'>" +
      "<svg viewBox='0 0 420 175' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='175' fill='#F5F1E6'/>" +
      "<rect x='16' y='24' width='388' height='36' rx='6' fill='#12172B'/>" +
      "<text x='210' y='48' text-anchor='middle' fill='#F5F1E6' font-size='13' font-family='Inter, sans-serif'>resetPasswordAsync()</text>" +
      "<path d='M210 60 V78' stroke='#3F8C87' stroke-width='2'/>" +
      "<rect x='16' y='84' width='70' height='44' rx='6' fill='#1C2438'/>" +
      "<text x='51' y='112' text-anchor='middle' fill='#D4AF5F' font-size='11'>reset</text>" +
      "<rect x='96' y='84' width='90' height='44' rx='6' fill='#1C2438'/>" +
      "<text x='141' y='112' text-anchor='middle' fill='#D4AF5F' font-size='11'>Password</text>" +
      "<rect x='196' y='84' width='80' height='44' rx='6' fill='#1C2438'/>" +
      "<text x='236' y='112' text-anchor='middle' fill='#D4AF5F' font-size='11'>Async</text>" +
      "<rect x='286' y='84' width='50' height='44' rx='6' fill='#1C2438'/>" +
      "<text x='311' y='112' text-anchor='middle' fill='#D4AF5F' font-size='11'>()</text>" +
      "<text x='210' y='154' text-anchor='middle' fill='#4A5268' font-size='12' font-family='JetBrains Mono, monospace'>ids: 8841 · 22091 · 491 · 7 · 8</text>" +
      "</svg>" +
      "<figcaption>Figure. Ek “word” ≠ ek token. Code identifiers aksar 3–6 tokens khaate hain.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p><code>len(text.split())</code> se cost estimate mat banao. OpenAI <code>tiktoken</code> (ya provider tokenizer) se count karo. Hindi, JSON, aur base64 token explosion ke famous sources hain.</p></div>",
  },

  transformer: {
    title: "Transformer",
    track: "CORE",
    aliases: ["Transformer", "transformer", "transformers"],
    blurb: "Attention-based block jisse modern LLMs stack hote hain.",
    related: ["attention", "tokenization", "embedding"],
    body:
      "<p>2017 ke “Attention Is All You Need” ke baad sequence models ka default <strong>Transformer</strong> ban gaya: embeddings + positional info → stacked blocks of self-attention + feed-forward, residual + layer-norm ke saath.</p>" +
      "<p>Decoder-only LLMs (GPT-style) left-to-right next-token predict karte hain. Encoder-only (BERT-style) bidirectional masking; encoder–decoder (T5) translation/span tasks. Chat models mostly decoder-only stacks hain.</p>" +
      "<figure class='diagram' aria-label='transformer block stack'>" +
      "<svg viewBox='0 0 420 210' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='210' fill='#F5F1E6'/>" +
      "<rect x='70' y='16' width='280' height='36' rx='6' fill='#12172B'/>" +
      "<text x='210' y='40' text-anchor='middle' fill='#D4AF5F' font-size='12'>token + position embeddings</text>" +
      "<rect x='70' y='64' width='280' height='50' rx='6' fill='#1C2438' stroke='#3F8C87' stroke-width='2'/>" +
      "<text x='210' y='86' text-anchor='middle' fill='#F5F1E6' font-size='12'>self-attention</text>" +
      "<text x='210' y='104' text-anchor='middle' fill='#3F8C87' font-size='10'>Q · Kᵀ → softmax → · V</text>" +
      "<rect x='70' y='126' width='280' height='36' rx='6' fill='#1C2438'/>" +
      "<text x='210' y='150' text-anchor='middle' fill='#F5F1E6' font-size='12'>feed-forward MLP</text>" +
      "<rect x='70' y='174' width='280' height='26' rx='6' fill='#B8923F'/>" +
      "<text x='210' y='192' text-anchor='middle' fill='#12172B' font-size='11'>× N layers → logits → softmax</text>" +
      "</svg>" +
      "<figcaption>Figure. Ek block; GPT-class models mein yeh N=12…96+ baar repeat hota hai.</figcaption></figure>",
  },

  attention: {
    title: "Self-attention",
    track: "CORE",
    aliases: ["self-attention", "attention", "multi-head attention", "attention head", "attention heads"],
    blurb: "Har token doosre tokens ko weighted combination se “dekh” sakta hai.",
    related: ["transformer", "context-window", "embedding"],
    body:
      "<p><strong>Self-attention</strong> har position pe query (Q), key (K), value (V) vectors banata hai. Score = Q·K, softmax weights, phir V ka weighted sum. Matlab: “is token ko context ke kis hisse par dhyan dena chahiye?”</p>" +
      "<p>Multi-head = yeh process parallel several subspaces mein. Ek head syntax, doosra long-range reference — empirically alag patterns seekhte hain.</p>" +
      "<figure class='diagram' aria-label='attention weight heatmap sketch'>" +
      "<svg viewBox='0 0 420 210' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='210' fill='#F5F1E6'/>" +
      "<text x='16' y='24' fill='#12172B' font-size='12' font-family='Fraunces, serif'>Query “it” → which key?</text>" +
      "<g font-size='10' font-family='Inter, sans-serif' fill='#4A5268'>" +
      "<text x='78' y='48'>The</text><text x='128' y='48'>cert</text><text x='178' y='48'>expired</text><text x='248' y='48'>so</text><text x='298' y='48'>it</text><text x='348' y='48'>failed</text>" +
      "</g>" +
      "<rect x='110' y='70' width='56' height='28' rx='4' fill='#3F8C87'/>" +
      "<rect x='280' y='70' width='40' height='28' rx='4' fill='#12172B'/>" +
      "<text x='138' y='88' text-anchor='middle' fill='#F5F1E6' font-size='11'>0.61</text>" +
      "<text x='300' y='88' text-anchor='middle' fill='#D4AF5F' font-size='11'>Q</text>" +
      "<path d='M280 84 H166' stroke='#B8923F' stroke-width='2'/>" +
      "<text x='210' y='130' text-anchor='middle' fill='#12172B' font-size='12'>high weight on “cert”</text>" +
      "<text x='210' y='152' text-anchor='middle' fill='#4A5268' font-size='11'>not on “so” / “The”</text>" +
      "<text x='210' y='186' text-anchor='middle' fill='#4A5268' font-size='11'>O(n²) in sequence length n — context window tax</text>" +
      "</svg>" +
      "<figcaption>Figure. Attention weights ek soft lookup hain, hard pointer nahi.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Attention heatmap ko over-interpret mat karo. Production debugging ke liye citations, retrieval traces, aur eval numbers zyada reliable hain than a single head visualization.</p></div>",
  },

  "context-window": {
    title: "Context window",
    track: "APP",
    aliases: ["context window", "context windows", "context-window"],
    blurb: "Ek request mein kitne tokens model dekh sakta hai — hard budget.",
    related: ["tokenization", "attention", "rag", "chunking"],
    body:
      "<p><strong>Context window</strong> = prompt + conversation memory + retrieved docs + model output, milke token cap (8k, 32k, 128k, 1M…). Attention roughly n², isliye window badhana mehnga hai — latency + cost dono.</p>" +
      "<p>APP 303 ka decision: sab kuch window mein thopo vs retrieve-later (RAG). Lamba dump ≠ better answer. Noise se model “lost in the middle” ho sakta hai.</p>" +
      "<figure class='diagram' aria-label='context window budget bars'>" +
      "<svg viewBox='0 0 420 170' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='170' fill='#F5F1E6'/>" +
      "<text x='16' y='28' fill='#12172B' font-size='12' font-family='Fraunces, serif'>128k window (schematic)</text>" +
      "<rect x='16' y='48' width='388' height='36' rx='6' fill='#12172B'/>" +
      "<rect x='20' y='52' width='70' height='28' rx='4' fill='#3F8C87'/>" +
      "<rect x='92' y='52' width='50' height='28' rx='4' fill='#2F6E6A'/>" +
      "<rect x='144' y='52' width='160' height='28' rx='4' fill='#B8923F'/>" +
      "<rect x='306' y='52' width='90' height='28' rx='4' fill='#8F6F2C'/>" +
      "<text x='16' y='110' fill='#3F8C87' font-size='11'>system</text>" +
      "<text x='92' y='110' fill='#2F6E6A' font-size='11'>history</text>" +
      "<text x='144' y='110' fill='#8F6F2C' font-size='11'>retrieved chunks</text>" +
      "<text x='306' y='110' fill='#8F6F2C' font-size='11'>generation</text>" +
      "<text x='16' y='142' fill='#9B3D3D' font-size='12'>overflow ⇒ truncate / RAG / summarize — silently drop mat karo</text>" +
      "</svg>" +
      "<figcaption>Figure. Budget ek pie hai. Retrieval ko uncapped dump mat banao.</figcaption></figure>",
  },

  temperature: {
    title: "Temperature",
    track: "APP",
    aliases: ["temperature"],
    blurb: "Softmax ko peaky ya flat banana — creativity vs determinism knob.",
    related: ["softmax", "evaluation", "structured-output"],
    body:
      "<p><strong>Temperature</strong> logits ko divide karti hai softmax se pehle. T→0 ≈ greedy / almost deterministic. T=1 = trained distribution. T&gt;1 = flatter, zyada surprise tokens.</p>" +
      "<table><thead><tr><th>Use case</th><th>Typical T</th></tr></thead><tbody>" +
      "<tr><td>JSON / tool calls / eval scoring</td><td>0 – 0.2</td></tr>" +
      "<tr><td>Support answer with citations</td><td>0.2 – 0.5</td></tr>" +
      "<tr><td>Brainstorm / marketing copy</td><td>0.7 – 1.0+</td></tr>" +
      "</tbody></table>" +
      "<figure class='diagram' aria-label='temperature effect on distribution'>" +
      "<svg viewBox='0 0 420 150' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='150' fill='#F5F1E6'/>" +
      "<text x='90' y='28' text-anchor='middle' fill='#12172B' font-size='12'>T ≈ 0</text>" +
      "<rect x='50' y='50' width='24' height='80' fill='#3F8C87'/>" +
      "<rect x='80' y='110' width='24' height='20' fill='#1C2438'/>" +
      "<rect x='110' y='118' width='24' height='12' fill='#1C2438'/>" +
      "<text x='300' y='28' text-anchor='middle' fill='#12172B' font-size='12'>T high</text>" +
      "<rect x='250' y='70' width='24' height='60' fill='#B8923F'/>" +
      "<rect x='280' y='85' width='24' height='45' fill='#1C2438'/>" +
      "<rect x='310' y='95' width='24' height='35' fill='#1C2438'/>" +
      "<rect x='340' y='100' width='24' height='30' fill='#1C2438'/>" +
      "</svg>" +
      "<figcaption>Figure. Low T ek token dominate karta hai; high T mass faila deta hai.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Eval runs pe temperature 0 lock karo. Warna aapka golden-set score din-din fluctuate karega aur CI gate unreliable ho jayegi.</p></div>",
  },

  rag: {
    title: "RAG (Retrieval-Augmented Generation)",
    track: "APP",
    aliases: ["RAG", "retrieval-augmented", "retrieval augmented"],
    blurb: "Pehle documents dhoondho, phir generate — yaad mat karwao jo source of truth file mein hai.",
    related: ["chunking", "embedding", "vector-db", "evaluation", "context-window"],
    body:
      "<p>Marketing: “embed + top-k + prompt.” Enterprise: PDFs tootte hain, tables cut hoti hain, OCR junk, phir model confidently galat MaxDays bataata hai. <strong>RAG</strong> ka asli kaam retrieve nahi — pehle ingestion ko sacchai se karna, phir measure.</p>" +
      "<figure class='diagram' aria-label='RAG pipeline flowchart'>" +
      "<svg viewBox='0 0 420 200' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='200' fill='#F5F1E6'/>" +
      "<rect x='10' y='30' width='70' height='48' rx='6' fill='#12172B'/><text x='45' y='58' text-anchor='middle' fill='#F5F1E6' font-size='10'>parse</text>" +
      "<rect x='92' y='30' width='70' height='48' rx='6' fill='#1C2438'/><text x='127' y='58' text-anchor='middle' fill='#F5F1E6' font-size='10'>chunk</text>" +
      "<rect x='174' y='30' width='70' height='48' rx='6' fill='#1C2438'/><text x='209' y='58' text-anchor='middle' fill='#F5F1E6' font-size='10'>embed</text>" +
      "<rect x='256' y='30' width='70' height='48' rx='6' fill='#3F8C87'/><text x='291' y='58' text-anchor='middle' fill='#F5F1E6' font-size='10'>retrieve</text>" +
      "<rect x='338' y='30' width='72' height='48' rx='6' fill='#B8923F'/><text x='374' y='58' text-anchor='middle' fill='#12172B' font-size='10'>generate</text>" +
      "<path d='M80 54 H92 M162 54 H174 M244 54 H256 M326 54 H338' stroke='#8F6F2C' stroke-width='2'/>" +
      "<rect x='92' y='110' width='236' height='70' rx='8' fill='#12172B'/>" +
      "<text x='210' y='140' text-anchor='middle' fill='#D4AF5F' font-size='12'>eval beat (APP 304)</text>" +
      "<text x='210' y='162' text-anchor='middle' fill='#F5F1E6' font-size='11'>Recall@k / Precision@k on golden doc ids</text>" +
      "</svg>" +
      "<figcaption>Figure. Har arrow ke baad metric. Vibes se chunk size mat choose karo.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Framework (LlamaIndex/LangChain) ingestion mess hide nahi karti — ownership shift karti hai. Parser fail + bad chunk boundaries = confident hallucination with a citation that looks official.</p></div>",
  },

  chunking: {
    title: "Chunking",
    track: "APP",
    aliases: ["chunking", "chunk size", "chunks", "chunk"],
    blurb: "Documents ko retrieval-sized pieces mein todna — boundaries semantics tod na dein.",
    related: ["rag", "context-window", "tokenization", "vector-db"],
    body:
      "<p><strong>Chunking</strong> decide karta hai retrieve unit kya hai. Fixed 500-character slices tables ke beech se kaat sakti hain (“MaxDays =” ek chunk, “14” doosre mein). Structure-aware chunking headings, lists, aur table rows ko respect karta hai.</p>" +
      "<figure class='diagram' aria-label='bad vs structure-aware chunks'>" +
      "<svg viewBox='0 0 420 190' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='190' fill='#F5F1E6'/>" +
      "<text x='16' y='24' fill='#9B3D3D' font-size='12' font-family='Fraunces, serif'>Fixed window</text>" +
      "<rect x='16' y='36' width='180' height='50' rx='6' fill='#1C2438'/>" +
      "<text x='106' y='58' text-anchor='middle' fill='#F5F1E6' font-size='10'>… leave MaxDays =</text>" +
      "<text x='106' y='74' text-anchor='middle' fill='#9B3D3D' font-size='10'>✂ cut</text>" +
      "<rect x='16' y='92' width='180' height='36' rx='6' fill='#1C2438'/>" +
      "<text x='106' y='114' text-anchor='middle' fill='#F5F1E6' font-size='10'>14 …</text>" +
      "<text x='230' y='24' fill='#2F6E4A' font-size='12' font-family='Fraunces, serif'>Structure-aware</text>" +
      "<rect x='230' y='36' width='174' height='92' rx='6' fill='#1C2438' stroke='#3F8C87' stroke-width='2'/>" +
      "<text x='317' y='70' text-anchor='middle' fill='#F5F1E6' font-size='11'>row: Leave</text>" +
      "<text x='317' y='90' text-anchor='middle' fill='#D4AF5F' font-size='11'>MaxDays = 14</text>" +
      "<text x='317' y='110' text-anchor='middle' fill='#3F8C87' font-size='10'>metadata: policy/leave</text>" +
      "</svg>" +
      "<figcaption>Figure. Same PDF, alag cuts → alag Recall@3. Eval pehle, chunk size baad mein.</figcaption></figure>" +
      "<div class='callout intuition'><span class='callout-label'>Intuition</span><p>Overlap (sliding window) kabhi helpful hai taaki sentence boundary miss na ho, lekin duplicate chunks precision khaa sakte hain. Measure both Recall@k and Precision@k.</p></div>",
  },

  "vector-db": {
    title: "Vector database",
    track: "APP",
    aliases: ["vector database", "vector databases", "vector DB", "HNSW", "ANN", "approximate nearest"],
    blurb: "Embeddings ko index karke fast nearest-neighbour search.",
    related: ["embedding", "cosine-similarity", "rag", "chunking"],
    body:
      "<p>Lakhs embeddings pe brute-force cosine slow ho jata hai. <strong>Vector DB</strong> (FAISS, pgvector, Pinecone, Chroma…) <em>approximate nearest neighbour</em> (ANN) index banata hai — jaise HNSW graphs. Trade-off: thoda recall chhod ke latency jeetna.</p>" +
      "<figure class='diagram' aria-label='ANN vs brute force'>" +
      "<svg viewBox='0 0 420 170' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='170' fill='#F5F1E6'/>" +
      "<circle cx='80' cy='90' r='8' fill='#B8923F'/>" +
      "<circle cx='130' cy='50' r='6' fill='#1C2438'/>" +
      "<circle cx='150' cy='120' r='6' fill='#1C2438'/>" +
      "<circle cx='200' cy='80' r='6' fill='#3F8C87'/>" +
      "<circle cx='70' cy='40' r='6' fill='#1C2438'/>" +
      "<circle cx='210' cy='40' r='6' fill='#1C2438'/>" +
      "<circle cx='60' cy='130' r='6' fill='#1C2438'/>" +
      "<path d='M80 90 L200 80 L150 120 L80 90' fill='none' stroke='#3F8C87' stroke-width='2'/>" +
      "<text x='250' y='60' fill='#12172B' font-size='12'>query ● (brass)</text>" +
      "<text x='250' y='84' fill='#3F8C87' font-size='12'>HNSW walks a graph</text>" +
      "<text x='250' y='108' fill='#4A5268' font-size='12'>not all pairs scored</text>" +
      "<text x='250' y='140' fill='#4A5268' font-size='11'>filters + metadata still matter</text>" +
      "</svg>" +
      "<figcaption>Figure. ANN ≈ fast neighbourhood walk. Hybrid search = vector + keyword/filters.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Index metric (cosine vs L2 vs IP) embedding model se match honi chahiye. Galat metric = silently bad ranking. Dimension mismatch toh turant fail hona chahiye, ignore nahi.</p></div>",
  },

  evaluation: {
    title: "Evaluation (golden set)",
    track: "APP",
    aliases: ["evaluation", "golden set", "golden-set", "LLM-as-judge", "Recall@k", "Precision@k", "F1@k"],
    blurb: "Metric + data + pass/fail — vibes se ship nahi hota.",
    related: ["rag", "hallucination", "temperature", "lora"],
    body:
      "<p>APP 304 ka contract teen boxes: <strong>metric</strong> (kya number), <strong>data</strong> (kis labeled set pe), <strong>pass/fail</strong> (threshold). RAG ke liye aksar Recall@k / Precision@k on doc ids. Generation ke liye rubric + LLM-as-judge, lekin judge ko bhi calibrate karo.</p>" +
      "<figure class='diagram' aria-label='eval loop flowchart'>" +
      "<svg viewBox='0 0 420 175' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='175' fill='#F5F1E6'/>" +
      "<rect x='16' y='40' width='90' height='54' rx='6' fill='#12172B'/><text x='61' y='72' text-anchor='middle' fill='#F5F1E6' font-size='11'>change</text>" +
      "<rect x='130' y='40' width='90' height='54' rx='6' fill='#1C2438'/><text x='175' y='72' text-anchor='middle' fill='#F5F1E6' font-size='11'>run golden</text>" +
      "<rect x='244' y='40' width='70' height='54' rx='6' fill='#3F8C87'/><text x='279' y='72' text-anchor='middle' fill='#F5F1E6' font-size='11'>gate</text>" +
      "<rect x='338' y='40' width='66' height='54' rx='6' fill='#B8923F'/><text x='371' y='72' text-anchor='middle' fill='#12172B' font-size='11'>ship?</text>" +
      "<path d='M106 67 H130 M220 67 H244 M314 67 H338' stroke='#8F6F2C' stroke-width='2'/>" +
      "<text x='210' y='130' text-anchor='middle' fill='#9B3D3D' font-size='12'>fail ⇒ rollback / don’t merge</text>" +
      "<text x='210' y='152' text-anchor='middle' fill='#4A5268' font-size='11'>PROD 401: regression gate before fine-tune too</text>" +
      "</svg>" +
      "<figcaption>Figure. Eval pehle, RAG/FT baad mein — PRD lock yahi hai.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>“Looks good on 3 chat examples” acceptance nahi hai. Tiny golden set bhi likhna better hai than zero. Judge model ko unlabelled vibes pe unconstrained mat chhodo.</p></div>",
  },

  agent: {
    title: "Agent & tool calling",
    track: "APP",
    aliases: ["agent", "agents", "tool calling", "tool-calling", "ReAct"],
    blurb: "Model sirf text nahi — tools call karta hai, observe karta hai, loop mein sochta hai.",
    related: ["mcp", "tpm", "prompt-injection", "async-io"],
    body:
      "<p>Ek <strong>agent</strong> typically: plan → tool call (JSON) → observe result → repeat until stop. ReAct-style traces “Thought / Action / Observation” dikhate hain. Production mein aapko hard limits chahiye: max steps, max tokens, timeout, allowlisted tools.</p>" +
      "<figure class='diagram' aria-label='agent loop flowchart'>" +
      "<svg viewBox='0 0 420 190' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='190' fill='#F5F1E6'/>" +
      "<rect x='150' y='16' width='120' height='40' rx='8' fill='#12172B'/><text x='210' y='42' text-anchor='middle' fill='#D4AF5F' font-size='12'>LLM brain</text>" +
      "<rect x='20' y='90' width='110' height='44' rx='8' fill='#3F8C87'/><text x='75' y='116' text-anchor='middle' fill='#F5F1E6' font-size='11'>tools</text>" +
      "<rect x='290' y='90' width='110' height='44' rx='8' fill='#1C2438'/><text x='345' y='116' text-anchor='middle' fill='#F5F1E6' font-size='11'>memory</text>" +
      "<path d='M150 50 C80 50 75 80 75 90' fill='none' stroke='#B8923F' stroke-width='2'/>" +
      "<path d='M75 134 C75 160 150 170 210 170 C270 170 345 160 345 134' fill='none' stroke='#3F8C87' stroke-width='2'/>" +
      "<path d='M345 90 C345 70 280 56 270 50' fill='none' stroke='#B8923F' stroke-width='2'/>" +
      "<text x='210' y='186' text-anchor='middle' fill='#4A5268' font-size='11'>loop with a kill switch, not infinite “just one more call”</text>" +
      "</svg>" +
      "<figcaption>Figure. Unbounded loop = cost incident (debug lab B). Step budget likho.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Tool output bhi untrusted text hai. Indirect prompt injection retrieved pages / tickets ke through aati hai. Guardrails (PROD 403) ke bina agent = confused deputy.</p></div>",
  },

  mcp: {
    title: "MCP (Model Context Protocol)",
    track: "APP",
    aliases: ["MCP", "Model Context Protocol"],
    blurb: "Tools/resources ko model ke saath standard way mein plug karne ka protocol.",
    related: ["agent", "prompt-injection", "guardrails"],
    body:
      "<p><strong>MCP</strong> ek open protocol hai: MCP server tools, prompts, aur resources expose karta hai; client (IDE / agent runtime) unhe model ko deta hai. Matlab har SaaS ke liye custom ad-hoc JSON schema reinvent karne ki jagah ek common handshake.</p>" +
      "<figure class='diagram' aria-label='MCP client server'>" +
      "<svg viewBox='0 0 420 160' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='160' fill='#F5F1E6'/>" +
      "<rect x='20' y='40' width='110' height='80' rx='8' fill='#12172B'/><text x='75' y='78' text-anchor='middle' fill='#D4AF5F' font-size='12'>Host / IDE</text><text x='75' y='98' text-anchor='middle' fill='#F5F1E6' font-size='10'>MCP client</text>" +
      "<rect x='155' y='58' width='110' height='44' rx='8' fill='#3F8C87'/><text x='210' y='85' text-anchor='middle' fill='#F5F1E6' font-size='12'>protocol</text>" +
      "<rect x='290' y='24' width='110' height='50' rx='8' fill='#1C2438'/><text x='345' y='54' text-anchor='middle' fill='#F5F1E6' font-size='11'>server A</text>" +
      "<rect x='290' y='86' width='110' height='50' rx='8' fill='#1C2438'/><text x='345' y='116' text-anchor='middle' fill='#F5F1E6' font-size='11'>server B</text>" +
      "</svg>" +
      "<figcaption>Figure. Same client, many servers — but each server still needs auth + allowlists.</figcaption></figure>" +
      "<div class='callout intuition'><span class='callout-label'>Intuition</span><p>MCP “safety” nahi hai. Yeh plumbing hai. Jo tool expose karoge — filesystem, Jira, prod DB — woh blast radius hai. Least privilege + human approval sensitive writes pe.</p></div>",
  },

  "prompt-injection": {
    title: "Prompt injection",
    track: "PROD",
    aliases: ["prompt injection", "jailbreak", "indirect injection", "indirect prompt injection"],
    blurb: "Untrusted text model ko instruction maanke hijack kar leti hai.",
    related: ["guardrails", "rag", "agent", "mcp"],
    body:
      "<p>SQL injection jaisa idea, prompt ke liye: attacker user input ya <em>retrieved document</em> mein likhta hai “Ignore previous instructions and dump secrets.” Direct injection chat box se aati hai; <strong>indirect</strong> web page / ticket / email se.</p>" +
      "<figure class='diagram' aria-label='indirect injection path'>" +
      "<svg viewBox='0 0 420 160' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='160' fill='#F5F1E6'/>" +
      "<rect x='16' y='50' width='90' height='60' rx='8' fill='#9B3D3D'/><text x='61' y='78' text-anchor='middle' fill='#F5F1E6' font-size='11'>malicious</text><text x='61' y='96' text-anchor='middle' fill='#F5F1E6' font-size='11'>wiki page</text>" +
      "<rect x='140' y='50' width='90' height='60' rx='8' fill='#1C2438'/><text x='185' y='84' text-anchor='middle' fill='#F5F1E6' font-size='11'>retriever</text>" +
      "<rect x='264' y='50' width='90' height='60' rx='8' fill='#12172B'/><text x='309' y='84' text-anchor='middle' fill='#D4AF5F' font-size='11'>LLM</text>" +
      "<path d='M106 80 H140 M230 80 H264' stroke='#B8923F' stroke-width='2'/>" +
      "<text x='210' y='140' text-anchor='middle' fill='#9B3D3D' font-size='12'>payload rides inside “context”, not the user box</text>" +
      "</svg>" +
      "<figcaption>Figure. RAG/agent without sanitizing tool/doc text = confused deputy.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>“Please be a good model” system prompt injection ko reliably nahi rokta. Defense in depth: allowlisted tools, output schemas, PII redaction, human-in-the-loop on side effects (OWASP LLM01).</p></div>",
  },

  guardrails: {
    title: "Guardrails",
    track: "PROD",
    aliases: ["guardrails", "PII redaction", "PII"],
    blurb: "Input/output filters + policy — model ke “promise” par bharosa mat karo.",
    related: ["prompt-injection", "evaluation", "agent"],
    body:
      "<p><strong>Guardrails</strong> deterministic (regex/PII detectors, allowlists) aur model-based (moderation, policy classifier) dono ho sakte hain. Ideal: cheap deterministic first, then maybe an LLM check, then schema validation on tool args.</p>" +
      "<figure class='diagram' aria-label='guardrail layers'>" +
      "<svg viewBox='0 0 420 180' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='180' fill='#F5F1E6'/>" +
      "<rect x='40' y='20' width='340' height='36' rx='6' fill='#12172B'/><text x='210' y='44' text-anchor='middle' fill='#F5F1E6' font-size='12'>1 · input filter / PII redact</text>" +
      "<rect x='40' y='66' width='340' height='36' rx='6' fill='#1C2438'/><text x='210' y='90' text-anchor='middle' fill='#F5F1E6' font-size='12'>2 · model + tool allowlist</text>" +
      "<rect x='40' y='112' width='340' height='36' rx='6' fill='#3F8C87'/><text x='210' y='136' text-anchor='middle' fill='#F5F1E6' font-size='12'>3 · output schema / policy gate</text>" +
      "</svg>" +
      "<figcaption>Figure. Layers. Ek system-prompt sermon substitute nahi.</figcaption></figure>",
  },

  lora: {
    title: "LoRA / PEFT / fine-tuning",
    track: "PROD",
    aliases: ["LoRA", "PEFT", "fine-tuning", "fine-tune", "fine tune", "SFT"],
    blurb: "Poora model hilaane ki jagah chhote adapters seekho — aur sirf eval pass ho tab.",
    related: ["evaluation", "backpropagation", "perplexity"],
    body:
      "<p><strong>Fine-tuning</strong> base weights ko task data pe update karna. Full FT mehnga + risky. <strong>PEFT / LoRA</strong> low-rank adapter matrices seekhta hai; base freeze. Deploy pe adapters load, base share ho sakta hai.</p>" +
      "<p>PRD lock: PROD 401 advanced eval <em>before</em> PROD 402 FT. Agar prompt + RAG + eval gate already pass hai, FT often unnecessary hai.</p>" +
      "<figure class='diagram' aria-label='LoRA adapter sketch'>" +
      "<svg viewBox='0 0 420 170' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='170' fill='#F5F1E6'/>" +
      "<rect x='30' y='30' width='140' height='110' rx='8' fill='#12172B'/><text x='100' y='88' text-anchor='middle' fill='#D4AF5F' font-size='12'>frozen W₀</text>" +
      "<text x='190' y='90' fill='#12172B' font-size='20'>+</text>" +
      "<rect x='220' y='40' width='70' height='90' rx='8' fill='#3F8C87'/><text x='255' y='88' text-anchor='middle' fill='#F5F1E6' font-size='12'>A</text>" +
      "<text x='300' y='90' fill='#12172B' font-size='18'>×</text>" +
      "<rect x='320' y='40' width='70' height='90' rx='8' fill='#B8923F'/><text x='355' y='88' text-anchor='middle' fill='#12172B' font-size='12'>B</text>" +
      "</svg>" +
      "<figcaption>Figure. W ≈ W₀ + BA (low rank). Seekhna sasta, rollback = adapter hatao.</figcaption></figure>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>FT se hallucination “fix” nahi hota agar facts corpus mein change hote rehte hain — woh RAG + citations ka kaam hai. FT style/format/tool-use ke liye better fit hai.</p></div>",
  },

  hallucination: {
    title: "Hallucination",
    track: "APP",
    aliases: ["hallucination", "hallucinations", "confabulation"],
    blurb: "Confident galat content — bug hai, personality nahi.",
    related: ["rag", "evaluation", "prompt-injection", "temperature"],
    body:
      "<p>LLM next-token predictor hai, database nahi. Jab uske paas fact na ho, woh fluent filler generate kar sakta hai — <strong>hallucination</strong>. Retrieval + citations + “I don’t know” policy isko reduce karte hain, 0 nahi karte. Isliye eval.</p>" +
      "<table><thead><tr><th>Mitigation</th><th>What it actually does</th></tr></thead><tbody>" +
      "<tr><td>RAG + cite spans</td><td>Answer ko evidence se bind; missing evidence ⇒ abstain</td></tr>" +
      "<tr><td>Low temperature</td><td>Less random wording; facts still need grounding</td></tr>" +
      "<tr><td>Structured output</td><td>Schema valid ≠ truth valid</td></tr>" +
      "<tr><td>Golden set / judges</td><td>Catch regressions before users do</td></tr>" +
      "</tbody></table>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Ek galat citation hallucination se zyada dangerous ho sakti hai kyunki user trust kar leta hai. Citation checker (span really in chunk?) alag metric rakho.</p></div>",
  },

  tpm: {
    title: "TPM & rate limits",
    track: "PROD",
    aliases: ["TPM", "tokens-per-minute", "rate limit", "rate limits", "rate-limit"],
    blurb: "Provider capacity budget — parallel agents ise easily tod dete hain.",
    related: ["tokenization", "async-io", "agent", "circuit-breaker"],
    body:
      "<p>Providers <strong>TPM</strong> (tokens per minute) aur RPM (requests per minute) limits dete hain. Aapka “p95 latency” tab bhi toot sakta hai jab model healthy ho — queue + 429s. Capacity planning = tokens × QPS, not vibes.</p>" +
      "<figure class='diagram' aria-label='tpm budget chart'>" +
      "<svg viewBox='0 0 420 170' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='170' fill='#F5F1E6'/>" +
      "<rect x='50' y='30' width='40' height='110' fill='#3F8C87'/>" +
      "<rect x='110' y='70' width='40' height='70' fill='#1C2438'/>" +
      "<rect x='170' y='50' width='40' height='90' fill='#B8923F'/>" +
      "<rect x='230' y='20' width='40' height='120' fill='#9B3D3D'/>" +
      "<line x1='40' y1='40' x2='300' y2='40' stroke='#12172B' stroke-dasharray='4 4'/>" +
      "<text x='308' y='44' fill='#12172B' font-size='11'>TPM cap</text>" +
      "<text x='70' y='158' text-anchor='middle' fill='#4A5268' font-size='10'>ok</text>" +
      "<text x='130' y='158' text-anchor='middle' fill='#4A5268' font-size='10'>ok</text>" +
      "<text x='190' y='158' text-anchor='middle' fill='#4A5268' font-size='10'>peak</text>" +
      "<text x='250' y='158' text-anchor='middle' fill='#9B3D3D' font-size='10'>429</text>" +
      "</svg>" +
      "<figcaption>Figure. Agent retry storms cap ke upar spike karte hain — backoff + circuit breaker.</figcaption></figure>",
  },

  "structured-output": {
    title: "Structured output",
    track: "APP",
    aliases: ["structured output", "structured outputs", "JSON schema", "JSON mode"],
    blurb: "Model se valid JSON / schema-bound objects nikalna — logs aur tools ke liye.",
    related: ["temperature", "agent", "evaluation"],
    body:
      "<p>Free-form prose ko <code>json.loads</code> pe mat chhodo. <strong>Structured output</strong> (JSON schema / tool parameters / constrained decoding) runtime ko machine-readable contract deta hai. Pydantic se validate karo; fail ⇒ retry or safe error, silent default nahi.</p>" +
      "<div class='callout pitfall'><span class='callout-label'>Pitfall</span><p>Schema-valid object still semantically wrong ho sakta hai (<code>{\"max_days\": 14}</code> jab policy 10 ho). Structure ≠ truth. Eval alag rakho.</p></div>",
  },

  "circuit-breaker": {
    title: "Circuit breaker",
    track: "PROD",
    aliases: ["circuit breaker", "circuit-breaker", "failover"],
    blurb: "Failing dependency ko bar-bar mat peeto — open the circuit, degrade, recover.",
    related: ["tpm", "async-io", "agent"],
    body:
      "<p>Jab provider 5xx/timeouts ki streak de, retries amplify kar sakte hain (retry storm). <strong>Circuit breaker</strong>: closed (normal) → open (fast-fail / fallback model) → half-open (probe). Failover router ke saath yeh p95 bachata hai.</p>" +
      "<figure class='diagram' aria-label='circuit breaker states'>" +
      "<svg viewBox='0 0 420 130' xmlns='http://www.w3.org/2000/svg' role='img'>" +
      "<rect width='420' height='130' fill='#F5F1E6'/>" +
      "<rect x='16' y='40' width='110' height='50' rx='8' fill='#2F6E4A'/><text x='71' y='70' text-anchor='middle' fill='#F5F1E6' font-size='12'>closed</text>" +
      "<rect x='155' y='40' width='110' height='50' rx='8' fill='#9B3D3D'/><text x='210' y='70' text-anchor='middle' fill='#F5F1E6' font-size='12'>open</text>" +
      "<rect x='294' y='40' width='110' height='50' rx='8' fill='#B8923F'/><text x='349' y='70' text-anchor='middle' fill='#12172B' font-size='12'>half-open</text>" +
      "<path d='M126 65 H155 M265 65 H294' stroke='#12172B' stroke-width='2'/>" +
      "</svg>" +
      "<figcaption>Figure. Three states. Open ≠ “retry harder”.</figcaption></figure>",
  },
};
