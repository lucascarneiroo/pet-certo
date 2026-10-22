// Exportação de listagens em CSV — usada pelas telas de relatório/gestão
// (animais, usuários, instituições, processos). Gerado no navegador, sem
// nenhuma biblioteca externa: monta o texto CSV e dispara o download via
// Blob, igual a qualquer link de arquivo comum.

function escaparCampo(valor) {
  const texto = valor === null || valor === undefined ? "" : String(valor);
  if (texto.includes(";") || texto.includes('"') || texto.includes("\n")) {
    return `"${texto.replace(/"/g, '""')}"`;
  }
  return texto;
}

// colunas: [{ chave, titulo }], linhas: array de objetos
export function exportarCsv(nomeArquivo, colunas, linhas) {
  const cabecalho = colunas.map((c) => escaparCampo(c.titulo)).join(";");
  const corpo = linhas
    .map((linha) => colunas.map((c) => escaparCampo(linha[c.chave])).join(";"))
    .join("\n");
  // BOM (marca de ordem de byte) garante que o Excel abra os acentos
  // corretamente. Usa String.fromCharCode em vez do caractere/escape
  // literal porque ferramentas de build podem normalizar/remover um BOM
  // "de verdade" embutido no código-fonte.
  const bom = String.fromCharCode(0xfeff);
  const conteudo = bom + cabecalho + "\n" + corpo;

  const blob = new Blob([conteudo], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nomeArquivo.endsWith(".csv") ? nomeArquivo : `${nomeArquivo}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
