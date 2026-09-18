import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { visits, requests } from "../../data/mockData";

export default function OngVisits() {
  const process = requests[0];

  return (
    <>
      <Panel title="Agenda de visitas" subtitle="Semana de 14 a 20 de setembro">
        <div className="space-y-3">
          {visits.map((v) => (
            <Row
              key={v.id}
              title={`${v.date} · ${v.time} · ${v.people} · ${v.note}`}
              right={<StatusBadge status={v.status} />}
            />
          ))}
        </div>
        <button className="mt-5 rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark">
          Registrar visita
        </button>
      </Panel>

      <Panel title="Processo de adoção" subtitle={`#${process.id} · ${process.adopter} × ${process.animal}`}>
        <div className="rounded-xl border border-slate-100 p-4">
          <p className="text-sm font-bold text-ink">Status atual</p>
          <span className="mt-2 inline-flex items-center rounded-full bg-[#FBF0DC] px-3 py-1 text-xs font-semibold text-[#9A6B1E]">
            {process.stage}
          </span>
          <p className="mt-3 flex flex-wrap gap-x-2 gap-y-1 text-sm text-muted">
            {process.steps.map((s, i) => (
              <span key={s.label}>
                {s.label}
                {s.done ? " ✓" : ""}
                {i < process.steps.length - 1 ? " ·" : ""}
              </span>
            ))}
          </p>
        </div>

        <div className="mt-4 rounded-xl border border-slate-100 p-4">
          <p className="text-sm font-bold text-ink">Ação da instituição</p>
          <p className="mt-1 text-sm text-muted">
            Revisar nova versão do comprovante de residência e registrar decisão.
          </p>
          <button className="mt-3 rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark">
            Abrir análise
          </button>
        </div>
      </Panel>
    </>
  );
}
