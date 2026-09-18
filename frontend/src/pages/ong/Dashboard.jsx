import { Panel, Stat } from "../../components/Panel";

export default function OngDashboard() {
  return (
    <Panel title="Dashboard da instituição" subtitle="Instituto Amor Animal">
      <div className="grid gap-4 sm:grid-cols-3">
        <Stat label="Disponíveis" value="38" hint="+4 este mês" hintTone="up" />
        <Stat label="Em processo" value="12" hint="5 aguardam análise" hintTone="warn" />
        <Stat label="Adotados" value="27" hint="+18% no trimestre" hintTone="up" />
      </div>

      <div className="mt-4 rounded-xl border border-slate-100 p-4">
        <p className="text-sm font-bold text-ink">Agenda de hoje</p>
        <p className="mt-1 text-sm text-muted">
          14:30 · Marina Oliveira visita Luna · 16:00 · Paulo visita Nino
        </p>
      </div>
    </Panel>
  );
}
