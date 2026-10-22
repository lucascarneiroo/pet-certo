import { useEffect, useMemo, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { excluirAnimal, listarAnimais, listarProcessos, listarRegistrosAdmin } from "../../services/api";
import { exportarCsv } from "../../utils/exportarCsv";

const STATUS_ANIMAL = ["Disponível", "Em Processo", "Adotado"];
const STATUS_PROCESSO = ["Em Andamento", "Concluído", "Cancelado"];

export default function AdminAnimals() {
  const [animais, setAnimais] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [registros, setRegistros] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [excluindoId, setExcluindoId] = useState(null);

  const [buscaAnimal, setBuscaAnimal] = useState("");
  const [statusAnimal, setStatusAnimal] = useState("");
  const [statusProcesso, setStatusProcesso] = useState("");

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

  const animaisFiltrados = useMemo(() => {
    const termo = buscaAnimal.trim().toLowerCase();
    return animais.filter((a) => {
      const bateBusca = !termo || `${a.name} ${a.institution}`.toLowerCase().includes(termo);
      const bateStatus = !statusAnimal || a.status === statusAnimal;
      return bateBusca && bateStatus;
    });
  }, [animais, buscaAnimal, statusAnimal]);

  const processosFiltrados = useMemo(
    () => processos.filter((p) => !statusProcesso || p.status === statusProcesso),
    [processos, statusProcesso]
  );

  function exportarAnimais() {
    exportarCsv(
      "animais-pet-certo",
      [
        { chave: "id", titulo: "ID" },
        { chave: "nome", titulo: "Nome" },
        { chave: "instituicao", titulo: "Instituição" },
        { chave: "status", titulo: "Situação" },
        { chave: "caracteristicas", titulo: "Características" },
      ],
      animaisFiltrados.map((a) => ({
        id: a.id,
        nome: a.name,
        instituicao: a.institution,
        status: a.status,
        caracteristicas: (a.caracteristicas || []).join(", "),
      }))
    );
  }

  function exportarProcessos() {
    exportarCsv(
      "processos-de-adocao-pet-certo",
      [
        { chave: "id", titulo: "Processo" },
        { chave: "animal", titulo: "Animal" },
        { chave: "adotante", titulo: "Adotante" },
        { chave: "status", titulo: "Situação" },
      ],
      processosFiltrados.map((p) => ({
        id: p.id,
        animal: p.nome_animal,
        adotante: p.nome_adotante,
        status: p.status,
      }))
    );
  }

  return (
    <>
      <Panel title="Animais" subtitle={`${animaisFiltrados.length} de ${animais.length} animais cadastrados na plataforma`}>
        <div className="mb-4 flex flex-wrap items-end gap-3">
          <input
            value={buscaAnimal}
            onChange={(e) => setBuscaAnimal(e.target.value)}
            placeholder="Buscar por nome do animal ou instituição"
            className="min-w-[220px] flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink outline-none focus:border-admin"
          />
          <select
            value={statusAnimal}
            onChange={(e) => setStatusAnimal(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
          >
            <option value="">Todas as situações</option>
            {STATUS_ANIMAL.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <button
            onClick={exportarAnimais}
            disabled={animaisFiltrados.length === 0}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink hover:border-admin disabled:opacity-60"
          >
            Exportar CSV
          </button>
        </div>

        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && !erro && animaisFiltrados.length === 0 && (
          <p className="text-sm text-muted">Nenhum animal encontrado com esses filtros.</p>
        )}
        <div className="space-y-3">
          {animaisFiltrados.map((a) => (
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

      <Panel title="Processos de adoção" subtitle={`${processosFiltrados.length} de ${processos.length} processos`}>
        <div className="mb-4 flex flex-wrap items-end gap-3">
          <select
            value={statusProcesso}
            onChange={(e) => setStatusProcesso(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
          >
            <option value="">Todas as situações</option>
            {STATUS_PROCESSO.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <button
            onClick={exportarProcessos}
            disabled={processosFiltrados.length === 0}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink hover:border-admin disabled:opacity-60"
          >
            Exportar CSV
          </button>
        </div>

        {!carregando && processosFiltrados.length === 0 && (
          <p className="text-sm text-muted">Nenhum processo encontrado com esse filtro.</p>
        )}
        <div className="space-y-3">
          {processosFiltrados.map((p) => (
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
