export function LogoMark({ className = "h-7 w-7" }) {
  return (
    <svg viewBox="0 0 48 48" fill="currentColor" className={className} aria-hidden="true">
      <ellipse cx="24" cy="31" rx="12.5" ry="10.5" />
      <circle cx="9.5" cy="16.5" r="5.8" />
      <circle cx="19.5" cy="8.5" r="6.2" />
      <circle cx="29.5" cy="8.5" r="6.2" />
      <circle cx="39.5" cy="16.5" r="5.8" />
    </svg>
  );
}

export default function Logo({ size = "md", tone = "brand", className = "" }) {
  const sizes = {
    sm: { icon: "h-6 w-6", text: "text-sm" },
    md: { icon: "h-8 w-8", text: "text-lg" },
    lg: { icon: "h-11 w-11", text: "text-2xl" },
  }[size];

  const toneClass = tone === "white" ? "text-white" : "text-adopter";

  return (
    <div className={`flex items-center gap-2.5 ${toneClass} ${className}`}>
      <LogoMark className={sizes.icon} />
      <span className={`font-extrabold tracking-tight ${sizes.text}`}>
        Pet<span className="font-light">Certo</span>
      </span>
    </div>
  );
}
