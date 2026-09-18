import { Panel, Stat } from "../../components/Panel";

export default function OngIndicators() {
  return (
    <Panel title="Indicadores" subtitle="Desempenho de adoções · 2026">
      <div className="grid gap-4 sm:grid-cols-3">
        <Stat label="Taxa de conclusão" value="72%" hint="+8 p.p." hintTone="up" />
        <Stat label="Tempo médio" value="18 dias" hint="-3 dias" hintTone="up" />
        <Stat label="Visitas realizadas" value="84" hint="91% comparecimento" />
      </div>

      <div className="mt-4 rounded-xl border border-slate-100 p-4">
        <p className="text-sm font-bold text-ink">Funil do processo</p>
        <p className="mt-1 text-sm text-muted">
          126 interesses → 78 análises → 51 visitas → 34 conclusões
        </p>
      </div>
    </Panel>
  );
}
