import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Panel } from "../../components/Panel";
import { getUsuario, listarAnimais, listarRecomendacoes, listarTagsPadrao } from "../../services/api";

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
  const usuario = getUsuario();
  const [query, setQuery] = useState("");
  const [filtros, setFiltros] = useState({}); // categoria -> etiqueta selecionada
  const [tagsDisponiveis, setTagsDisponiveis] = useState([]);
  const [animais, setAnimais] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const [recomendados, setRecomendados] = useState([]);
  const [carregandoRecs, setCarregandoRecs] = useState(false);
  const [erroRecs, setErroRecs] = useState("");

  useEffect(() => {
    listarTagsPadrao()
      .then(setTagsDisponiveis)
      .catch(() => setTagsDisponiveis([]));
  }, []);

  useEffect(() => {
    if (!usuario || usuario.perfil !== "adotante") return;
    setCarregandoRecs(true);
    listarRecomendacoes()
      .then(setRecomendados)
      .catch((err) => setErroRecs(err.message))
      .finally(() => setCarregandoRecs(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  return (
    <>
      {usuario && usuario.perfil === "adotante" && (
        <Panel
          title="Recomendados para você"
          subtitle="Ranking gerado pelo núcleo de compatibilidade, a partir dos animais que você favoritou"
        >
          {carregandoRecs && <p className="text-sm text-muted">Calculando recomendações...</p>}
          {erroRecs && <p className="text-sm text-red-600">{erroRecs}</p>}
          {!carregandoRecs && !erroRecs && recomendados.length === 0 && (
            <p className="text-sm text-muted">
              Favorite alguns animais para receber recomendações personalizadas.
            </p>
          )}
          <div className="grid gap-4 sm:grid-cols-2">
            {recomendados.map((a, i) => (
              <button
                key={a.id}
                onClick={() => navigate(`/adotante/animais/${a.id}`)}
                className="group overflow-hidden rounded-2xl border border-slate-100 bg-white text-left transition hover:-translate-y-1 hover:shadow-lift"
              >
                <div className="aspect-[4/3] w-full overflow-hidden bg-adopter-soft">
                  {a.foto && (
                    <img
                      src={a.foto}
                      alt={a.name}
                      className="h-full w-full object-cover object-top transition duration-300 group-hover:scale-105"
                      onError={(e) => { e.currentTarget.style.display = "none"; }}
                    />
                  )}
                </div>
                <div className="p-4">
                  <p className="text-base font-extrabold text-adopter">
                    #{i + 1} · {a.name}
                  </p>
                  <p className="mt-0.5 text-xs text-muted">
                    {(a.caracteristicas || []).slice(0, 2).join(" · ") || a.institution}
                  </p>
                  <span className="mt-2 inline-flex items-center rounded-full bg-[#E4F3E9] px-3 py-1 text-xs font-semibold text-[#2F7A50]">
                    {a.compat}% compatível
                  </span>
                </div>
              </button>
            ))}
          </div>
        </Panel>
      )}

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

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {animais.map((a) => (
            <button
              key={a.id}
              onClick={() => navigate(`/adotante/animais/${a.id}`)}
              className="group overflow-hidden rounded-2xl border border-slate-100 bg-white text-left transition hover:-translate-y-1 hover:shadow-lift"
            >
              <div className="aspect-[4/3] w-full overflow-hidden bg-adopter-soft">
                {a.foto && (
                  <img
                    src={a.foto}
                    alt={a.name}
                    className="h-full w-full object-cover object-top transition duration-300 group-hover:scale-105"
                    onError={(e) => { e.currentTarget.style.display = "none"; }}
                  />
                )}
              </div>
              <div className="p-4">
                <p className="text-lg font-extrabold text-adopter">{a.name}</p>
                <p className="mt-0.5 text-sm text-muted">{a.institution}</p>
                {a.caracteristicas?.length > 0 && (
                  <p className="mt-1.5 truncate text-xs text-muted">
                    {a.caracteristicas.slice(0, 2).join(" · ")}
                  </p>
                )}
              </div>
            </button>
          ))}
        </div>
      </Panel>
    </>
  );
}
