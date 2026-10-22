import { useEffect, useMemo, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { listarUsuarios } from "../../services/api";
import { exportarCsv } from "../../utils/exportarCsv";

const ROTULO_PERFIL = { adotante: "Adotante", instituicao: "Instituição", administrador: "Administrador" };
const COR_PERFIL = { adotante: "purple", instituicao: "blue", administrador: "green" };

export default function AdminUsers() {
  const [usuarios, setUsuarios] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [busca, setBusca] = useState("");
  const [perfil, setPerfil] = useState("");

  useEffect(() => {
    listarUsuarios()
      .then(setUsuarios)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  const filtrados = useMemo(() => {
    const termo = busca.trim().toLowerCase();
    return usuarios.filter((u) => {
      const bateBusca = !termo || `${u.nome} ${u.email}`.toLowerCase().includes(termo);
      const batePerfil = !perfil || u.perfil === perfil;
      return bateBusca && batePerfil;
    });
  }, [usuarios, busca, perfil]);

  function exportar() {
    exportarCsv(
      "usuarios-pet-certo",
      [
        { chave: "id", titulo: "ID" },
        { chave: "nome", titulo: "Nome" },
        { chave: "email", titulo: "E-mail" },
        { chave: "perfil", titulo: "Perfil" },
      ],
      filtrados.map((u) => ({ id: u.id, nome: u.nome, email: u.email, perfil: ROTULO_PERFIL[u.perfil] || u.perfil }))
    );
  }

  return (
    <Panel title="Gerenciamento de usuários" subtitle={`${filtrados.length} de ${usuarios.length} usuários cadastrados`}>
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <input
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Buscar por nome ou e-mail"
          className="min-w-[220px] flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink outline-none focus:border-admin"
        />
        <select
          value={perfil}
          onChange={(e) => setPerfil(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-ink"
        >
          <option value="">Todos os perfis</option>
          {Object.entries(ROTULO_PERFIL).map(([valor, rotulo]) => (
            <option key={valor} value={valor}>{rotulo}</option>
          ))}
        </select>
        <button
          onClick={exportar}
          disabled={filtrados.length === 0}
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink hover:border-admin disabled:opacity-60"
        >
          Exportar CSV
        </button>
      </div>

      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}
      {!carregando && !erro && filtrados.length === 0 && (
        <p className="text-sm text-muted">Nenhum usuário encontrado com esses filtros.</p>
      )}
      <div className="space-y-3">
        {filtrados.map((u) => (
          <Row
            key={u.id}
            title={u.nome}
            subtitle={u.email}
            right={<StatusBadge status={ROTULO_PERFIL[u.perfil] || u.perfil} tone={COR_PERFIL[u.perfil]} />}
          />
        ))}
      </div>
    </Panel>
  );
}
