import { NavLink, useNavigate } from "react-router-dom";
import { logout } from "../services/api";
import { LogoMark } from "./Logo";

export default function Sidebar({ base, roleLabel, items, theme }) {
  const navigate = useNavigate();

  function handleSair() {
    logout();
    navigate("/", { replace: true });
  }

  return (
    <aside
      className="flex w-56 shrink-0 flex-col gap-6 rounded-3xl p-5 text-white shadow-lift"
      style={{ background: `linear-gradient(165deg, ${theme.DEFAULT}, ${theme.dark || theme.DEFAULT})` }}
    >
      <div>
        <div className="flex items-center gap-2">
          <LogoMark className="h-6 w-6 text-white" />
          <span className="text-sm font-extrabold tracking-tight">PET CERTO</span>
        </div>
        <p className="mt-1 text-xs text-white/60">{roleLabel}</p>
      </div>

      <nav className="flex flex-1 flex-col gap-1">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={`${base}${item.to}`}
            end={item.end}
            className={({ isActive }) =>
              `rounded-xl px-3 py-2 text-sm font-medium transition ${
                isActive ? "bg-white/15 text-white shadow-inner" : "text-white/70 hover:bg-white/10 hover:text-white"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <button onClick={handleSair} className="text-left text-xs text-white/50 transition hover:text-white/80">
        ← Sair do painel
      </button>
    </aside>
  );
}
