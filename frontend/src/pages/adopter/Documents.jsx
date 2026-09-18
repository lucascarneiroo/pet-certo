import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";

const docs = [
  { id: 1, name: "RG ou CNH", status: "Aprovado" },
  { id: 2, name: "Comprovante de renda", status: "Aprovado" },
  { id: 3, name: "Comprovante de residência", detail: "Rejeitado · endereço ilegível", status: "Rejeitado" },
];

export default function AdopterDocuments() {
  return (
    <Panel title="Documentos" subtitle="Envie e acompanhe cada arquivo">
      <div className="space-y-3">
        {docs.map((d) => (
          <Row key={d.id} title={d.detail ? `${d.name}` : d.name} subtitle={d.detail} right={<StatusBadge status={d.status} />} />
        ))}
      </div>
      <button className="mt-5 rounded-lg bg-adopter px-4 py-2 text-sm font-semibold text-white transition hover:bg-adopter-dark">
        Enviar nova versão
      </button>
    </Panel>
  );
}
