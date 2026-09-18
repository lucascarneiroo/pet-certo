import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { institutions } from "../../data/mockData";

export default function AdminInstitutions() {
  return (
    <Panel title="Instituições" subtitle="Cadastro e validação de ONGs">
      <div className="space-y-3">
        {institutions.map((inst) => (
          <Row
            key={inst.id}
            title={`${inst.name} · ${inst.city}`}
            right={<StatusBadge status={inst.status} />}
          />
        ))}
      </div>
    </Panel>
  );
}
