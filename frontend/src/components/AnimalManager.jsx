import { useEffect, useState } from "react";
import { Panel, Row } from "./Panel";
import StatusBadge from "./StatusBadge";
import { listarAnimais, criarAnimal, atualizarAnimal, excluirAnimal } from "../services/api";

const ESPECIES = [
  { valor: "cachorro", rotulo: "Cão" },
  { valor: "gato", rotulo: "Gato" },
  { valor: "outro", rotulo: "Outro" },
];
const PORTES = [
  { valor: "pequeno", rotulo: "Pequeno" },
  { valor: "medio", rotulo: "Médio" },
  { valor: "grande", rotulo: "Grande" },
];
const ENERGIAS = [
  { valor: "baixo", rotulo: "Baixo" },
  { valor: "medio", rotulo: "Médio" },
  { valor: "alto", rotulo: "Alto" },
];
const ESPACOS = [
  { valor: "apartamento", rotulo: "Apartamento" },
  { valor: "casa_com_quintal", rotulo: "Casa com quintal" },
  { valor: "indiferente", rotulo: "Indiferente" },
];
const STATUS_OPCOES = [
  { valor: "disponivel", rotulo: "Disponível" },
  { valor: "em_processo", rotulo: "Em processo" },
  { valor: "adotado", rotulo: "Adotado" },
];

const FORM_VAZIO = {
  nome: "",
  especie: "cachorro",
  raca: "",
  porte: "medio",
  idade_anos: "",
  nivel_energia: "medio",
  temperamento: "",
  convive_criancas: false,
  convive_outros_pets: false,
  necessidades_especiais: "",
  espaco_recomendado: "indiferente",
  status: "disponivel",
};

