const states = [
  { tag: "Loading", tone: "gray", title: "Carregando recomendações", desc: "Buscando os melhores perfis para você…" },
  { tag: "Vazio", tone: "gray", title: "Nenhum favorito ainda", desc: "Salve animais para comparar depois." },
  { tag: "Erro", tone: "red", title: "Não foi possível carregar", desc: "Verifique sua conexão e tente novamente.", action: "Tentar novamente" },
  { tag: "Pendente", tone: "amber", title: "Documento em análise", desc: "Retorno previsto em até 2 dias úteis." },
  { tag: "Aprovado", tone: "green", title: "Documento aprovado", desc: "Etapa concluída com sucesso." },
  { tag: "Rejeitado", tone: "red", title: "Documento rejeitado", desc: "Endereço ilegível. Envie uma nova versão.", action: "Enviar nova versão" },
  { tag: "Concluído", tone: "purple", title: "Adoção concluída", desc: "Luna agora faz parte da família de Marina!" },
];

const TONE_CLASSES = {
  gray: "bg-[#EEF0F2] text-[#5B6472]",
  red: "bg-[#FBE7E7] text-[#B03A3A]",
  amber: "bg-[#FBF0DC] text-[#9A6B1E]",
  green: "bg-[#E4F3E9] text-[#2F7A50]",
  purple: "bg-[#F0E9F8] text-[#6C4F92]",
};

export default function SystemStates() {
  return (
    <div className="min-h-screen bg-canvas">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-extrabold text-ink">Estados do sistema</h1>
        <p className="mt-1 text-sm text-muted">
          Feedbacks consistentes para loading, vazio, erro e todos os status do processo.
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {states.map((s) => (
            <div key={s.title} className="rounded-2xl bg-white p-5 shadow-card">
              <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${TONE_CLASSES[s.tone]}`}>
                {s.tag}
              </span>
              <p className="mt-3 text-sm font-bold text-ink">{s.title}</p>
              <p className="mt-1 text-sm text-muted">{s.desc}</p>
              {s.action && (
                <button className="mt-3 rounded-lg bg-adopter px-3 py-1.5 text-xs font-semibold text-white">
                  {s.action}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
