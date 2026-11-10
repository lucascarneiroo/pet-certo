import { Link } from "react-router-dom";
import Logo from "../components/Logo";

const PROFILES = [
  {
    to: "/entrar?perfil=adotante",
    title: "Sou adotante",
    desc: "Encontre um animal compatível com sua rotina e acompanhe cada etapa do processo.",
    color: "text-adopter",
    dot: "bg-adopter",
  },
  {
    to: "/entrar?perfil=instituicao",
    title: "Sou instituição / ONG",
    desc: "Gerencie animais, avalie solicitações e organize visitas em um só lugar.",
    color: "text-ong",
    dot: "bg-ong",
  },
  {
    to: "/entrar?perfil=administrador",
    title: "Sou administrador",
    desc: "Supervisione usuários, instituições e a saúde geral da plataforma.",
    color: "text-admin",
    dot: "bg-admin",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-canvas">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <Logo size="md" />

        <section className="relative mt-10 overflow-hidden rounded-3xl bg-white p-8 shadow-lift ring-1 ring-black/[0.03] sm:p-14">
          <div
            className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full opacity-20 blur-3xl"
            style={{ background: "radial-gradient(circle, #F08A5D, transparent 70%)" }}
          />
          <div
            className="pointer-events-none absolute -bottom-24 -left-16 h-64 w-64 rounded-full opacity-20 blur-3xl"
            style={{ background: "radial-gradient(circle, #6A4C8C, transparent 70%)" }}
          />

          <div className="relative">
            <span className="inline-flex items-center rounded-full bg-brand-soft px-3 py-1 text-xs font-semibold text-brand-dark">
              Adoção responsável, feita simples
            </span>
            <h1 className="mt-4 text-4xl font-black leading-[1.05] tracking-tight text-adopter sm:text-6xl">
              Encontre seu
              <br />
              novo melhor amigo!
            </h1>
            <p className="mt-4 max-w-xl text-lg text-muted">
              Conectamos adotantes e instituições com compatibilidade de verdade — do primeiro
              favorito até a adoção concluída.
            </p>

            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              {PROFILES.map((p) => (
                <Link
                  key={p.title}
                  to={p.to}
                  className="group rounded-2xl border border-slate-100 p-5 transition hover:-translate-y-1 hover:border-transparent hover:shadow-lift"
                >
                  <span className={`inline-block h-2.5 w-2.5 rounded-full ${p.dot}`} />
                  <p className={`mt-3 text-sm font-bold ${p.color}`}>{p.title}</p>
                  <p className="mt-2 text-sm text-muted">{p.desc}</p>
                  <span className={`mt-3 inline-flex items-center text-xs font-semibold ${p.color} opacity-0 transition group-hover:opacity-100`}>
                    Começar →
                  </span>
                </Link>
              ))}
            </div>

            <div className="mt-10 flex flex-wrap gap-3">
              <Link
                to="/entrar"
                className="rounded-full bg-adopter px-7 py-3.5 text-sm font-bold text-white shadow-soft transition hover:-translate-y-0.5 hover:bg-adopter-dark hover:shadow-lift"
              >
                Entrar
              </Link>
              <Link
                to="/cadastro"
                className="rounded-full border-2 border-adopter px-7 py-3.5 text-sm font-bold text-adopter transition hover:-translate-y-0.5 hover:bg-adopter-soft"
              >
                Cadastrar-se
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
