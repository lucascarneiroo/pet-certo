import { useEffect, useState } from "react";
import { Panel, Stat } from "../../components/Panel";
import { getUsuario, listarAnimais, listarProcessos, listarVisitas } from "../../services/api";

function formatarDataHora(valor) {
  const d = new Date(String(valor).replace(" ", "T"));
  if (Number.isNaN(d.getTime())) return valor;
  return d.toLocaleString("pt-BR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}

function mesmoDia(valor, referencia) {
  const d = new Date(String(valor).replace(" ", "T"));
  return !Number.isNaN(d.getTime()) && d.toDateString() === referencia.toDateString();
}

export default function OngDashboard() {
  const usuario = getUsuario();
  const [animais, setAnimais] = useState([]);
  const [visitasHoje, setVisitasHoje] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    if (!usuario) return;
    setCarregando(true);
    setErro("");
    Promise.all([listarAnimais({ id_instituicao: usuario.id }), listarProcessos()])
      .then(async ([listaAnimais, listaProcessos]) => {
        setAnimais(listaAnimais);
        const emAndamento = listaProcessos.filter((p) => p.status === "Em Andamento");
        const todasVisitas = (
          await Promise.all(emAndamento.map((p) => listarVisitas(p.id).catch(() => [])))
        ).flat();
        const hoje = new Date();
        setVisitasHoje(
          todasVisitas
            .filter((v) => v.status === "Agendada" && mesmoDia(v.data_visita, hoje))
            .sort((a, b) => new Date(a.data_visita) - new Date(b.data_visita))
        );
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, [usuario]);

  const disponiveis = animais.filter((a) => a.status === "Disponível").length;
  const emProcesso = animais.filter((a) => a.status === "Em Processo").length;
  const adotados = animais.filter((a) => a.status === "Adotado").length;

  return (
    <Panel title="Dashboard da instituição" subtitle={usuario ? usuario.nome : ""}>
      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}

      {!carregando && !erro && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Disponíveis" value={disponiveis} />
            <Stat label="Em processo" value={emProcesso} />
            <Stat label="Adotados" value={adotados} />
          </div>

          <div className="mt-4 rounded-xl border border-slate-100 p-4">
            <p className="text-sm font-bold text-ink">Agenda de hoje</p>
            {visitasHoje.length === 0 ? (
              <p className="mt-1 text-sm text-muted">Nenhuma visita agendada para hoje.</p>
            ) : (
              <p className="mt-1 text-sm text-muted">
                {visitasHoje.map((v) => formatarDataHora(v.data_visita)).join(" · ")}
              </p>
            )}
          </div>
        </>
      )}
    </Panel>
  );
}
