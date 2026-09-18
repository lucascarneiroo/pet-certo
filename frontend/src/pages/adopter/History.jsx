import { Panel } from "../../components/Panel";
import { compatibilityProfile, history } from "../../data/mockData";

export default function AdopterHistory() {
  return (
    <>
      <Panel title="Perfil de Compatibilidade" subtitle="5 de 5 categorias preenchidas">
        <div className="grid gap-3 sm:grid-cols-2">
          {compatibilityProfile.map((c) => (
            <div key={c.label} className="rounded-xl border border-slate-100 p-4">
              <p className="text-sm font-bold text-ink">
                {c.label} · {c.value}
              </p>
              <span className="mt-2 inline-flex items-center rounded-full bg-[#E4F3E9] px-3 py-1 text-xs font-semibold text-[#2F7A50]">
                Completo
              </span>
            </div>
          ))}
        </div>
        <button className="mt-5 rounded-lg bg-adopter px-4 py-2 text-sm font-semibold text-white transition hover:bg-adopter-dark">
          Atualizar perfil
        </button>
      </Panel>

      <Panel title="Histórico do processo" subtitle="Registro rastreável de Luna">
        <div className="space-y-3">
          {history.map((h) => (
            <div
              key={h.id}
              className="rounded-xl border border-slate-100 px-4 py-3 text-sm text-ink"
            >
              <span className="text-muted">{h.date} · </span>
              {h.label} · {h.by}
            </div>
          ))}
        </div>
      </Panel>
    </>
  );
}