// Painel completo de CRUD de animais. `podeExcluir` controla se o botão de
// excluir aparece — no backend, só o perfil admin pode excluir de fato
// (voluntário de instituição só cria/edita), então cada tela que usa esse
// componente passa esse valor de acordo com quem está logado.
export default function AnimalManager({ podeExcluir = false, corTema = "ong" }) {
  const [animais, setAnimais] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [mostrarForm, setMostrarForm] = useState(false);
  const [editandoId, setEditandoId] = useState(null);
  const [form, setForm] = useState(FORM_VAZIO);
  const [erroForm, setErroForm] = useState("");
  const [salvando, setSalvando] = useState(false);

  function carregar() {
    setCarregando(true);
    listarAnimais()
      .then(setAnimais)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }

  useEffect(carregar, []);

  function update(campo) {
    return (e) => {
      const valor = e.target.type === "checkbox" ? e.target.checked : e.target.value;
      setForm((f) => ({ ...f, [campo]: valor }));
    };
  }

  function abrirNovo() {
    setForm(FORM_VAZIO);
    setEditandoId(null);
    setErroForm("");
    setMostrarForm(true);
  }

  function abrirEdicao(animal) {
    const a = animal._original;
    setForm({
      nome: a.nome,
      especie: a.especie,
      raca: a.raca || "",
      porte: a.porte,
      idade_anos: String(a.idade_anos),
      nivel_energia: a.nivel_energia,
      temperamento: a.temperamento || "",
      convive_criancas: a.convive_criancas,
      convive_outros_pets: a.convive_outros_pets,
      necessidades_especiais: a.necessidades_especiais || "",
      espaco_recomendado: a.espaco_recomendado,
      status: a.status,
    });
    setEditandoId(a.id);
    setErroForm("");
    setMostrarForm(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErroForm("");
    setSalvando(true);
    try {
      const payload = { ...form, idade_anos: parseFloat(form.idade_anos || "0") };
      if (editandoId) {
        await atualizarAnimal(editandoId, payload);
      } else {
        delete payload.status; // no cadastro, o backend sempre começa como "disponivel"
        await criarAnimal(payload);
      }
      setMostrarForm(false);
      carregar();
    } catch (err) {
      setErroForm(err.message || "Não foi possível salvar o animal.");
    } finally {
      setSalvando(false);
    }
  }

  async function handleExcluir(id) {
    if (!confirm("Excluir este animal? Essa ação não pode ser desfeita.")) return;
    try {
      await excluirAnimal(id);
      carregar();
    } catch (err) {
      alert(err.message || "Não foi possível excluir.");
    }
  }

  const corBotao = corTema === "admin" ? "bg-admin hover:bg-admin-dark" : "bg-ong hover:bg-ong-dark";
  const corFoco = corTema === "admin" ? "focus:border-admin" : "focus:border-ong";

  if (mostrarForm) {
    return (
      <Panel title={editandoId ? "Editar animal" : "Cadastro de animal"} subtitle="Dados reais, salvos no backend">
        <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-3">
          <Campo label="Nome">
            <input value={form.nome} onChange={update("nome")} required
              className={`w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none ${corFoco}`} />
          </Campo>
          <CampoSelect label="Espécie" value={form.especie} onChange={update("especie")} opcoes={ESPECIES} corFoco={corFoco} />
          <Campo label="Raça (opcional)">
            <input value={form.raca} onChange={update("raca")}
              className={`w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none ${corFoco}`} />
          </Campo>

          <CampoSelect label="Porte" value={form.porte} onChange={update("porte")} opcoes={PORTES} corFoco={corFoco} />
          <Campo label="Idade (anos)">
            <input type="number" min="0" step="0.5" value={form.idade_anos} onChange={update("idade_anos")} required
              className={`w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none ${corFoco}`} />
          </Campo>
          <CampoSelect label="Nível de energia" value={form.nivel_energia} onChange={update("nivel_energia")} opcoes={ENERGIAS} corFoco={corFoco} />

          <CampoSelect label="Espaço recomendado" value={form.espaco_recomendado} onChange={update("espaco_recomendado")} opcoes={ESPACOS} corFoco={corFoco} />
          {editandoId && (
            <CampoSelect label="Status" value={form.status} onChange={update("status")} opcoes={STATUS_OPCOES} corFoco={corFoco} />
          )}

          <div className="flex items-end gap-4 sm:col-span-1">
            <label className="flex items-center gap-2 text-sm text-ink">
              <input type="checkbox" checked={form.convive_criancas} onChange={update("convive_criancas")} />
              Convive com crianças
            </label>
          </div>
          <div className="flex items-end gap-4 sm:col-span-2">
            <label className="flex items-center gap-2 text-sm text-ink">
              <input type="checkbox" checked={form.convive_outros_pets} onChange={update("convive_outros_pets")} />
              Convive com outros pets
            </label>
          </div>

          <div className="sm:col-span-3">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
              Temperamento
            </label>
            <textarea value={form.temperamento} onChange={update("temperamento")} rows={2}
              placeholder="Dócil, energia moderada, adaptação gradual a crianças."
              className={`w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none ${corFoco}`} />
          </div>
          <div className="sm:col-span-3">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
              Necessidades especiais (opcional)
            </label>
            <input value={form.necessidades_especiais} onChange={update("necessidades_especiais")}
              className={`w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none ${corFoco}`} />
          </div>

          {erroForm && <p className="text-xs font-semibold text-red-600 sm:col-span-3">{erroForm}</p>}

          <div className="flex gap-3 sm:col-span-3">
            <button type="submit" disabled={salvando}
              className={`rounded-lg px-4 py-2 text-sm font-semibold text-white transition disabled:opacity-60 ${corBotao}`}>
              {salvando ? "Salvando..." : "Salvar animal"}
            </button>
            <button type="button" onClick={() => setMostrarForm(false)}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink">
              Cancelar
            </button>
          </div>
        </form>
      </Panel>
    );
  }

  return (
    <Panel title="Gerenciamento de animais" subtitle="Dados reais do backend">
      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">Não foi possível carregar: {erro}</p>}

      {!carregando && !erro && (
        <div className="space-y-3">
          {animais.map((a) => (
            <Row
              key={a.id}
              title={a.name}
              subtitle={`${a.speciesTag} · ${a.age} · ${a.size}`}
              right={
                <div className="flex items-center gap-3">
                  <StatusBadge status={a.status} />
                  <button
                    onClick={() => abrirEdicao(a)}
                    className="text-xs font-semibold text-ink hover:underline"
                  >
                    Editar
                  </button>
                  {podeExcluir && (
                    <button
                      onClick={() => handleExcluir(a.id)}
                      className="text-xs font-semibold text-red-600 hover:underline"
                    >
                      Excluir
                    </button>
                  )}
                </div>
              }
            />
          ))}
          {animais.length === 0 && <p className="text-sm text-muted">Nenhum animal cadastrado ainda.</p>}
        </div>
      )}

      <button onClick={abrirNovo} className={`mt-5 rounded-lg px-4 py-2 text-sm font-semibold text-white transition ${corBotao}`}>
        Cadastrar animal
      </button>
    </Panel>
  );
}

function Campo({ label, children }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">{label}</label>
      {children}
    </div>
  );
}

function CampoSelect({ label, value, onChange, opcoes, corFoco }) {
  return (
    <Campo label={label}>
      <select value={value} onChange={onChange}
        className={`w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none ${corFoco}`}>
        {opcoes.map((o) => (
          <option key={o.valor} value={o.valor}>{o.rotulo}</option>
        ))}
      </select>
    </Campo>
  );
}
