export function Panel({ title, subtitle, children, className = "" }) {
  return (
    <section className={`rounded-2xl bg-white p-6 shadow-card ${className}`}>
      {(title || subtitle) && (
        <header className="mb-5">
          {title && <h2 className="text-lg font-bold text-ink">{title}</h2>}
          {subtitle && <p className="mt-0.5 text-sm text-muted">{subtitle}</p>}
        </header>
      )}
      {children}
    </section>
  );
}

export function Row({ title, subtitle, right, onClick, className = "" }) {
  const Comp = onClick ? "button" : "div";
  return (
    <Comp
      onClick={onClick}
      className={`flex w-full items-center justify-between gap-4 rounded-xl border border-slate-100 bg-white px-4 py-3.5 text-left transition hover:border-slate-200 hover:shadow-sm ${className}`}
    >
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold text-ink">{title}</p>
        {subtitle && <p className="mt-0.5 truncate text-xs text-muted">{subtitle}</p>}
      </div>
      {right}
    </Comp>
  );
}

export function Stat({ label, value, hint, hintTone = "muted" }) {
  const toneClass =
    hintTone === "up" ? "text-[#2F7A50]" : hintTone === "warn" ? "text-[#9A6B1E]" : "text-muted";
  return (
    <div className="rounded-xl border border-slate-100 bg-white p-4">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-1 text-2xl font-extrabold text-ink">{value}</p>
      {hint && <p className={`mt-1 text-xs font-medium ${toneClass}`}>{hint}</p>}
    </div>
  );
}

export function ProgressBar({ label, value }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="text-ink">{label}</span>
        <span className="font-semibold text-[#2F7A50]">{value}%</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-[#3E9C63]"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
