import { useEffect, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import {
  agendarVisita,
  atualizarVisita,
  criarHorarioVisita,
  getUsuario,
  listarEtapas,
  listarHorariosDisponiveis,
  listarProcessos,
  listarVisitas,
} from "../../services/api";

function formatarDataHora(valor) {
  const d = new Date(String(valor).replace(" ", "T"));
  return Number.isNaN(d.getTime()) ? valor : d.toLocaleString("pt-BR");
}

export default function OngVisits() {
  const usuario = getUsuario();
  const [horarios, setHorarios] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [etapasPorProcesso, setEtapasPorProcesso] = useState({});
  const [visitasPorProcesso, setVisitasPorProcesso] = useState({});
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const [novoHorario, setNovoHorario] = useState("");
  const [erroHorario, setErroHorario] = useState("");
  const [salvandoHorario, setSalvandoHorario] = useState(false);

  const [selecaoHorario, setSelecaoHorario] = useState({});
  const [agendando, setAgendando] = useState(null);
  const [erroAgendar, setErroAgendar] = useState("");

  function carregar() {
    if (!usuario) return Promise.resolve();
    setCarregando(true);
    setErro("");
    return Promise.all([listarHorariosDisponiveis(usuario.id), listarProcessos()])
      .then(async ([listaHorarios, listaProcessos]) => {
        setHorarios(listaHorarios);
        setProcessos(listaProcessos);
        const emAndamento = listaProcessos.filter((p) => p.status === "Em Andamento");
        const etapasEntries = await Promise.all(
          emAndamento.map((p) => listarEtapas(p.id).then((e) => [p.id, e]).catch(() => [p.id, []]))
        );
        setEtapasPorProcesso(Object.fromEntries(etapasEntries));
        const visitasEntries = await Promise.all(
          emAndamento.map((p) => listarVisitas(p.id).then((v) => [p.id, v]).catch(() => [p.id, []]))
        );
        setVisitasPorProcesso(Object.fromEntries(visitasEntries));
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleCriarHorario(e) {
    e.preventDefault();
    if (!novoHorario) {
      setErroHorario("Escolha uma data e horário.");
      return;
    }
    setErroHorario("");
    setSalvandoHorario(true);
    try {
      await criarHorarioVisita(usuario.id, novoHorario);
      setNovoHorario("");
      await carregar();
    } catch (err) {
      setErroHorario(err.message);
    } finally {
      setSalvandoHorario(false);
    }
  }

  async function handleAgendar(processoId) {
    const idHorario = selecaoHorario[processoId];
    if (!idHorario) return;
    setErroAgendar("");
    setAgendando(processoId);
    try {
      await agendarVisita(processoId, Number(idHorario));
      await carregar();
    } catch (err) {
      setErroAgendar(err.message);
    } finally {
      setAgendando(null);
    }
  }

  async function handleMarcarVisita(visitaId, status) {
    setErro("");
    try {
      await atualizarVisita(visitaId, status, status === "Realizada" ? "Visita realizada." : "Visita cancelada.");
      await carregar();
    } catch (err) {
      setErro(err.message);
    }
  }

  const processosEmVisita = processos
    .filter((p) => p.status === "Em Andamento")
    .filter((p) => {
      const atual = (etapasPorProcesso[p.id] || []).find((e) => e.status === "Em Andamento");
      return atual && atual.nome === "Visita";
    });

  const todasVisitas = processos
    .filter((p) => p.status === "Em Andamento")
    .flatMap((p) => (visitasPorProcesso[p.id] || []).map((v) => ({ ...v, processo: p })));

  return (
    <>
      <Panel title="Horários disponíveis" subtitle="Datas e horários que a instituição oferece para visitas">
        <form onSubmit={handleCriarHorario} className="mb-4 flex flex-wrap items-end gap-3">
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
              Novo horário
            </label>
            <input
              type="datetime-local"
              value={novoHorario}
              onChange={(e) => setNovoHorario(e.target.value)}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink outline-none focus:border-ong"
            />
          </div>
          <button
            type="submit"
            disabled={salvandoHorario}
            className="rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark disabled:opacity-60"
          >
            {salvandoHorario ? "Salvando..." : "Adicionar horário"}
          </button>
        </form>
        {erroHorario && <p className="mb-3 text-sm text-red-600">{erroHorario}</p>}

        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && !erro && horarios.length === 0 && (
          <p className="text-sm text-muted">Nenhum horário disponível cadastrado.</p>
        )}
        <div className="space-y-3">
          {horarios.map((h) => (
            <Row key={h.id} title={formatarDataHora(h.data_hora)} right={<StatusBadge status={h.status} />} />
          ))}
        </div>
      </Panel>

      <Panel title="Processos aguardando visita" subtitle="Escolha um horário disponível para cada um">
        {!carregando && processosEmVisita.length === 0 && (
          <p className="text-sm text-muted">Nenhum processo aguardando agendamento de visita no momento.</p>
        )}
        <div className="space-y-4">
          {processosEmVisita.map((p) => (
            <div key={p.id} className="rounded-xl border border-slate-100 p-4">
              <p className="text-sm font-bold text-ink">
                {p.nome_adotante} × {p.nome_animal}
              </p>
              <div className="mt-3 flex flex-wrap items-center gap-3">
                <select
                  value={selecaoHorario[p.id] || ""}
                  onChange={(e) => setSelecaoHorario((s) => ({ ...s, [p.id]: e.target.value }))}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
                >
                  <option value="">Selecione um horário...</option>
                  {horarios.map((h) => (
                    <option key={h.id} value={h.id}>
                      {formatarDataHora(h.data_hora)}
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => handleAgendar(p.id)}
                  disabled={!selecaoHorario[p.id] || agendando === p.id}
                  className="rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark disabled:opacity-60"
                >
                  {agendando === p.id ? "Agendando..." : "Agendar visita"}
                </button>
              </div>
            </div>
          ))}
          {erroAgendar && <p className="text-sm text-red-600">{erroAgendar}</p>}
        </div>
      </Panel>

      <Panel title="Visitas agendadas" subtitle="Marque como realizada ou cancelada depois do dia">
        {todasVisitas.length === 0 && !carregando && (
          <p className="text-sm text-muted">Nenhuma visita agendada ainda.</p>
        )}
        <div className="space-y-3">
          {todasVisitas.map((v) => (
            <Row
              key={v.id}
              title={`${v.processo.nome_adotante} × ${v.processo.nome_animal}`}
              subtitle={formatarDataHora(v.data_visita)}
              right={
                <div className="flex items-center gap-2">
                  <StatusBadge status={v.status} />
                  {v.status === "Agendada" && (
                    <>
                      <button
                        onClick={() => handleMarcarVisita(v.id, "Realizada")}
                        className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:border-ong"
                      >
                        Realizada
                      </button>
                      <button
                        onClick={() => handleMarcarVisita(v.id, "Cancelada")}
                        className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:border-ong"
                      >
                        Cancelar
                      </button>
                    </>
                  )}
                </div>
              }
            />
          ))}
        </div>
      </Panel>
    </>
  );
}
