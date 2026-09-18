import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import AnimalManager from "../../components/AnimalManager";
import { requests } from "../../data/mockData";

export default function AdminAnimals() {
  return (
    <>
      {/* Admin tem permissão total no backend (criar, editar e excluir),
          por isso aqui aparece o botão de excluir — diferente da tela
          equivalente da instituição. */}
      <AnimalManager podeExcluir={true} corTema="admin" />

      <Panel title="Processos de adoção (visão geral)" subtitle="Ainda usando dados de exemplo — pendente de conectar ao backend">
        <div className="space-y-3">
          {requests.map((r) => (
            <Row
              key={r.id}
              title={`${r.animal} · Amor Animal · ${
                r.status === "Concluído" ? `Processo #${r.id}` : `Solicitação #${r.id}`
              }`}
              right={<StatusBadge status={r.status} />}
            />
          ))}
        </div>
      </Panel>
    </>
  );
}

