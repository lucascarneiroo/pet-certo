import { Panel, Row } from "../../components/Panel";
import StatusBadge from "../../components/StatusBadge";
import { users } from "../../data/mockData";

export default function AdminUsers() {
  return (
    <Panel title="Gerenciamento de usuários" subtitle="Adotantes, equipes e permissões">
      <div className="space-y-3">
        {users.map((u) => (
          <Row
            key={u.id}
            title={`${u.name} · ${u.role} · ${u.email}`}
            right={<StatusBadge status={u.status} />}
          />
        ))}
        <Row title="Conta sinalizada · tentativas inválidas" right={<StatusBadge status="Bloqueado" />} />
      </div>

      <button className="mt-5 rounded-lg bg-admin px-4 py-2 text-sm font-semibold text-white transition hover:bg-admin-dark">
        Gerenciar permissões
      </button>
    </Panel>
  );
}
