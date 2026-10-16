import { useEffect, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { listarUsuarios } from "../../services/api";

const ROTULO_PERFIL = { adotante: "Adotante", instituicao: "Instituição", administrador: "Administrador" };
const COR_PERFIL = { adotante: "purple", instituicao: "blue", administrador: "green" };

export default function AdminUsers() {
  const [usuarios, setUsuarios] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    listarUsuarios()
      .then(setUsuarios)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  return (
    <Panel title="Gerenciamento de usuários" subtitle={`${usuarios.length} usuários cadastrados`}>
      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}
      {!carregando && !erro && usuarios.length === 0 && (
        <p className="text-sm text-muted">Nenhum usuário cadastrado ainda.</p>
      )}
      <div className="space-y-3">
        {usuarios.map((u) => (
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
