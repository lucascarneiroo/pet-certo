import { useEffect, useMemo, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import {
  atualizarAnimal,
  criarAnimal,
  getUsuario,
  listarAnimais,
  listarTagsPadrao,
} from "../../services/api";
import { exportarCsv } from "../../utils/exportarCsv";

// valores canônicos usados pelo fluxo de adoção (ver backend/database/adocao_repository.py)
const STATUS_OPCOES = ["Disponível", "Em Processo", "Adotado"];

const formVazio = { nome: "", data_nascimento: "", tags: [] };

// separa as etiquetas padrão em categorias de escolha única ("Porte: Pequeno", "Porte: Médio"...)
// e etiquetas booleanas soltas ("Convive com Crianças"), a partir do texto de cada etiqueta.
function agruparTags(tags) {
  const categorias = new Map();
  const booleanas = [];
  for (const tag of tags) {
    const indice = tag.indexOf(": ");
    if (indice === -1) {
      booleanas.push(tag);
      continue;
    }
    const categoria = tag.slice(0, indice);
    if (!categorias.has(categoria)) categorias.set(categoria, []);
    categorias.get(categoria).push(tag);
  }
  return { categorias, booleanas };
}

export default function OngAnimals() {
  const usuario = getUsuario();

  const [animais, setAnimais] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erroLista, setErroLista] = useState("");
  const [busca, setBusca] = useState("");

  const [tagsDisponiveis, setTagsDisponiveis] = useState([]);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [editandoId, setEditandoId] = useState(null);
  const [form, setForm] = useState(formVazio);
  const [erroForm, setErroForm] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    listarTagsPadrao()
      .then(setTagsDisponiveis)
      .catch(() => setTagsDisponiveis([]));
  }, []);

  useEffect(() => {
    if (!usuario) {
      setCarregando(false);
      return;
    }
    const timer = setTimeout(() => {
      setCarregando(true);
      setErroLista("");
      listarAnimais({ id_instituicao: usuario.id, busca: busca || undefined })
        .then(setAnimais)
        .catch((err) => setErroLista(err.message))
        .finally(() => setCarregando(false));
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busca]);

  const { categorias, booleanas } = useMemo(() => agruparTags(tagsDisponiveis), [tagsDisponiveis]);

  function recarregar() {
    return listarAnimais({ id_instituicao: usuario.id, busca: busca || undefined }).then(setAnimais);
  }

  function alternarTagBooleana(tag) {
    setForm((f) => ({
      ...f,
      tags: f.tags.includes(tag) ? f.tags.filter((t) => t !== tag) : [...f.tags, tag],
    }));
  }

  function selecionarCategoria(tagsDaCategoria, valor) {
    setForm((f) => ({
      ...f,
      tags: [...f.tags.filter((t) => !tagsDaCategoria.includes(t)), ...(valor ? [valor] : [])],
    }));
  }

  function novoCadastro() {
    setForm(formVazio);
    setEditandoId(null);
    setErroForm("");
    setMostrarForm(true);
  }

  function editar(animal) {
    setForm({
      nome: animal.name || "",
      data_nascimento: animal.dataNascimento || "",
      tags: animal.caracteristicas || [],
    });
    setEditandoId(animal.id);
    setErroForm("");
    setMostrarForm(true);
  }

  async function salvar(e) {
    e.preventDefault();
    const nome = form.nome.trim();
    if (!nome) {
      setErroForm("Informe o nome do animal.");
      return;
    }
    setErroForm("");
    setSalvando(true);
    try {
      const dados = { nome, data_nascimento: form.data_nascimento || null, caracteristicas: form.tags };
      if (editandoId) {
        await atualizarAnimal(editandoId, dados);
      } else {
        await criarAnimal(dados);
      }
      setMostrarForm(false);
      setForm(formVazio);
      setEditandoId(null);
      await recarregar();
    } catch (err) {
      setErroForm(err.message);
    } finally {
      setSalvando(false);
    }
  }

  async function mudarStatus(animal, novoStatus) {
    if (novoStatus === animal.status) return;
    setErroLista("");
    try {
      await atualizarAnimal(animal.id, { status: novoStatus });
      await recarregar();
    } catch (err) {
      setErroLista(err.message);
    }
  }

  if (!usuario) {
    return (
      <Panel title="Gerenciamento de animais">
        <p className="text-sm text-muted">Faça login como instituição para gerenciar seus animais.</p>
      </Panel>
    );
  }

  if (mostrarForm) {
    return (
      <Panel
        title={editandoId ? "Editar animal" : "Cadastro de animal"}
        subtitle={editandoId ? "Atualize os dados e as características" : "Novo perfil para recomendação"}
      >
        <form onSubmit={salvar} className="space-y-4">
          {erroForm && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{erroForm}</p>}

          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              label="Nome"
              value={form.nome}
              onChange={(e) => setForm((f) => ({ ...f, nome: e.target.value }))}
              placeholder="Mel"
            />
            <Field
              label="Data de nascimento"
              type="date"
              value={form.data_nascimento || ""}
              onChange={(e) => setForm((f) => ({ ...f, data_nascimento: e.target.value }))}
            />
          </div>

          {categorias.size > 0 && (
            <div className="grid gap-4 sm:grid-cols-3">
              {[...categorias.entries()].map(([categoria, tagsDaCategoria]) => (
                <div key={categoria}>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
                    {categoria}
                  </label>
                  <select
                    value={form.tags.find((t) => tagsDaCategoria.includes(t)) || ""}
                    onChange={(e) => selecionarCategoria(tagsDaCategoria, e.target.value)}
                    className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-ong"
                  >
                    <option value="">Selecione...</option>
                    {tagsDaCategoria.map((tag) => (
                      <option key={tag} value={tag}>
                        {tag.slice(categoria.length + 2)}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          )}

          {booleanas.length > 0 && (
            <div>
              <label className="mb-2 block text-xs font-semibold uppercase tracking-wide text-muted">
                Outras características
              </label>
              <div className="flex flex-wrap gap-3">
                {booleanas.map((tag) => (
                  <label
                    key={tag}
                    className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
                  >
                    <input type="checkbox" checked={form.tags.includes(tag)} onChange={() => alternarTagBooleana(tag)} />
                    {tag}
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={salvando}
              className="rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark disabled:opacity-60"
            >
              {salvando ? "Salvando..." : "Salvar animal"}
            </button>
            <button
              type="button"
              onClick={() => setMostrarForm(false)}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink"
            >
              Cancelar
            </button>
          </div>
        </form>
      </Panel>
    );
  }

  function exportar() {
    exportarCsv(
      "meus-animais-pet-certo",
      [
        { chave: "id", titulo: "ID" },
        { chave: "nome", titulo: "Nome" },
        { chave: "status", titulo: "Situação" },
        { chave: "caracteristicas", titulo: "Características" },
      ],
      animais.map((a) => ({
        id: a.id,
        nome: a.name,
        status: a.status,
        caracteristicas: (a.caracteristicas || []).join(", "),
      }))
    );
  }

  return (
    <Panel title="Gerenciamento de animais" subtitle="Cadastro, edição e situação dos animais da instituição">
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <input
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Buscar pelo nome do animal"
          className="min-w-[220px] flex-1 rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-ink outline-none focus:border-ong"
        />
        <button
          onClick={exportar}
          disabled={animais.length === 0}
          className="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-semibold text-ink hover:border-ong disabled:opacity-60"
        >
          Exportar CSV
        </button>
      </div>

      {carregando && <p className="text-sm text-muted">Carregando animais...</p>}
      {erroLista && <p className="text-sm text-red-600">{erroLista}</p>}
      {!carregando && !erroLista && animais.length === 0 && (
        <p className="text-sm text-muted">Nenhum animal encontrado.</p>
      )}

      <div className="space-y-3">
        {animais.map((a) => (
          <Row
            key={a.id}
            title={a.name}
            subtitle={(a.caracteristicas || []).join(" · ") || "Sem características cadastradas"}
            right={
              <div className="flex items-center gap-2">
                <select
                  value={a.status}
                  onChange={(e) => mudarStatus(a, e.target.value)}
                  className="rounded-lg border border-slate-200 px-2 py-1.5 text-xs text-ink"
                >
                  {STATUS_OPCOES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
                <StatusBadge status={a.status} />
                <button
                  onClick={() => editar(a)}
                  className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:border-ong"
                >
                  Editar
                </button>
              </div>
            }
          />
        ))}
      </div>

      <button
        onClick={novoCadastro}
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
      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">{label}</label>
      <input
        {...props}
        className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-ong"
      />
    </div>
  );
}
