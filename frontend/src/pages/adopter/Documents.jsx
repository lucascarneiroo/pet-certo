import { useEffect, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import { enviarDocumento, listarDocumentos, listarProcessos } from "../../services/api";

export default function AdopterDocuments() {
  const [processos, setProcessos] = useState([]);
  const [selecionadoId, setSelecionadoId] = useState(null);
  const [documentos, setDocumentos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const [nome, setNome] = useState("");
  const [caminho, setCaminho] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erroEnvio, setErroEnvio] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    listarProcessos()
      .then((procs) => {
        setProcessos(procs);
        const emAndamento = procs.filter((p) => p.status === "Em Andamento");
        if (emAndamento.length > 0) setSelecionadoId(emAndamento[0].id);
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  function carregarDocumentos() {
    if (!selecionadoId) {
      setDocumentos([]);
      return;
    }
    listarDocumentos(selecionadoId)
      .then(setDocumentos)
      .catch((err) => setErro(err.message));
  }

  useEffect(() => {
    carregarDocumentos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selecionadoId]);

  async function handleEnviar(e) {
    e.preventDefault();
    if (!nome.trim() || !caminho.trim()) {
      setErroEnvio("Preencha o nome do documento e o arquivo.");
      return;
    }
    setErroEnvio("");
    setEnviando(true);
    try {
      await enviarDocumento(selecionadoId, nome.trim(), caminho.trim());
      setNome("");
      setCaminho("");
      carregarDocumentos();
    } catch (err) {
      setErroEnvio(err.message);
    } finally {
      setEnviando(false);
    }
  }

  const emAndamento = processos.filter((p) => p.status === "Em Andamento");

  if (carregando) {
    return (
      <Panel title="Documentos">
        <p className="text-sm text-muted">Carregando...</p>
      </Panel>
    );
  }

  if (emAndamento.length === 0) {
    return (
      <Panel title="Documentos" subtitle="Envie e acompanhe cada arquivo">
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        <p className="text-sm text-muted">Você não tem nenhum processo de adoção em andamento no momento.</p>
      </Panel>
    );
  }

  return (
    <Panel title="Documentos" subtitle="Envie e acompanhe cada arquivo do seu processo">
      {erro && <p className="text-sm text-red-600">{erro}</p>}

      {emAndamento.length > 1 && (
        <select
          value={selecionadoId || ""}
          onChange={(e) => setSelecionadoId(Number(e.target.value))}
          className="mb-4 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
        >
          {emAndamento.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nome_animal} · Processo #{p.id}
            </option>
          ))}
        </select>
      )}

      <div className="space-y-3">
        {documentos.length === 0 && <p className="text-sm text-muted">Nenhum documento enviado ainda.</p>}
        {documentos.map((d) => (
          <Row key={d.id} title={d.nome} subtitle={d.caminho_arquivo} />
        ))}
      </div>

      <form onSubmit={handleEnviar} className="mt-5 grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
        <input
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          placeholder="Nome do documento (ex.: RG)"
          className="rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
        />
        <input
          value={caminho}
          onChange={(e) => setCaminho(e.target.value)}
          placeholder="Caminho/referência do arquivo"
          className="rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
        />
        <button
          type="submit"
          disabled={enviando}
          className="rounded-lg bg-adopter px-4 py-2 text-sm font-semibold text-white transition hover:bg-adopter-dark disabled:opacity-60"
        >
          {enviando ? "Enviando..." : "Enviar"}
        </button>
      </form>
      {erroEnvio && <p className="mt-2 text-sm text-red-600">{erroEnvio}</p>}
    </Panel>
  );
}
