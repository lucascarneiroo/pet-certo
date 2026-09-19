import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { requests } from "../../data/mockData";

export default function AdminAnimals() {
  return (
    <Panel title="Animais e processos" subtitle="Supervisão de cadastros e adoções">
      <div className="space-y-3">
        {requests.map((r) => (
          <Row
            key={r.id}
            title={`${r.animal} · ${r.status === "Concluído" ? "Amor Animal" : "Amor Animal"} · ${
              r.status === "Concluído" ? `Processo #${r.id}` : `Solicitação #${r.id}`
            }`}
            right={<StatusBadge status={r.status} />}
          />
        ))}
      </div>

      <div className="mt-5 rounded-xl border border-slate-100 p-4">
        <p className="text-sm font-bold text-ink">Registros administrativos</p>
        <p className="mt-1 text-xs text-muted">
          14 set, 10:20 · alteração de permissão · admin@petcerto.org
        </p>
      </div>
    </Panel>
  );
}
