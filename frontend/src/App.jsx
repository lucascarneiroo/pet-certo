import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import RoleLayout from "./layouts/RoleLayout";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import SystemStates from "./pages/SystemStates";

import AdminDashboard from "./pages/admin/Dashboard";
import AdminAnimals from "./pages/admin/Animals";
import AdminInstitutions from "./pages/admin/Institutions";
import AdminUsers from "./pages/admin/Users";

import OngDashboard from "./pages/ong/Dashboard";
import OngAnimals from "./pages/ong/Animals";
import OngRequests from "./pages/ong/Requests";
import OngVisits from "./pages/ong/Visits";
import OngDocuments from "./pages/ong/Documents";
import OngIndicators from "./pages/ong/Indicators";

import AdopterDashboard from "./pages/adopter/Dashboard";
import AdopterAnimals from "./pages/adopter/Animals";
import AnimalDetail from "./pages/adopter/AnimalDetail";
import AdopterRequests from "./pages/adopter/Requests";
import AdopterVisits from "./pages/adopter/Visits";
import AdopterDocuments from "./pages/adopter/Documents";
import AdopterHistory from "./pages/adopter/History";

const ADMIN_ITEMS = [
  { to: "", label: "Visão geral", end: true },
  { to: "/animais", label: "Animais" },
  { to: "/instituicoes", label: "Instituições" },
  { to: "/usuarios", label: "Usuários" },
];

const ONG_ITEMS = [
  { to: "", label: "Visão geral", end: true },
  { to: "/animais", label: "Animais" },
  { to: "/solicitacoes", label: "Solicitações" },
  { to: "/visitas", label: "Visitas" },
  { to: "/documentos", label: "Documentos" },
  { to: "/indicadores", label: "Indicadores" },
];

const ADOPTER_ITEMS = [
  { to: "", label: "Visão geral", end: true },
  { to: "/animais", label: "Animais" },
  { to: "/solicitacoes", label: "Solicitações" },
  { to: "/visitas", label: "Visitas" },
  { to: "/documentos", label: "Documentos" },
  { to: "/historico", label: "Histórico" },
];

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/entrar" element={<Login />} />
        <Route path="/cadastro" element={<Signup />} />
        <Route path="/estados" element={<SystemStates />} />

        <Route
          path="/admin"
          element={
            <RoleLayout
              base="/admin"
              roleLabel="Administrador"
              roleTitle="Perfil Administrador"
              roleDescription="Governança de usuários, instituições, animais, processos, permissões e registros."
              items={ADMIN_ITEMS}
              theme={{ DEFAULT: "#3E6B52" }}
            />
          }
        >
          <Route index element={<AdminDashboard />} />
          <Route path="animais" element={<AdminAnimals />} />
          <Route path="instituicoes" element={<AdminInstitutions />} />
          <Route path="usuarios" element={<AdminUsers />} />
        </Route>

        <Route
          path="/instituicao"
          element={
            <RoleLayout
              base="/instituicao"
              roleLabel="Instituição / ONG"
              roleTitle="Perfil Instituição / ONG"
              roleDescription="Operação diária do Instituto Amor Animal, com análise, agenda e indicadores."
              items={ONG_ITEMS}
              theme={{ DEFAULT: "#33566F" }}
            />
          }
        >
          <Route index element={<OngDashboard />} />
          <Route path="animais" element={<OngAnimals />} />
          <Route path="solicitacoes" element={<OngRequests />} />
          <Route path="visitas" element={<OngVisits />} />
          <Route path="documentos" element={<OngDocuments />} />
          <Route path="indicadores" element={<OngIndicators />} />
        </Route>

        <Route
          path="/adotante"
          element={
            <RoleLayout
              base="/adotante"
              roleLabel="Adotante"
              roleTitle="Perfil Adotante"
              roleDescription="Descoberta, compatibilidade e acompanhamento completo da adoção."
              items={ADOPTER_ITEMS}
              theme={{ DEFAULT: "#6A4C8C" }}
            />
          }
        >
          <Route index element={<AdopterDashboard />} />
          <Route path="animais" element={<AdopterAnimals />} />
          <Route path="animais/:id" element={<AnimalDetail />} />
          <Route path="solicitacoes" element={<AdopterRequests />} />
          <Route path="visitas" element={<AdopterVisits />} />
          <Route path="documentos" element={<AdopterDocuments />} />
          <Route path="historico" element={<AdopterHistory />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
