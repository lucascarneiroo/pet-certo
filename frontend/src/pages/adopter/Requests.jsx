import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { requests } from "../../data/mockData";

export default function AdopterRequests() {
  const mine = requests[0];

  return (
    <>
      <Panel title="Minhas Adoções" subtitle="Acompanhe solicitações e status">
        <Row
          title={`${mine.animal} · Solicitação #${mine.id}`}
          subtitle={mine.animal === "Luna" ? "Instituto Amor Animal" : ""}
          right={<StatusBadge status="Documentos pendentes" />}
        />

        <div className="mt-5 rounded-xl border border-slate-100 p-4">
          <p className="text-sm font-bold text-ink">Outras solicitações</p>
          <p className="mt-1 text-sm text-muted">
            Nino · Rejeitada em 22 ago · perfil incompatível com rotina
          </p>
        </div>
      </Panel>

      <Panel title="Processo de Adoção" subtitle={`${mine.animal} · Solicitação #${mine.id}`}>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-100 p-4">
            <p className="mb-2 text-sm font-bold text-ink">Etapas</p>
            <ul className="space-y-1.5 text-sm">
              {mine.steps.map((s) => (
                <li
                  key={s.label}
                  className={s.current ? "font-semibold text-adopter" : "text-muted"}
                >
                  {s.done ? "✓ " : s.current ? "• " : "· "}
                  {s.label} {s.date && `· ${s.date}`}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border border-slate-100 p-4">
            <p className="text-sm font-bold text-ink">Próxima ação</p>
            <StatusBadge status="Documentos pendentes" />
            <p className="mt-2 text-sm text-muted">Envie o comprovante corrigido até 18 set.</p>
            <button className="mt-3 rounded-lg bg-adopter px-4 py-2 text-sm font-semibold text-white transition hover:bg-adopter-dark">
              Ver documentos
            </button>
          </div>
        </div>
      </Panel>
    </>
  );
}
