import { Navigate } from "react-router-dom";
import { getUsuario } from "../services/api";

// mantém a mesma correspondência perfil -> área usada no login (Login.jsx)
const ROTA_DO_PERFIL = {
  adotante: "/adotante",
  instituicao: "/instituicao",
  administrador: "/admin",
};

// Protege as rotas /admin, /instituicao e /adotante: sem isso, qualquer
// pessoa podia digitar a URL direto e entrar em qualquer painel, sem estar
// logada ou logada com outro perfil.
export default function RequireRole({ perfil, children }) {
  const usuario = getUsuario();

  if (!usuario) {
    return <Navigate to="/entrar" replace />;
  }
  if (usuario.perfil !== perfil) {
    // logado, mas tentando acessar a área de outro perfil: manda pra área dele
    return <Navigate to={ROTA_DO_PERFIL[usuario.perfil] || "/entrar"} replace />;
  }
  return children;
}
