import { useEffect, useState } from "react";
import { Panel, Stat } from "../../components/Panel";
import { listarManifestacoes, listarProcessos, listarVisitas } from "../../services/api";

export default function OngIndicators() {
  const [manifestacoes, setManifestacoes] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [visitas, setVisitas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    Promise.all([listarManifestacoes(), listarProcessos()])
      .then(async ([manifs, procs]) => {
        setManifestacoes(manifs);
        setProcessos(procs);
        const todasVisitas = (
          await Promise.all(procs.map((p) => listarVisitas(p.id).catch(() => [])))
        ).flat();
        setVisitas(todasVisitas);
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  const pendentes = manifestacoes.filter((m) => m.status === "Pendente").length;
  const concluidos = processos.filter((p) => p.status === "Concluído").length;
  const taxaConclusao = processos.length > 0 ? Math.round((concluidos / processos.length) * 100) : 0;
  const visitasRealizadas = visitas.filter((v) => v.status === "Realizada").length;
  const visitasAgendadas = visitas.filter((v) => v.status !== "Cancelada").length;
  const comparecimento = visitasAgendadas > 0 ? Math.round((visitasRealizadas / visitasAgendadas) * 100) : 0;

  return (
    <Panel title="Indicadores" subtitle="Desempenho de adoções desta instituição">
      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}

      {!carregando && !erro && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Taxa de conclusão" value={`${taxaConclusao}%`} hint={`${concluidos} de ${processos.length} processos`} />
            <Stat
              label="Visitas realizadas"
              value={visitasRealizadas}
              hint={visitasAgendadas > 0 ? `${comparecimento}% comparecimento` : undefined}
            />
            <Stat label="Manifestações pendentes" value={pendentes} hintTone="warn" />
          </div>

          <div className="mt-4 rounded-xl border border-slate-100 p-4">
            <p className="text-sm font-bold text-ink">Funil do processo</p>
            <p className="mt-1 text-sm text-muted">
              {manifestacoes.length} interesses → {processos.length} processos → {visitas.length} visitas →{" "}
              {concluidos} conclusões
            </p>
          </div>
        </>
      )}
    </Panel>
  );
}
