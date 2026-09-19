import { useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { animals as initialAnimals } from "../../data/mockData";

const emptyForm = {
  nome: "",
  especie: "Cão",
  idade: "",
  porte: "Pequeno",
  situacao: "Disponível",
  comportamento: "",
};

export default function OngAnimals() {
  const [animals, setAnimals] = useState(initialAnimals);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setAnimals((list) => [
      ...list,
      {
        id: form.nome.toLowerCase().replace(/\s+/g, "-") || `novo-${list.length}`,
        name: form.nome || "Novo animal",
        species: form.especie,
        speciesTag: form.especie.toUpperCase(),
        breed: "SRD",
        age: form.idade,
        size: form.porte,
        status: form.situacao,
        institution: "Instituto Amor Animal",
        city: "Recife",
        compat: 0,
        temperament: form.comportamento,
        behavior: form.comportamento,
      },
    ]);
    setForm(emptyForm);
    setShowForm(false);
  }

  if (showForm) {
    return (
      <Panel title="Cadastro de Animal" subtitle="Novo perfil para recomendação">
        <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-3">
          <Field label="Nome" value={form.nome} onChange={update("nome")} placeholder="Mel" />
          <Field label="Espécie" value={form.especie} onChange={update("especie")} placeholder="Cão" />
          <Field label="Idade" value={form.idade} onChange={update("idade")} placeholder="1 ano" />
          <Field label="Porte" value={form.porte} onChange={update("porte")} placeholder="Pequeno" />
          <Field label="Situação" value={form.situacao} onChange={update("situacao")} placeholder="Disponível" />
          <div className="sm:col-span-3">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
              Comportamento e necessidades
            </label>
            <textarea
              value={form.comportamento}
              onChange={update("comportamento")}
              placeholder="Dócil, energia moderada, adaptação gradual a crianças."
              rows={2}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-ong"
            />
          </div>
          <div className="flex gap-3 sm:col-span-3">
            <button
              type="submit"
              className="rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark"
            >
              Salvar animal
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink"
            >
              Cancelar
            </button>
          </div>
        </form>
      </Panel>
    );
  }

  return (
    <Panel title="Gerenciamento de animais" subtitle="Cadastro e situação dos animais">
      <div className="space-y-3">
        {animals.map((a) => (
          <Row
            key={a.id}
            title={a.name}
            subtitle={`${a.speciesTag} · ${a.age} · ${a.size}`}
            right={<StatusBadge status={a.status} />}
          />
        ))}
      </div>
      <button
        onClick={() => setShowForm(true)}
        className="mt-5 rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark"
      >
        Cadastrar animal
      </button>
    </Panel>
  );
}

function Field({ label, ...props }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
        {label}
      </label>
      <input
        {...props}
        className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-ong"
      />
    </div>
  );
}
