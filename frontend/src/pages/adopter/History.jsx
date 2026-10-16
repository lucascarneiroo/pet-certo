import { useEffect, useState } from "react";
import { Panel } from "../../components/Panel";
import { getUsuario, listarHistoricoProcesso, listarProcessos } from "../../services/api";

export default function AdopterHistory() {
  const usuario = getUsuario();
  const [eventos, setEventos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    listarProcessos()
      .then(async (processos) => {
        const porProcesso = await Promise.all(
          processos.map((p) =>
            listarHistoricoProcesso(p.id)
              .then((historico) => historico.map((h) => ({ ...h, nome_animal: p.nome_animal, processo_id: p.id })))
              .catch(() => [])
          )
        );
        const todos = porProcesso.flat().sort((a, b) => new Date(b.data_hora) - new Date(a.data_hora));
        setEventos(todos);
      })
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  return (
    <>
      <Panel title="Meu perfil" subtitle="Dados usados pelo núcleo de compatibilidade">
        {usuario ? (
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl border border-slate-100 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">Nome</p>
              <p className="mt-1 text-sm text-ink">{usuario.nome}</p>
            </div>
            <div className="rounded-xl border border-slate-100 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">E-mail</p>
              <p className="mt-1 text-sm text-ink">{usuario.email}</p>
            </div>
            <div className="rounded-xl border border-slate-100 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">CPF</p>
              <p className="mt-1 text-sm text-ink">{usuario.cpf || "—"}</p>
            </div>
            <div className="rounded-xl border border-slate-100 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">Endereço</p>
              <p className="mt-1 text-sm text-ink">{usuario.endereco || "—"}</p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted">Faça login para ver seu perfil.</p>
        )}
        <p className="mt-4 text-xs text-muted">
          A compatibilidade com cada animal é aprendida a partir dos animais que você favorita — veja o painel
          "Compatibilidade" na página de cada animal.
        </p>
      </Panel>

      <Panel title="Histórico do processo" subtitle="Registro rastreável de todas as suas adoções">
        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && !erro && eventos.length === 0 && (
          <p className="text-sm text-muted">Nenhum evento registrado ainda — isso aparece assim que você iniciar um processo de adoção.</p>
        )}
        <div className="space-y-3">
          {eventos.map((h) => (
            <div key={h.id} className="rounded-xl border border-slate-100 px-4 py-3 text-sm text-ink">
              <span className="text-muted">{h.data_hora} · </span>
              {h.nome_animal} · {h.acao}
              {h.mudanca ? ` · ${h.mudanca}` : ""}
            </div>
          ))}
        </div>
      </Panel>
    </>
  );
}
