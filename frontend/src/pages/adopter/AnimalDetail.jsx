import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Panel, ProgressBar } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { animals } from "../../data/mockData";

export default function AnimalDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const animal = animals.find((a) => a.id === id) || animals[0];
  const [showInterestForm, setShowInterestForm] = useState(false);
  const [message, setMessage] = useState(
    "Tenho rotina estável, experiência com cães e muito carinho para oferecer."
  );
  const [sent, setSent] = useState(false);

  return (
    <>
      <Panel>
        <div className="grid gap-6 sm:grid-cols-[220px_1fr]">
          <div className="flex aspect-square items-center justify-center rounded-xl bg-adopter-soft text-sm font-semibold text-adopter">
            {animal.speciesTag}
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-ink">{animal.name}</h2>
            <p className="text-sm text-muted">
              {animal.breed} · {animal.age} · {animal.size}
            </p>
            <StatusBadge status={animal.status} />
            <p className="mt-3 text-sm text-ink">{animal.temperament}</p>

            <div className="mt-4 rounded-xl border border-slate-100 p-4">
              <p className="text-sm font-bold text-ink">Instituição</p>
              <p className="mt-1 text-sm text-muted">
                {animal.institution} · {animal.city}
              </p>
            </div>

            {!sent ? (
              <button
                onClick={() => setShowInterestForm(true)}
                className="mt-4 rounded-lg bg-adopter px-4 py-2 text-sm font-semibold text-white transition hover:bg-adopter-dark"
              >
                Manifestar interesse
              </button>
            ) : (
              <p className="mt-4 text-sm font-semibold text-[#2F7A50]">
                Interesse enviado para {animal.institution}.
              </p>
            )}
          </div>
        </div>
      </Panel>

      {showInterestForm && !sent && (
        <Panel title="Manifestar interesse" subtitle={`Solicitação para adotar ${animal.name}`}>
          <div className="rounded-xl border border-slate-100 p-4">
            <p className="text-sm font-bold text-ink">Antes de enviar</p>
            <p className="mt-1 text-sm text-muted">
              A instituição analisará seu perfil e poderá entrar em contato. Conte por que{" "}
              {animal.name} combina com sua família.
            </p>
            <label className="mb-1 mt-4 block text-xs font-semibold uppercase tracking-wide text-muted">
              Mensagem
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
            />
          </div>
          <div className="mt-4 flex gap-3">
            <button
              onClick={() => setSent(true)}
              className="rounded-lg bg-adopter px-4 py-2 text-sm font-semibold text-white transition hover:bg-adopter-dark"
            >
              Enviar interesse
            </button>
            <button
              onClick={() => setShowInterestForm(false)}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink"
            >
              Cancelar
            </button>
          </div>
        </Panel>
      )}

      <Panel title={`Compatibilidade com ${animal.name}`} subtitle="Resultado claro e personalizado">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex flex-col items-start justify-center rounded-xl border border-slate-100 p-4">
            <p className="text-3xl font-extrabold text-[#2F7A50]">{animal.compat}%</p>
            <p className="mt-1 text-sm text-muted">Excelente combinação</p>
          </div>
          <div className="rounded-xl border border-slate-100 p-4">
            <p className="mb-3 text-sm font-bold text-ink">Fatores positivos</p>
            <div className="space-y-3">
              <ProgressBar label="Rotina" value={96} />
              <ProgressBar label="Moradia" value={92} />
              <ProgressBar label="Experiência" value={95} />
            </div>
          </div>
        </div>
        <div className="mt-4 rounded-xl border border-slate-100 p-4">
          <p className="text-sm font-bold text-ink">Pontos de atenção</p>
          <p className="mt-1 text-sm text-muted">
            {animal.name} precisa de adaptação gradual ao ficar sozinho(a).
          </p>
        </div>
      </Panel>

      <button onClick={() => navigate(-1)} className="text-sm font-medium text-adopter hover:underline">
        ← Voltar
      </button>
    </>
  );
}
