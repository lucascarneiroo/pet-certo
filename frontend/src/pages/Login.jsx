import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { login } from "../services/api";

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
      <div className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-card">
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
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
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
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
            />
          </div>
          <button
            type="submit"
            disabled={enviando}
            className="w-full rounded-lg bg-adopter py-2.5 text-sm font-semibold text-white transition hover:bg-adopter-dark disabled:opacity-60"
          >
            {enviando ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p className="mt-4 text-xs text-muted">
          <Link to="/cadastro" className="hover:text-ink">
            Criar uma conta
          </Link>
        </p>
      </div>
    </div>
  );
}
