import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { login } from "../services/api";

const DESTINATIONS = {
  adotante: "/adotante",
  voluntario: "/instituicao",
  admin: "/admin",
};

export default function Login() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setCarregando(true);
    try {
      const usuario = await login(email, senha);
      navigate(DESTINATIONS[usuario.perfil] || "/adotante");
    } catch (err) {
      setErro(err.message || "Não foi possível entrar. Confira e-mail e senha.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-8 shadow-card">
        <h1 className="text-xl font-extrabold text-ink">Entrar</h1>
        <p className="mt-1 text-sm text-muted">Acesse sua conta Pet Certo</p>

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

          {erro && <p className="text-xs font-semibold text-red-600">{erro}</p>}

          <button
            type="submit"
            disabled={carregando}
            className="w-full rounded-lg bg-adopter py-2.5 text-sm font-semibold text-white transition hover:bg-adopter-dark disabled:opacity-60"
          >
            {carregando ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p className="mt-4 text-xs text-muted">
          <button className="hover:text-ink">Esqueci minha senha</button>
          {" · "}
          <Link to="/cadastro" className="hover:text-ink">
            Criar uma conta
          </Link>
        </p>

        <div className="mt-6 border-t border-slate-100 pt-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
            Acesso de teste (criado automaticamente pelo backend)
          </p>
          <p className="text-xs text-muted">admin@petcerto.com · admin123</p>
        </div>
      </div>
    </div>
  );
}
