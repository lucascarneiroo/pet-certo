import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { cadastrarUsuario, login } from "../services/api";
import Logo from "../components/Logo";

const DESTINATIONS = {
  adotante: "/adotante",
  instituicao: "/instituicao",
  administrador: "/admin",
};

export default function Signup() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const perfil = params.get("perfil") || "adotante";

  const [form, setForm] = useState({
    nome: "",
    cpf: "",
    endereco: "",
    email: "",
    senha: "",
    cnpj: "",
    localizacao: "",
    info_abrigo: "",
  });
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      await cadastrarUsuario({ ...form, perfil });
      const usuario = await login(form.email, form.senha);
      navigate(DESTINATIONS[usuario.perfil] || "/adotante");
    } catch (err) {
      setErro(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-6 flex justify-center">
          <Logo size="md" />
        </div>
        <div className="rounded-3xl bg-white p-8 shadow-lift ring-1 ring-black/[0.03]">
        <h1 className="text-xl font-extrabold text-ink">Criar conta</h1>
        <p className="mt-1 text-sm text-muted">
          {perfil === "instituicao" ? "Cadastre sua instituição" : "Comece seu perfil de adotante"}
        </p>

        {erro && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{erro}</p>}

        <form onSubmit={handleSubmit} className="mt-6 grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">Nome</label>
            <input
              value={form.nome}
              onChange={update("nome")}
              required
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none transition focus:border-adopter focus:ring-2 focus:ring-adopter/15"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">E-mail</label>
            <input
              type="email"
              value={form.email}
              onChange={update("email")}
              required
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">Senha</label>
            <input
              type="password"
              value={form.senha}
              onChange={update("senha")}
              required
              minLength={6}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none focus:border-adopter"
            />
          </div>

          {perfil === "adotante" && (
            <>
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">CPF</label>
                <input
                  placeholder="000.000.000-00"
                  value={form.cpf}
                  onChange={update("cpf")}
                  required
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none transition focus:border-adopter focus:ring-2 focus:ring-adopter/15"
                />
              </div>
              <div className="col-span-2">
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">Endereço</label>
                <input
                  value={form.endereco}
                  onChange={update("endereco")}
                  required
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none transition focus:border-adopter focus:ring-2 focus:ring-adopter/15"
                />
              </div>
            </>
          )}

          {perfil === "instituicao" && (
            <>
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">CNPJ</label>
                <input
                  placeholder="00.000.000/0000-00"
                  value={form.cnpj}
                  onChange={update("cnpj")}
                  required
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none transition focus:border-adopter focus:ring-2 focus:ring-adopter/15"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">Localização</label>
                <input
                  value={form.localizacao}
                  onChange={update("localizacao")}
                  required
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none transition focus:border-adopter focus:ring-2 focus:ring-adopter/15"
                />
              </div>
              <div className="col-span-2">
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted">Sobre o abrigo</label>
                <input
                  value={form.info_abrigo}
                  onChange={update("info_abrigo")}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-ink outline-none transition focus:border-adopter focus:ring-2 focus:ring-adopter/15"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={enviando}
            className="col-span-2 mt-1 rounded-xl bg-adopter py-2.5 text-sm font-semibold text-white shadow-soft transition hover:-translate-y-0.5 hover:bg-adopter-dark hover:shadow-lift disabled:translate-y-0 disabled:opacity-60"
          >
            {enviando ? "Criando conta..." : "Criar conta"}
          </button>
        </form>
        </div>
      </div>
    </div>
  );
}
