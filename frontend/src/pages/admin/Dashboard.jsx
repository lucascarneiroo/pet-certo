import { Panel, Stat } from "../../components/Panel";

export default function AdminDashboard() {
  return (
    <Panel title="Dashboard administrativo" subtitle="Visão geral da plataforma">
      <div className="grid gap-4 sm:grid-cols-3">
        <Stat label="Usuários" value="8.420" hint="+6,4%" hintTone="up" />
        <Stat label="Instituições" value="146" hint="8 em análise" hintTone="warn" />
        <Stat label="Processos ativos" value="392" hint="74 concluídos/mês" />
      </div>

      <div className="mt-4 rounded-xl border border-slate-100 p-4">
        <p className="text-sm font-bold text-ink">Saúde operacional</p>
        <span className="mt-2 inline-flex items-center rounded-full bg-admin-soft px-3 py-1 text-xs font-semibold text-admin">
          Todos os serviços operacionais
        </span>
      </div>
    </Panel>
  );
}
