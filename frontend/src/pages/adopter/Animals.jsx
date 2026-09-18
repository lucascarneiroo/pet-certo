import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { listarAnimais } from "../../services/api";

export default function AdopterAnimals() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [animals, setAnimals] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    listarAnimais()
      .then(setAnimals)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  const results = animals.filter((a) =>
    `${a.name} ${a.size} ${a.city}`.toLowerCase().includes(query.toLowerCase())
  );

  if (carregando) {
    return <Panel title="Encontre seu novo melhor amigo"><p className="text-sm text-muted">Carregando animais...</p></Panel>;
  }

  if (erro) {
    return (
      <Panel title="Encontre seu novo melhor amigo">
        <p className="text-sm text-red-600">
          Não foi possível carregar os animais: {erro}. Confira se o backend está rodando em localhost:8000.
        </p>
      </Panel>
    );
  }

  return (
    <>
      <Panel title="Encontre seu novo melhor amigo" subtitle="Dados reais do backend">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Busque por nome, porte ou cidade"
          className="mb-4 w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-ink outline-none focus:border-adopter"
        />
        <div className="grid gap-3 sm:grid-cols-2">
          {results.map((a) => (
            <button
              key={a.id}
              onClick={() => navigate(`/adotante/animais/${a.id}`)}
              className="rounded-xl border border-slate-100 p-4 text-left transition hover:border-adopter hover:shadow-sm"
            >
              <p className="text-sm font-bold text-ink">{a.name}</p>
              <p className="mt-0.5 text-xs text-muted">
                {a.age} · {a.size}
              </p>
              <StatusBadge status={a.status} />
            </button>
          ))}
          {results.length === 0 && (
            <p className="text-sm text-muted">Nenhum animal cadastrado ainda.</p>
          )}
        </div>
      </Panel>
    </>
  );
}
