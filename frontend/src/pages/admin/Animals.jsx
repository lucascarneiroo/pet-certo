import { useEffect, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { excluirAnimal, listarAnimais, listarProcessos, listarRegistrosAdmin } from "../../services/api";

export default function AdminAnimals() {
  const [animais, setAnimais] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [registros, setRegistros] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [excluindoId, setExcluindoId] = useState(null);

  function carregar() {
    setCarregando(true);
    setErro("");
    return Promise.all([listarAnimais(), listarProcessos(), listarRegistrosAdmin()])
      .then(([ans, procs, regs]) => {
        setAnimais(ans);
        setProcessos(procs);
        setRegistros(regs);
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    carregar();
  }, []);

  async function handleExcluir(id) {
    if (!window.confirm("Excluir este animal? Essa ação não pode ser desfeita.")) return;
    setExcluindoId(id);
    try {
      await excluirAnimal(id);
      await carregar();
    } catch (err) {
      setErro(err.message);
    } finally {
      setExcluindoId(null);
    }
  }

  return (
    <>
      <Panel title="Animais" subtitle={`${animais.length} animais cadastrados na plataforma`}>
        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && !erro && animais.length === 0 && (
          <p className="text-sm text-muted">Nenhum animal cadastrado ainda.</p>
        )}
        <div className="space-y-3">
          {animais.map((a) => (
            <Row
              key={a.id}
              title={`${a.name} · ${a.institution}`}
              subtitle={(a.caracteristicas || []).join(" · ")}
              right={
                <div className="flex items-center gap-2">
                  <StatusBadge status={a.status} />
                  <button
                    onClick={() => handleExcluir(a.id)}
                    disabled={excluindoId === a.id}
                    className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:border-red-300 hover:text-red-600 disabled:opacity-60"
                  >
                    {excluindoId === a.id ? "Excluindo..." : "Excluir"}
                  </button>
                </div>
              }
            />
          ))}
        </div>
      </Panel>

      <Panel title="Processos de adoção" subtitle={`${processos.length} processos no total`}>
        {!carregando && processos.length === 0 && (
          <p className="text-sm text-muted">Nenhum processo de adoção iniciado ainda.</p>
        )}
        <div className="space-y-3">
          {processos.map((p) => (
            <Row
              key={p.id}
              title={`${p.nome_animal} · ${p.nome_adotante} · Processo #${p.id}`}
              right={<StatusBadge status={p.status} />}
            />
          ))}
        </div>
      </Panel>

      <div className="rounded-2xl bg-white p-6 shadow-card">
        <p className="text-sm font-bold text-ink">Registros administrativos</p>
        {registros.length === 0 ? (
          <p className="mt-1 text-xs text-muted">Nenhum registro ainda.</p>
        ) : (
          <div className="mt-3 space-y-2">
            {registros.slice(0, 20).map((r) => (
              <p key={r.id} className="text-xs text-muted">
                {r.data_hora} · {r.tipo_atividade}
                {r.descricao ? ` · ${r.descricao}` : ""}
              </p>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
