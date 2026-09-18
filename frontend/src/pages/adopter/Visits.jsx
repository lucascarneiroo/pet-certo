import { Panel } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";

export default function AdopterVisits() {
  return (
    <Panel title="Agendamento de Visita" subtitle="Conheça Luna no Instituto Amor Animal">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-100 p-4">
          <p className="mb-3 text-sm font-bold text-ink">Data e horário</p>
          <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
            Data
          </label>
          <input
            readOnly
            value="15 de setembro de 2026"
            className="mb-3 w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink"
          />
          <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
            Horário
          </label>
          <input
            readOnly
            value="14:30"
            className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink"
          />
        </div>
        <div className="rounded-xl border border-slate-100 p-4">
          <p className="mb-3 text-sm font-bold text-ink">Local</p>
          <p className="text-sm text-muted">Rua das Acácias, 120 · Vila Mariana</p>
          <div className="mt-3">
            <StatusBadge status="Agendada" />
          </div>
          <button className="mt-4 rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink">
            Reagendar
          </button>
        </div>
      </div>
    </Panel>
  );
}
