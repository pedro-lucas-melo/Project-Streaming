// ── NAVEGAÇÃO ESPACIAL PARA TV (controle remoto) ─────────────────────────────
// Fonte única usada por todas as grades (filmes, séries, temporadas, episódios).
//
// Esquerda/Direita = ORDEM DE LEITURA (cima→baixo, esquerda→direita).
//   Garante que apertar → percorre TODOS os títulos em sequência, sem pular
//   e sem travar no fim da linha (no fim de uma linha pula para o início da
//   próxima). Resolve o "pular título" e o "não consigo selecionar X".
//
// Cima/Baixo = salto de linha geométrico, com forte preferência de coluna
//   (peso 3 no desvio horizontal) para nunca cair num item diagonal errado.
//
// TODAS as comparações verticais usam o CENTRO do elemento, nunca as bordas:
//   o foco aplica transform scale(), que expande as bordas (top/bottom) mas
//   mantém o centro fixo. Comparar bordas fazia o card focado "invadir" a
//   linha de baixo e a navegação pular uma linha inteira.
//
// `items` deve conter só os alvos navegáveis (cards/botões reais), nunca os
// botões sobrepostos (watchlist/remover) — esses são tratados caso a caso.
(function () {
    function centerY(r) { return r.top + r.height / 2; }

    function byReadingOrder(a, b) {
        var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        // mesma linha se os centros verticais estiverem próximos
        var d = centerY(ra) - centerY(rb);
        if (Math.abs(d) > 24) return d;
        return ra.left - rb.left;
    }

    window.tvNavMove = function (items, cur, dir) {
        if (!items || !items.length) return null;
        var ordered = items.slice().sort(byReadingOrder);
        var idx = ordered.indexOf(cur);
        if (idx === -1) return ordered[0];

        if (dir === "right") return idx < ordered.length - 1 ? ordered[idx + 1] : null;
        if (dir === "left")  return idx > 0 ? ordered[idx - 1] : null;

        // cima / baixo: salto de linha geométrico por centro
        var cr = cur.getBoundingClientRect();
        var ccx = cr.left + cr.width / 2;
        var ccy = centerY(cr);
        var best = null, bestScore = Infinity;
        items.forEach(function (el) {
            if (el === cur) return;
            var r = el.getBoundingClientRect();
            var rcy = centerY(r);
            var ok = dir === "down" ? rcy > ccy + 10 : rcy < ccy - 10;
            if (!ok) return;
            var dx = Math.abs((r.left + r.width / 2) - ccx);
            var dy = Math.abs(rcy - ccy);
            var score = dy + dx * 3;
            if (score < bestScore) { bestScore = score; best = el; }
        });
        return best;
    };
})();
