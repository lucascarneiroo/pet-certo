import { useState } from "react";
import { Panel, Row, ProgressBar } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { requests, documents } from "../../data/mockData";

export default function OngRequests() {
  const [selectedId, setSelectedId] = useState(requests[0].id);
  const selected = requests.find((r) => r.id === selectedId);

  return (
    <>
      <Panel title="Solicitações recebidas" subtitle={`${requests.length} solicitações no total`}>
        <div className="space-y-3">
          {requests.map((r) => (
            <Row
              key={r.id}
              title={`${r.adopter} → ${r.animal} · ${r.compat}%`}
              onClick={() => setSelectedId(r.id)}
              className={selectedId === r.id ? "border-ong" : ""}
              right={<StatusBadge status={r.tag} />}
            />
          ))}
        </div>
      </Panel>

      {selected && (
        <Panel title="Análise do adotante" subtitle={`${selected.adopter} × ${selected.animal}`}>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-slate-100 p-4">
              <p className="text-sm font-bold text-ink">Perfil</p>
              <span className="mt-2 inline-flex items-center rounded-full bg-[#E4F3E9] px-3 py-1 text-xs font-semibold text-[#2F7A50]">
                {selected.compat}% compatível
              </span>
              <p className="mt-3 text-sm text-muted">{selected.profile}</p>
            </div>
            <div className="rounded-xl border border-slate-100 p-4">
              <p className="mb-3 text-sm font-bold text-ink">Fatores</p>
              <div className="space-y-3">
                <ProgressBar label="Moradia" value={selected.factors.moradia} />
                <ProgressBar label="Rotina" value={selected.factors.rotina} />
              </div>
            </div>
          </div>
          <div className="mt-4 flex gap-3">
            <button className="rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark">
              Aceitar solicitação
            </button>
            <button className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink">
              Rejeitar
            </button>
          </div>
        </Panel>
      )}

      {selected && (
        <Panel title="Análise de documentos" subtitle={`Solicitação #${selected.id}`}>
          <div className="space-y-3">
            {documents.map((d) => (
              <Row key={d.id} title={`${d.name} · ${d.detail}`} right={<StatusBadge status={d.status} />} />
            ))}
          </div>
          <div className="mt-4 flex gap-3">
            <button className="rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark">
              Aprovar documento
            </button>
            <button className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink">
              Rejeitar com motivo
            </button>
          </div>
        </Panel>
      )}
    </>
  );
}
