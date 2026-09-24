import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { listarAnimais, listarTagsPadrao } from "../../services/api";

// categorias de etiquetas oferecidas como filtro rápido nesta tela
const CATEGORIAS_FILTRO = ["Espécie", "Porte", "Energia", "Espaço"];

function agruparTagsDeFiltro(tags) {
  const categorias = new Map();
  for (const tag of tags) {
    const indice = tag.indexOf(": ");
    if (indice === -1) continue;
    const categoria = tag.slice(0, indice);
    if (!CATEGORIAS_FILTRO.includes(categoria)) continue;
    if (!categorias.has(categoria)) categorias.set(categoria, []);
    categorias.get(categoria).push(tag);
  }
  return categorias;
}

export default function AdopterAnimals() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [filtros, setFiltros] = useState({}); // categoria -> etiqueta selecionada
  const [tagsDisponiveis, setTagsDisponiveis] = useState([]);
  const [animais, setAnimais] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    listarTagsPadrao()
      .then(setTagsDisponiveis)
      .catch(() => setTagsDisponiveis([]));
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setCarregando(true);
      setErro("");
      listarAnimais({
        status: "Disponível",
        busca: query || undefined,
        caracteristicas: Object.values(filtros).filter(Boolean),
      })
        .then(setAnimais)
        .catch((err) => setErro(err.message))
        .finally(() => setCarregando(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [query, filtros]);

  const categoriasDeFiltro = useMemo(() => agruparTagsDeFiltro(tagsDisponiveis), [tagsDisponiveis]);
  const ranked = [...animais].sort((a, b) => (b.compat || 0) - (a.compat || 0));

  return (
    <>
      <Panel title="Encontre seu novo melhor amigo" subtitle="Busca e filtros vindos do backend">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Busque por nome do animal"
          className="mb-4 w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-ink outline-none focus:border-adopter"
        />

        {categoriasDeFiltro.size > 0 && (
          <div className="mb-4 grid gap-3 sm:grid-cols-4">
            {[...categoriasDeFiltro.entries()].map(([categoria, tagsDaCategoria]) => (
              <div key={categoria}>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
                  {categoria}
                </label>
                <select
                  value={filtros[categoria] || ""}
                  onChange={(e) =>
                    setFiltros((f) => ({ ...f, [categoria]: e.target.value || undefined }))
                  }
                  className="w-full rounded-lg border border-slate-200 px-2 py-2 text-sm text-ink outline-none focus:border-adopter"
                >
                  <option value="">Todos</option>
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

        {carregando && <p className="text-sm text-muted">Carregando animais...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && !erro && animais.length === 0 && (
          <p className="text-sm text-muted">Nenhum animal encontrado com esses filtros.</p>
        )}

        <div className="grid gap-3 sm:grid-cols-2">
          {animais.map((a) => (
            <button
              key={a.id}
              onClick={() => navigate(`/adotante/animais/${a.id}`)}
              className="rounded-xl border border-slate-100 p-4 text-left transition hover:border-adopter hover:shadow-sm"
            >
              <p className="text-sm font-bold text-ink">{a.name}</p>
              <p className="mt-0.5 text-xs text-muted">
                {(a.caracteristicas || []).slice(0, 2).join(" · ") || a.institution}
              </p>
              {typeof a.compat === "number" && (
                <span className="mt-2 inline-flex items-center rounded-full bg-[#E4F3E9] px-3 py-1 text-xs font-semibold text-[#2F7A50]">
                  {a.compat}% compatível
                </span>
              )}
            </button>
          ))}
        </div>
      </Panel>

      <Panel title="Todos os animais disponíveis" subtitle="Lista completa vinda do backend, já com os filtros acima">
        <div className="space-y-3">
          {ranked.map((a, i) => (
            <Row
              key={a.id}
              title={`${i + 1}. ${a.name}`}
              subtitle={(a.caracteristicas || []).join(" · ") || a.institution}
              onClick={() => navigate(`/adotante/animais/${a.id}`)}
              right={<StatusBadge status={a.status} tone="green" />}
            />
          ))}
        </div>
      </Panel>
    </>
  );
}
