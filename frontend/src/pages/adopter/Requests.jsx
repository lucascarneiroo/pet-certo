import { useEffect, useMemo, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { listarEtapas, listarManifestacoes, listarProcessos } from "../../services/api";

// união dos status possíveis: de ManifestacaoInteresse (sem processo ainda)
// e de ProcessoAdocao (depois que a instituição aprova)
const STATUS_SOLICITACAO = ["Pendente", "Recusada", "Em Andamento", "Concluído", "Cancelado"];

export default function AdopterRequests() {
  const [manifestacoes, setManifestacoes] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [statusFiltro, setStatusFiltro] = useState("");

  const [processoSelecionadoId, setProcessoSelecionadoId] = useState(null);
  const [etapas, setEtapas] = useState([]);
  const [carregandoEtapas, setCarregandoEtapas] = useState(false);

  useEffect(() => {
    setCarregando(true);
    setErro("");
    Promise.all([listarManifestacoes(), listarProcessos()])
      .then(([listaManifestacoes, listaProcessos]) => {
        setManifestacoes(listaManifestacoes);
        setProcessos(listaProcessos);
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  useEffect(() => {
    if (!processoSelecionadoId) {
      setEtapas([]);
      return;
    }
    setCarregandoEtapas(true);
    listarEtapas(processoSelecionadoId)
      .then(setEtapas)
      .catch(() => setEtapas([]))
      .finally(() => setCarregandoEtapas(false));
  }, [processoSelecionadoId]);

  const processoDaManifestacao = (idManifestacao) =>
    processos.find((p) => p.id_manifestacao === idManifestacao);

  const processoAtivo = processos.find((p) => p.id === processoSelecionadoId) || null;

  const manifestacoesFiltradas = useMemo(
    () =>
      manifestacoes.filter((m) => {
        if (!statusFiltro) return true;
        const processo = processoDaManifestacao(m.id);
        const statusEfetivo = processo ? processo.status : m.status;
        return statusEfetivo === statusFiltro;
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [manifestacoes, processos, statusFiltro]
  );

  return (
    <>
      <Panel
        title="Minhas Adoções"
        subtitle={`${manifestacoesFiltradas.length} de ${manifestacoes.length} — acompanhe suas manifestações de interesse e processos`}
      >
        <select
          value={statusFiltro}
          onChange={(e) => setStatusFiltro(e.target.value)}
          className="mb-4 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
        >
          <option value="">Todas as situações</option>
          {STATUS_SOLICITACAO.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && !erro && manifestacoes.length === 0 && (
          <p className="text-sm text-muted">Você ainda não manifestou interesse em nenhum animal.</p>
        )}
        {!carregando && !erro && manifestacoes.length > 0 && manifestacoesFiltradas.length === 0 && (
          <p className="text-sm text-muted">Nenhuma solicitação encontrada com esse filtro.</p>
        )}
        <div className="space-y-3">
          {manifestacoesFiltradas.map((m) => {
            const processo = processoDaManifestacao(m.id);
            return (
              <Row
                key={m.id}
                title={`${m.nome_animal} · Solicitação #${m.id}`}
                subtitle={
                  processo
                    ? `Processo #${processo.id} em andamento — clique para ver as etapas`
                    : `Manifestada em ${m.data_manifestacao}`
                }
                onClick={processo ? () => setProcessoSelecionadoId(processo.id) : undefined}
                className={processo && processoSelecionadoId === processo.id ? "border-adopter" : ""}
                right={<StatusBadge status={processo ? processo.status : m.status} />}
              />
            );
          })}
        </div>
      </Panel>

      {processoAtivo && (
        <Panel title="Processo de Adoção" subtitle={`${processoAtivo.nome_animal} · Processo #${processoAtivo.id}`}>
          {carregandoEtapas && <p className="text-sm text-muted">Carregando etapas...</p>}
          <div className="rounded-xl border border-slate-100 p-4">
            <p className="mb-2 text-sm font-bold text-ink">Etapas</p>
            <ul className="space-y-1.5 text-sm">
              {etapas.map((e) => (
                <li key={e.id} className={e.status === "Em Andamento" ? "font-semibold text-adopter" : "text-muted"}>
                  {e.status === "Concluída" ? "✓ " : e.status === "Em Andamento" ? "• " : "· "}
                  {e.nome} — {e.status}
                </li>
              ))}
            </ul>
          </div>
        </Panel>
      )}
    </>
  );
}
