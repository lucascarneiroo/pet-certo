import { useEffect, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import { listarInstituicoes } from "../../services/api";

export default function AdminInstitutions() {
  const [instituicoes, setInstituicoes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    listarInstituicoes()
      .then(setInstituicoes)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  return (
    <Panel title="Instituições" subtitle={`${instituicoes.length} instituições cadastradas`}>
      {carregando && <p className="text-sm text-muted">Carregando...</p>}
      {erro && <p className="text-sm text-red-600">{erro}</p>}
      {!carregando && !erro && instituicoes.length === 0 && (
        <p className="text-sm text-muted">Nenhuma instituição cadastrada ainda.</p>
      )}
      <div className="space-y-3">
        {instituicoes.map((inst) => (
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
