import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { documents, requests } from "../../data/mockData";

export default function OngDocuments() {
  return (
    <Panel title="Análise de documentos" subtitle={`Solicitação #${requests[0].id}`}>
      <div className="space-y-3">
        {documents.map((d) => (
          <Row key={d.id} title={`${d.name} · ${d.detail}`} right={<StatusBadge status={d.status} />} />
        ))}
      </div>
      <div className="mt-4 flex gap-3">
        <button className="rounded-lg bg-ong px-4 py-2 text-sm font-semibold text-white transition hover:bg-ong-dark">
          Aprovar documento
        </button>
        <button className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink">
          Rejeitar com motivo
        </button>
      </div>
    </Panel>
  );
}
