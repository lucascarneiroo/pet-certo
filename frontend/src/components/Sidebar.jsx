import { NavLink } from "react-router-dom";

export default function Sidebar({ base, roleLabel, items, theme }) {
  return (
    <aside
      className="flex w-56 shrink-0 flex-col gap-6 rounded-2xl p-5 text-white"
      style={{ backgroundColor: theme.DEFAULT }}
    >
      <div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-white/80" />
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
              `rounded-lg px-3 py-2 text-sm font-medium transition ${
                isActive ? "bg-white/15 text-white" : "text-white/70 hover:bg-white/10 hover:text-white"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <NavLink to="/" className="text-xs text-white/50 hover:text-white/80">
        ← Sair do painel
      </NavLink>
    </aside>
  );
}
