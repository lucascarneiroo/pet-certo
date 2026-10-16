import { useEffect, useState } from "react";
import { Panel, Row } from "../../components/Panel";
import { listarDocumentos, listarProcessos } from "../../services/api";

export default function OngDocuments() {
  const [processos, setProcessos] = useState([]);
  const [selecionadoId, setSelecionadoId] = useState(null);
  const [documentos, setDocumentos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [carregandoDocs, setCarregandoDocs] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    setCarregando(true);
    setErro("");
    listarProcessos()
      .then(setProcessos)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregando(false));
  }, []);

  useEffect(() => {
    if (!selecionadoId) {
      setDocumentos([]);
      return;
    }
    setCarregandoDocs(true);
    listarDocumentos(selecionadoId)
      .then(setDocumentos)
      .catch((err) => setErro(err.message))
      .finally(() => setCarregandoDocs(false));
  }, [selecionadoId]);

  return (
    <>
      <Panel title="Processos" subtitle="Selecione um processo para ver os documentos enviados">
        {carregando && <p className="text-sm text-muted">Carregando...</p>}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {!carregando && processos.length === 0 && (
          <p className="text-sm text-muted">Nenhum processo de adoção ainda.</p>
        )}
        <div className="space-y-3">
          {processos.map((p) => (
            <Row
              key={p.id}
              title={`${p.nome_adotante} × ${p.nome_animal}`}
              subtitle={`Processo #${p.id}`}
              onClick={() => setSelecionadoId(p.id)}
              className={selecionadoId === p.id ? "border-ong" : ""}
              right={<span className="text-xs text-muted">{p.status}</span>}
            />
          ))}
        </div>
      </Panel>

      {selecionadoId && (
        <Panel title="Documentos enviados" subtitle={`Processo #${selecionadoId}`}>
          {carregandoDocs && <p className="text-sm text-muted">Carregando...</p>}
          {!carregandoDocs && documentos.length === 0 && (
            <p className="text-sm text-muted">Nenhum documento enviado ainda para este processo.</p>
          )}
          <div className="space-y-3">
            {documentos.map((d) => (
              <Row key={d.id} title={d.nome} subtitle={d.caminho_arquivo} />
            ))}
          </div>
        </Panel>
      )}
    </>
  );
}
