import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { login } from "../services/api";
import Logo from "../components/Logo";

const DESTINATIONS = {
  adotante: "/adotante",
  instituicao: "/instituicao",
  administrador: "/admin",
};

export default function Login() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const perfil = params.get("perfil") || "adotante";
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      const usuario = await login(email, senha);
      navigate(DESTINATIONS[usuario.perfil] || "/adotante");
    } catch (err) {
      setErro(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex justify-center">
          <Logo size="md" />
        </div>
        <div className="rounded-3xl bg-white p-8 shadow-lift ring-1 ring-black/[0.03]">
          <h1 className="text-xl font-extrabold text-ink">Entrar</h1>
          <p className="mt-1 text-sm text-muted">Acesse sua conta Pet Certo</p>

          {erro && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{erro}</p>}

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
                E-mail
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none transition focus:border-adopter focus:ring-2 focus:ring-adopter/15"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
                Senha
              </label>
              <input
                type="password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none transition focus:border-adopter focus:ring-2 focus:ring-adopter/15"
              />
            </div>
            <button
              type="submit"
              disabled={enviando}
              className="w-full rounded-xl bg-adopter py-2.5 text-sm font-semibold text-white shadow-soft transition hover:-translate-y-0.5 hover:bg-adopter-dark hover:shadow-lift disabled:translate-y-0 disabled:opacity-60"
            >
              {enviando ? "Entrando..." : "Entrar"}
            </button>
          </form>

          <p className="mt-4 text-center text-xs text-muted">
            <Link to="/cadastro" className="font-medium text-adopter hover:underline">
              Criar uma conta
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
