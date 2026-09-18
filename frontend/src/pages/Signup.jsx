import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { cadastrarUsuario, login } from "../services/api";

const DESTINATIONS = {
  adotante: "/adotante",
  voluntario: "/instituicao",
  admin: "/admin",
};

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    nome: "",
    email: "",
    senha: "",
    perfil: "adotante", // "adotante" ou "instituicao" — admin não pode se autocadastrar
    instituicao_nome: "",
    instituicao_cidade: "",
  });
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setCarregando(true);
    try {
      await cadastrarUsuario(form);
      const usuario = await login(form.email, form.senha);
      navigate(DESTINATIONS[usuario.perfil] || "/adotante");
    } catch (err) {
      setErro(err.message || "Não foi possível criar a conta.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-card">
        <h1 className="text-xl font-extrabold text-ink">Criar conta</h1>
        <p className="mt-1 text-sm text-muted">Comece seu perfil no Pet Certo</p>

        <form onSubmit={handleSubmit} className="mt-6 grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
              Nome
            </label>
            <input
              value={form.nome}
              onChange={update("nome")}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
            />
          </div>
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
              E-mail
            </label>
            <input
              type="email"
              value={form.email}
              onChange={update("email")}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
            />
          </div>
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
              Senha (mín. 6 caracteres)
            </label>
            <input
              type="password"
              value={form.senha}
              onChange={update("senha")}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
            />
          </div>
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
              Eu sou
            </label>
            <select
              value={form.perfil}
              onChange={update("perfil")}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
            >
              <option value="adotante">Adotante</option>
              <option value="instituicao">Instituição / ONG</option>
            </select>
          </div>

          {form.perfil === "instituicao" && (
            <>
              <div className="col-span-2">
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
                  Nome da instituição
                </label>
                <input
                  value={form.instituicao_nome}
                  onChange={update("instituicao_nome")}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
                />
              </div>
              <div className="col-span-2">
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">
                  Cidade
                </label>
                <input
                  value={form.instituicao_cidade}
                  onChange={update("instituicao_cidade")}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
                />
              </div>
            </>
          )}

          {erro && <p className="col-span-2 text-xs font-semibold text-red-600">{erro}</p>}

          <button
            type="submit"
            disabled={carregando}
            className="col-span-2 mt-1 rounded-lg bg-adopter py-2.5 text-sm font-semibold text-white transition hover:bg-adopter-dark disabled:opacity-60"
          >
            {carregando ? "Criando..." : "Criar conta"}
          </button>
        </form>
      </div>
    </div>
  );
}
