import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Panel, ProgressBar } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import {
  buscarAnimal,
  buscarCompatibilidade,
  desfavoritarAnimal,
  favoritarAnimal,
  getUsuario,
  listarFavoritos,
  manifestarInteresse,
} from "../../services/api";

export default function AnimalDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const usuario = getUsuario();

  const [animal, setAnimal] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const [compat, setCompat] = useState(null);
  const [erroCompat, setErroCompat] = useState("");

  const [enviando, setEnviando] = useState(false);
  const [erroInteresse, setErroInteresse] = useState("");
  const [enviado, setEnviado] = useState(false);

  const [favoritado, setFavoritado] = useState(false);
  const [alterandoFavorito, setAlterandoFavorito] = useState(false);
  const [erroFavorito, setErroFavorito] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    buscarAnimal(id)
      .then(setAnimal)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, [id]);

  function recarregarCompatibilidade() {
    if (!usuario || usuario.perfil !== "adotante") return;
    buscarCompatibilidade(id)
      .then(setCompat)
      .catch((err) => setErroCompat(err.message));
  }

  useEffect(() => {
    recarregarCompatibilidade();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, usuario]);

  useEffect(() => {
    if (!usuario || usuario.perfil !== "adotante") return;
    listarFavoritos()
      .then((favoritos) => setFavoritado(favoritos.some((f) => f.id_animal === Number(id))))
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, usuario]);

  async function handleFavoritar() {
    setErroFavorito("");
    setAlterandoFavorito(true);
    try {
      if (favoritado) {
        await desfavoritarAnimal(Number(id));
        setFavoritado(false);
      } else {
        await favoritarAnimal(Number(id));
        setFavoritado(true);
      }
      recarregarCompatibilidade(); // favoritar muda a preferência aprendida do adotante
    } catch (err) {
      setErroFavorito(err.message);
    } finally {
      setAlterandoFavorito(false);
    }
  }

  async function handleManifestarInteresse() {
    setErroInteresse("");
    setEnviando(true);
    try {
      await manifestarInteresse(Number(id));
      setEnviado(true);
    } catch (err) {
      setErroInteresse(err.message);
    } finally {
      setEnviando(false);
    }
  }

  if (carregando) {
    return (
      <Panel>
        <p className="text-sm text-muted">Carregando animal...</p>
      </Panel>
    );
  }

  if (erro || !animal) {
    return (
      <Panel>
        <p className="text-sm text-red-600">{erro || "Animal não encontrado."}</p>
        <button onClick={() => navigate(-1)} className="mt-3 text-sm font-medium text-adopter hover:underline">
          ← Voltar
        </button>
      </Panel>
    );
  }

  return (
    <>
      <Panel>
        <div className="grid gap-6 sm:grid-cols-[220px_1fr]">
          <div className="flex aspect-square items-center justify-center rounded-xl bg-adopter-soft text-sm font-semibold text-adopter">
            {animal.name}
          </div>
          <div>
            <h2 className="text-xl font-extrabold text-ink">{animal.name}</h2>
            <p className="text-sm text-muted">{(animal.caracteristicas || []).join(" · ")}</p>
            <div className="mt-2">
              <StatusBadge status={animal.status} />
            </div>

            <div className="mt-4 rounded-xl border border-slate-100 p-4">
              <p className="text-sm font-bold text-ink">Instituição</p>
              <p className="mt-1 text-sm text-muted">{animal.institution}</p>
            </div>

            {erroFavorito && (
              <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{erroFavorito}</p>
            )}
            {erroInteresse && (
              <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{erroInteresse}</p>
            )}

            {usuario && usuario.perfil === "adotante" && (
              <button
                onClick={handleFavoritar}
                disabled={alterandoFavorito}
                className={`mt-4 mr-3 rounded-lg border px-4 py-2 text-sm font-semibold transition disabled:opacity-60 ${
                  favoritado
                    ? "border-adopter bg-adopter-soft text-adopter"
                    : "border-slate-200 text-ink hover:border-adopter"
                }`}
              >
                {favoritado ? "★ Favoritado" : "☆ Favoritar"}
              </button>
            )}

            {!usuario ? (
              <p className="mt-4 text-sm text-muted">Entre como adotante para manifestar interesse.</p>
            ) : !enviado ? (
              <button
                onClick={handleManifestarInteresse}
                disabled={enviando || animal.status !== "Disponível"}
                className="mt-4 rounded-lg bg-adopter px-4 py-2 text-sm font-semibold text-white transition hover:bg-adopter-dark disabled:opacity-60"
              >
                {enviando ? "Enviando..." : "Manifestar interesse"}
              </button>
            ) : (
              <p className="mt-4 text-sm font-semibold text-[#2F7A50]">
                Interesse enviado para {animal.institution}.
              </p>
            )}
            {usuario && animal.status !== "Disponível" && !enviado && (
              <p className="mt-2 text-xs text-muted">Este animal não está disponível no momento.</p>
            )}
          </div>
        </div>
      </Panel>

      <Panel title={`Compatibilidade com ${animal.name}`} subtitle="Resultado calculado a partir dos seus favoritos">
        {erroCompat && <p className="text-sm text-red-600">{erroCompat}</p>}
        {!compat && !erroCompat && (
          <p className="text-sm text-muted">
            {usuario && usuario.perfil === "adotante"
              ? "Calculando..."
              : "Entre como adotante para ver sua compatibilidade com este animal."}
          </p>
        )}
        {compat && (
          <>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="flex flex-col items-start justify-center rounded-xl border border-slate-100 p-4">
                <p className="text-3xl font-extrabold text-[#2F7A50]">{compat.score}%</p>
                <p className="mt-1 text-sm text-muted">
                  {compat.score >= 70
                    ? "Excelente combinação"
                    : compat.score >= 40
                      ? "Combinação razoável"
                      : "Combinação fraca"}
                </p>
              </div>
              <div className="rounded-xl border border-slate-100 p-4">
                <p className="mb-3 text-sm font-bold text-ink">Fatores que mais pesaram</p>
                <div className="space-y-3">
                  {compat.fatores.slice(0, 3).map((f) => (
                    <ProgressBar
                      key={f.criterio}
                      label={`${f.criterio} (${f.valor_do_animal})`}
                      value={Math.round(f.afinidade_pct)}
                    />
                  ))}
                </div>
              </div>
            </div>
            <div className="mt-4 rounded-xl border border-slate-100 p-4">
              <p className="text-sm font-bold text-ink">Todos os critérios considerados</p>
              <ul className="mt-2 space-y-1 text-sm text-muted">
                {compat.fatores.map((f) => (
                  <li key={f.criterio}>
                    {f.criterio}: {f.valor_do_animal} — {f.afinidade_pct}% de afinidade (peso {f.peso_pct}%)
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </Panel>

      <button onClick={() => navigate(-1)} className="text-sm font-medium text-adopter hover:underline">
        ← Voltar
      </button>
    </>
  );
}
