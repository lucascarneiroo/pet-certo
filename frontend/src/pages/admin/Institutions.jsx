import { useEffect, useMemo, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import { listarInstituicoes } from "../../services/api";
import { exportarCsv } from "../../utils/exportarCsv";

export default function AdminInstitutions() {
  const [instituicoes, setInstituicoes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [busca, setBusca] = useState("");

  useEffect(() => {
    listarInstituicoes()
      .then(setInstituicoes)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  const filtradas = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    return instituicoes.filter(
      (i) => !termo || `${i.nome} ${i.localizacao}`.toLowerCase().includes(termo)
    );
  }, [instituicoes, busca]);

  function exportar() {
    exportarCsv(
      "instituicoes-pet-certo",
      [
        { chave: "id", titulo: "ID" },
        { chave: "nome", titulo: "Nome" },
        { chave: "email", titulo: "E-mail" },
        { chave: "cnpj", titulo: "CNPJ" },
        { chave: "localizacao", titulo: "Localização" },
      ],
      filtradas.map((i) => ({ id: i.id, nome: i.nome, email: i.email, cnpj: i.cnpj, localizacao: i.localizacao }))
    );
  }

  return (
    <Panel title="Instituições" subtitle={`${filtradas.length} de ${instituicoes.length} instituições cadastradas`}>
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <input
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Buscar por nome ou localização"
          className="min-w-[220px] flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink outline-none focus:border-admin"
        />
        <button
          onClick={exportar}
          disabled={filtradas.length === 0}
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink hover:border-admin disabled:opacity-60"
        >
          Exportar CSV
        </button>
      </div>

      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}
      {!carregando && !erro && filtradas.length === 0 && (
        <p className="text-sm text-muted">Nenhuma instituição encontrada com essa busca.</p>
      )}
      <div className="space-y-3">
        {filtradas.map((inst) => (
          <Row
            key={inst.id}
            title={inst.nome}
            subtitle={`${inst.email} · CNPJ ${inst.cnpj} · ${inst.localizacao}`}
          />
        ))}
      </div>
    </Panel>
  );
}
