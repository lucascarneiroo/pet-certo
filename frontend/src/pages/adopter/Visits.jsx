import { useEffect, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { listarProcessos, listarVisitas } from "../../services/api";

function formatarDataHora(valor) {
  const d = new Date(String(valor).replace(" ", "T"));
  return Number.isNaN(d.getTime()) ? valor : d.toLocaleString("pt-BR");
}

export default function AdopterVisits() {
  const [processos, setProcessos] = useState([]);
  const [visitasPorProcesso, setVisitasPorProcesso] = useState({});
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    listarProcessos()
      .then(async (procs) => {
        setProcessos(procs);
        const emAndamento = procs.filter((p) => p.status === "Em Andamento");
        const entries = await Promise.all(
          emAndamento.map((p) => listarVisitas(p.id).then((v) => [p.id, v]).catch(() => [p.id, []]))
        );
        setVisitasPorProcesso(Object.fromEntries(entries));
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  const emAndamento = processos.filter((p) => p.status === "Em Andamento");

  return (
    <Panel title="Minhas visitas" subtitle="Agendadas pela instituição para o seu processo de adoção">
      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}
      {!carregando && !erro && emAndamento.length === 0 && (
        <p className="text-sm text-muted">Você não tem nenhum processo de adoção em andamento no momento.</p>
      )}
      <div className="space-y-4">
        {emAndamento.map((p) => {
          const visitas = visitasPorProcesso[p.id] || [];
          return (
            <div key={p.id} className="rounded-xl border border-slate-100 p-4">
              <p className="text-sm font-bold text-ink">
                {p.nome_animal} · Processo #{p.id}
              </p>
              {visitas.length === 0 ? (
                <p className="mt-2 text-sm text-muted">A instituição ainda não agendou uma visita.</p>
              ) : (
                <div className="mt-2 space-y-2">
                  {visitas.map((v) => (
                    <Row
                      key={v.id}
                      title={formatarDataHora(v.data_visita)}
                      subtitle={v.resultado || undefined}
                      right={<StatusBadge status={v.status} />}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Panel>
  );
}
