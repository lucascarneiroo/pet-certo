import { useEffect, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { listarEtapas, listarManifestacoes, listarProcessos } from "../../services/api";

export default function AdopterRequests() {
  const [manifestacoes, setManifestacoes] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

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

  return (
    <>
      <Panel title="Minhas Adoções" subtitle="Acompanhe suas manifestações de interesse e processos">
        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && !erro && manifestacoes.length === 0 && (
          <p className="text-sm text-muted">Você ainda não manifestou interesse em nenhum animal.</p>
        )}
        <div className="space-y-3">
          {manifestacoes.map((m) => {
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
