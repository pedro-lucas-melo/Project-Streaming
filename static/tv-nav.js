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
// `items` deve conter só os alvos navegáveis (cards/botões reais), nunca os
// botões sobrepostos (watchlist/remover) — esses são tratados caso a caso.
(function () {
    function byReadingOrder(a, b) {
        var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        // mesma linha se a diferença vertical for pequena (tolera scale no foco)
        if (Math.abs(ra.top - rb.top) > 24) return ra.top - rb.top;
        return ra.left - rb.left;
    }

    window.tvNavMove = function (items, cur, dir) {
        if (!items || !items.length) return null;
        var ordered = items.slice().sort(byReadingOrder);
        var idx = ordered.indexOf(cur);
        if (idx === -1) return ordered[0];

        if (dir === "right") return idx < ordered.length - 1 ? ordered[idx + 1] : null;
        if (dir === "left")  return idx > 0 ? ordered[idx - 1] : null;

        // cima / baixo: salto de linha geométrico
        var cr = cur.getBoundingClientRect();
        var ccx = cr.left + cr.width / 2;
        var best = null, bestScore = Infinity;
        items.forEach(function (el) {
            if (el === cur) return;
            var r = el.getBoundingClientRect();
            var ok = dir === "down" ? r.top >= cr.bottom - 5 : r.bottom <= cr.top + 5;
            if (!ok) return;
            var dx = Math.abs((r.left + r.width / 2) - ccx);
            var dy = dir === "down" ? r.top - cr.bottom : cr.top - r.bottom;
            var score = dy + dx * 3;
            if (score < bestScore) { bestScore = score; best = el; }
        });
        return best;
    };
})();
