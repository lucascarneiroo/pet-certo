import { useEffect, useState } from "react";
import { Panel, Stat } from "../../components/Panel";
import { listarAnimais, listarInstituicoes, listarProcessos } from "../../services/api";

export default function AdminDashboard() {
  const [instituicoes, setInstituicoes] = useState([]);
  const [animais, setAnimais] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    Promise.all([listarInstituicoes(), listarAnimais(), listarProcessos()])
      .then(([insts, ans, procs]) => {
        setInstituicoes(insts);
        setAnimais(ans);
        setProcessos(procs);
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  const ativos = processos.filter((p) => p.status === "Em Andamento").length;
  const concluidos = processos.filter((p) => p.status === "Concluído").length;

  return (
    <Panel title="Dashboard administrativo" subtitle="Visão geral da plataforma">
      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}

      {!carregando && !erro && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Instituições" value={instituicoes.length} />
            <Stat label="Animais cadastrados" value={animais.length} />
            <Stat label="Processos ativos" value={ativos} hint={`${concluidos} concluídos`} />
          </div>

          <div className="mt-4 rounded-xl border border-slate-100 p-4">
            <p className="text-sm font-bold text-ink">Saúde operacional</p>
            <span className="mt-2 inline-flex items-center rounded-full bg-admin-soft px-3 py-1 text-xs font-semibold text-admin">
              API conectada ao PostgreSQL
            </span>
          </div>
        </>
      )}
    </Panel>
  );
}
