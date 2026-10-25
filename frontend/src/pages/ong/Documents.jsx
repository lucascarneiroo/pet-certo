import { useEffect, useMemo, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import { listarDocumentos, listarProcessos } from "../../services/api";

const STATUS_PROCESSO = ["Em Andamento", "Concluído", "Cancelado"];

export default function OngDocuments() {
  const [processos, setProcessos] = useState([]);
  const [selecionadoId, setSelecionadoId] = useState(null);
  const [documentos, setDocumentos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [carregandoDocs, setCarregandoDocs] = useState(false);
  const [erro, setErro] = useState("");

  const [busca, setBusca] = useState("");
  const [statusFiltro, setStatusFiltro] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    listarProcessos()
      .then(setProcessos)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  useEffect(() => {
    if (!selecionadoId) {
      setDocumentos([]);
      return;
    }
    setCarregandoDocs(true);
    listarDocumentos(selecionadoId)
      .then(setDocumentos)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregandoDocs(false));
  }, [selecionadoId]);

  const processosFiltrados = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    return processos.filter((p) => {
      const bateBusca = !termo || `${p.nome_adotante} ${p.nome_animal}`.toLowerCase().includes(termo);
      const bateStatus = !statusFiltro || p.status === statusFiltro;
      return bateBusca && bateStatus;
    });
  }, [processos, busca, statusFiltro]);

  return (
    <>
      <Panel
        title="Processos"
        subtitle={`${processosFiltrados.length} de ${processos.length} — selecione um para ver os documentos enviados`}
      >
        <div className="mb-4 flex flex-wrap items-end gap-3">
          <input
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar por adotante ou animal"
            className="min-w-[220px] flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink outline-none focus:border-ong"
          />
          <select
            value={statusFiltro}
            onChange={(e) => setStatusFiltro(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
          >
            <option value="">Todas as situações</option>
            {STATUS_PROCESSO.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && processosFiltrados.length === 0 && (
          <p className="text-sm text-muted">Nenhum processo encontrado com esses filtros.</p>
        )}
        <div className="space-y-3">
          {processosFiltrados.map((p) => (
            <Row
              key={p.id}
              title={`${p.nome_adotante} × ${p.nome_animal}`}
              subtitle={`Processo #${p.id}`}
              onClick={() => setSelecionadoId(p.id)}
              className={selecionadoId === p.id ? "border-ong" : ""}
              right={<span className="text-xs text-muted">{p.status}</span>}
            />
          ))}
        </div>
      </Panel>

      {selecionadoId && (
        <Panel title="Documentos enviados" subtitle={`Processo #${selecionadoId}`}>
          {carregandoDocs && <p className="text-sm text-muted">Carregando...</p>}
          {!carregandoDocs && documentos.length === 0 && (
            <p className="text-sm text-muted">Nenhum documento enviado ainda para este processo.</p>
          )}
          <div className="space-y-3">
            {documentos.map((d) => (
              <Row key={d.id} title={d.nome} subtitle={d.caminho_arquivo} />
            ))}
          </div>
        </Panel>
      )}
    </>
  );
}
