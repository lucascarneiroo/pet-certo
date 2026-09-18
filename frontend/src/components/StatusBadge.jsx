const TONES = {
  green: "bg-[#E4F3E9] text-[#2F7A50]",
  amber: "bg-[#FBF0DC] text-[#9A6B1E]",
  red: "bg-[#FBE7E7] text-[#B03A3A]",
  blue: "bg-[#E3EEF7] text-[#2C6E9E]",
  purple: "bg-[#F0E9F8] text-[#6C4F92]",
  gray: "bg-[#EEF0F2] text-[#5B6472]",
};

const STATUS_TONE = {
  Verificada: "green",
  Ativo: "green",
  Disponível: "green",
  Aprovado: "green",
  Concluído: "purple",
  "Concluída": "purple",
  Adotado: "blue",
  Pendente: "amber",
  "Em processo": "amber",
  "Em análise": "amber",
  Revisão: "amber",
  Revisar: "amber",
  "Documentos pendentes": "amber",
  Agendada: "blue",
  Reagendada: "amber",
  Bloqueado: "red",
  Rejeitado: "red",
  "Rejeitada": "red",
  "Alta compatibilidade": "green",
};

export default function StatusBadge({ status, tone }) {
  const resolved = tone || STATUS_TONE[status] || "gray";
  return (
    <span
      className={`inline-flex shrink-0 items-center rounded-full px-3 py-1 text-xs font-semibold ${TONES[resolved]}`}
    >
      {status}
    </span>
  );
}
