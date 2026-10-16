import { useEffect, useState } from "react";
import { Panel, Stat } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { getUsuario, listarManifestacoes, listarProcessos, listarRecomendacoes, listarVisitas } from "../../services/api";

function formatarDataHora(valor) {
  const d = new Date(String(valor).replace(" ", "T"));
  if (Number.isNaN(d.getTime())) return valor;
  return d.toLocaleString("pt-BR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function AdopterDashboard() {
  const usuario = getUsuario();
  const [recomendacoes, setRecomendacoes] = useState([]);
  const [manifestacoes, setManifestacoes] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [proximaVisita, setProximaVisita] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    Promise.all([listarRecomendacoes(), listarManifestacoes(), listarProcessos()])
      .then(async ([recs, manifs, procs]) => {
        setRecomendacoes(recs);
        setManifestacoes(manifs);
        setProcessos(procs);
        const emAndamento = procs.filter((p) => p.status === "Em Andamento");
        const todasVisitas = (
          await Promise.all(emAndamento.map((p) => listarVisitas(p.id).catch(() => [])))
        ).flat();
        const agendadas = todasVisitas
          .filter((v) => v.status === "Agendada")
          .sort((a, b) => new Date(a.data_visita) - new Date(b.data_visita));
        setProximaVisita(agendadas[0] || null);
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  const pendentes = manifestacoes.filter((m) => m.status === "Pendente").length;
  const emAndamento = processos.filter((p) => p.status === "Em Andamento");
  const primeiroNome = usuario ? usuario.nome.split(" ")[0] : "";

  const subtitulo =
    emAndamento.length > 0
      ? `Seu processo com ${emAndamento[0].nome_animal} está avançando`
      : "Explore os animais disponíveis e encontre seu novo melhor amigo";

  return (
    <Panel title={`Olá, ${primeiroNome}`} subtitle={subtitulo}>
      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}

      {!carregando && !erro && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Recomendações" value={recomendacoes.length} />
            <Stat
              label="Solicitações"
              value={manifestacoes.length}
              hint={pendentes > 0 ? `${pendentes} em análise` : undefined}
              hintTone="warn"
            />
            <Stat label="Processos em andamento" value={emAndamento.length} />
          </div>

          {proximaVisita ? (
            <div className="mt-4 flex items-center justify-between rounded-xl border border-slate-100 p-4">
              <div>
                <p className="text-sm font-bold text-ink">Próxima visita</p>
                <p className="mt-1 text-sm text-muted">{formatarDataHora(proximaVisita.data_visita)}</p>
              </div>
              <StatusBadge status={proximaVisita.status} />
            </div>
          ) : (
            <div className="mt-4 rounded-xl border border-slate-100 p-4">
              <p className="text-sm font-bold text-ink">
                {emAndamento.length > 0 ? "Nenhuma visita agendada ainda" : "Nenhum processo em andamento"}
              </p>
              <p className="mt-1 text-sm text-muted">
                {emAndamento.length > 0
                  ? "A instituição ainda vai marcar uma data para a visita."
                  : "Favorite animais e manifeste interesse para começar uma adoção."}
              </p>
            </div>
          )}
        </>
      )}
    </Panel>
  );
}
