import { useEffect, useMemo, useState } from "react";
import { Panel, ProgressBar, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import {
  aprovarManifestacao,
  buscarCompatibilidadeDaManifestacao,
  listarManifestacoes,
  recusarManifestacao,
} from "../../services/api";
import { exportarCsv } from "../../utils/exportarCsv";

const STATUS_MANIFESTACAO = ["Pendente", "Aprovada", "Recusada"];

export default function OngRequests() {
  const [manifestacoes, setManifestacoes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [statusFiltro, setStatusFiltro] = useState("");

  const [selecionadaId, setSelecionadaId] = useState(null);
  const [compat, setCompat] = useState(null);
  const [carregandoCompat, setCarregandoCompat] = useState(false);
  const [erroCompat, setErroCompat] = useState("");

  const [processando, setProcessando] = useState(false);
  const [erroAcao, setErroAcao] = useState("");

  function carregar() {
    setCarregando(true);
    setErro("");
    return listarManifestacoes()
      .then(setManifestacoes)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    carregar();
  }, []);

  const selecionada = manifestacoes.find((m) => m.id === selecionadaId) || null;

  const manifestacoesFiltradas = useMemo(
    () => manifestacoes.filter((m) => !statusFiltro || m.status === statusFiltro),
    [manifestacoes, statusFiltro]
  );

  function exportar() {
    exportarCsv(
      "manifestacoes-de-interesse-pet-certo",
      [
        { chave: "id", titulo: "ID" },
        { chave: "adotante", titulo: "Adotante" },
        { chave: "animal", titulo: "Animal" },
        { chave: "status", titulo: "Situação" },
        { chave: "data", titulo: "Manifestada em" },
      ],
      manifestacoesFiltradas.map((m) => ({
        id: m.id,
        adotante: m.nome_adotante,
        animal: m.nome_animal,
        status: m.status,
        data: m.data_manifestacao,
      }))
    );
  }

  useEffect(() => {
    if (!selecionada) {
      setCompat(null);
      return;
    }
    setCarregandoCompat(true);
    setErroCompat("");
    buscarCompatibilidadeDaManifestacao(selecionada.id)
      .then(setCompat)
      .catch((err) => setErroCompat(err.message))
      .finally(() => setCarregandoCompat(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selecionadaId]);

  async function aceitar() {
    setErroAcao("");
    setProcessando(true);
    try {
      await aprovarManifestacao(selecionada.id);
      setSelecionadaId(null);
      await carregar();
    } catch (err) {
      setErroAcao(err.message);
    } finally {
      setProcessando(false);
    }
  }

  async function rejeitar() {
    setErroAcao("");
    setProcessando(true);
    try {
      await recusarManifestacao(selecionada.id);
      setSelecionadaId(null);
      await carregar();
    } catch (err) {
      setErroAcao(err.message);
    } finally {
      setProcessando(false);
    }
  }

  return (
    <>
      <Panel title="Solicitações recebidas" subtitle={`${manifestacoesFiltradas.length} de ${manifestacoes.length} manifestações de interesse`}>
        <div className="mb-4 flex flex-wrap items-end gap-3">
          <select
            value={statusFiltro}
            onChange={(e) => setStatusFiltro(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
          >
            <option value="">Todas as situações</option>
            {STATUS_MANIFESTACAO.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <button
            onClick={exportar}
            disabled={manifestacoesFiltradas.length === 0}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink hover:border-ong disabled:opacity-60"
          >
            Exportar CSV
          </button>
        </div>

        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && !erro && manifestacoesFiltradas.length === 0 && (
          <p className="text-sm text-muted">Nenhuma manifestação encontrada com esse filtro.</p>
        )}
        <div className="space-y-3">
          {manifestacoesFiltradas.map((m) => (
            <Row
              key={m.id}
              title={`${m.nome_adotante} → ${m.nome_animal}`}
              subtitle={`Manifestada em ${m.data_manifestacao}`}
              onClick={() => setSelecionadaId(m.id)}
              className={selecionadaId === m.id ? "border-ong" : ""}
              right={<StatusBadge status={m.status} />}
            />
          ))}
        </div>
      </Panel>

      {selecionada && (
        <Panel title="Análise do adotante" subtitle={`${selecionada.nome_adotante} × ${selecionada.nome_animal}`}>
          {carregandoCompat && <p className="text-sm text-muted">Calculando compatibilidade...</p>}
          {erroCompat && <p className="text-sm text-red-600">{erroCompat}</p>}
          {compat && (
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-slate-100 p-4">
                <p className="text-sm font-bold text-ink">Compatibilidade calculada</p>
                <span className="mt-2 inline-flex items-center rounded-full bg-[#E4F3E9] px-3 py-1 text-xs font-semibold text-[#2F7A50]">
                  {compat.score}% compatível
                </span>
                <p className="mt-3 text-xs text-muted">
                  Calculada pelo núcleo de compatibilidade a partir dos animais que este adotante já favoritou.
                </p>
              </div>
              <div className="rounded-xl border border-slate-100 p-4">
                <p className="mb-3 text-sm font-bold text-ink">Principais fatores</p>
                <div className="space-y-3">
                  {compat.fatores.slice(0, 4).map((f) => (
                    <ProgressBar
                      key={f.criterio}
                      label={`${f.criterio} (${f.valor_do_animal})`}
                      value={Math.round(f.afinidade_pct)}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          {erroAcao && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{erroAcao}</p>}

          {selecionada.status === "Pendente" ? (
            <div className="mt-4 flex gap-3">
              <button
                onClick={aceitar}
                disabled={processando}
                className="rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark disabled:opacity-60"
              >
                {processando ? "Processando..." : "Aceitar solicitação"}
              </button>
              <button
                onClick={rejeitar}
                disabled={processando}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink disabled:opacity-60"
              >
                Rejeitar
              </button>
            </div>
          ) : (
            <p className="mt-4 text-sm font-semibold text-muted">
              Esta manifestação já foi {selecionada.status === "Aprovada" ? "aprovada" : "recusada"}.
            </p>
          )}
        </Panel>
      )}
    </>
  );
}
