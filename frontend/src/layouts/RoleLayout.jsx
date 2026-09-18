import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";

export default function RoleLayout({ base, roleLabel, roleTitle, roleDescription, items, theme }) {
  return (
    <div className="min-h-screen bg-canvas">
      <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-6">
          <h1 className="text-2xl font-extrabold text-ink">{roleTitle}</h1>
          <p className="mt-1 text-sm text-muted">{roleDescription}</p>
        </header>

        <div className="flex flex-col gap-6 md:flex-row">
          <Sidebar base={base} roleLabel={roleLabel} items={items} theme={theme} />
          <main className="min-w-0 flex-1 space-y-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
