import { Link } from "react-router-dom";

const PROFILES = [
  {
    to: "/entrar?perfil=adotante",
    title: "Sou adotante",
    desc: "Encontre um animal compatível com sua rotina e acompanhe cada etapa do processo.",
    color: "text-adopter",
  },
  {
    to: "/entrar?perfil=instituicao",
    title: "Sou instituição / ONG",
    desc: "Gerencie animais, avalie solicitações e organize visitas em um só lugar.",
    color: "text-ong",
  },
  {
    to: "/entrar?perfil=administrador",
    title: "Sou administrador",
    desc: "Supervisione usuários, instituições e a saúde geral da plataforma.",
    color: "text-admin",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-canvas">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-ong" />
          <span className="text-sm font-extrabold tracking-tight text-ink">PET CERTO</span>
        </div>

        <section className="mt-10 rounded-2xl bg-white p-8 shadow-card sm:p-12">
          <h1 className="text-3xl font-extrabold leading-tight text-ink sm:text-4xl">
            Encontre seu novo melhor amigo
          </h1>
          <p className="mt-2 max-w-xl text-sm text-muted">
            Busca e apresentação da plataforma
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {PROFILES.map((p) => (
              <Link
                key={p.title}
                to={p.to}
                className="rounded-xl border border-slate-100 p-5 transition hover:-translate-y-0.5 hover:shadow-md"
              >
                <p className={`text-sm font-bold ${p.color}`}>{p.title}</p>
                <p className="mt-2 text-sm text-muted">{p.desc}</p>
              </Link>
            ))}
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/entrar"
              className="rounded-lg bg-adopter px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-adopter-dark"
            >
              Entrar
            </Link>
            <Link
              to="/cadastro"
              className="rounded-lg border border-adopter px-5 py-2.5 text-sm font-semibold text-adopter transition hover:bg-adopter-soft"
            >
              Cadastrar-se
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
