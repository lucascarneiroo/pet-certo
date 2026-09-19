import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { listarAnimais } from "../../services/api";

export default function AdopterAnimals() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [animais, setAnimais] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    listarAnimais({ status: "Disponível" })
      .then(setAnimais)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  const results = animais.filter((a) =>
    `${a.name} ${a.institution} ${(a.caracteristicas || []).join(" ")}`.toLowerCase().includes(query.toLowerCase())
  );
  const ranked = [...animais].sort((a, b) => (b.compat || 0) - (a.compat || 0));

  return (
    <>
      <Panel title="Encontre seu novo melhor amigo" subtitle="Busca e apresentação da plataforma">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Busque por nome, característica ou instituição"
          className="mb-4 w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-ink outline-none focus:border-adopter"
        />
        {carregando && <p className="text-sm text-muted">Carregando animais...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        <div className="grid gap-3 sm:grid-cols-2">
          {results.map((a) => (
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

      <Panel title="Todos os animais disponíveis" subtitle="Lista completa vinda do backend">
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
