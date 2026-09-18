import { Panel, Stat } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";

export default function AdopterDashboard() {
  return (
    <Panel title="Olá, Marina" subtitle="Seu processo com Luna está avançando">
      <div className="grid gap-4 sm:grid-cols-3">
        <Stat label="Recomendações" value="12" hint="3 novas" hintTone="up" />
        <Stat label="Solicitações" value="1" hint="Em análise" hintTone="warn" />
        <Stat label="Próxima visita" value="15 set" hint="14:30 · Amor Animal" />
      </div>

      <div className="mt-4 flex items-center justify-between rounded-xl border border-slate-100 p-4">
        <div>
          <p className="text-sm font-bold text-ink">Pendências</p>
          <p className="mt-1 text-sm text-muted">Envie o comprovante de residência</p>
        </div>
        <StatusBadge status="Pendente" />
      </div>
    </Panel>
  );
}
