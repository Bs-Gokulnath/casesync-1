export function AuroraBackground({ intensity = "subtle" }: { intensity?: "subtle" | "bold" }) {
  const opacity = intensity === "bold" ? "opacity-60" : "opacity-25";
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden>
      <div className="bg-background absolute inset-0" />
      <div className="grid-pattern absolute inset-0 opacity-40" />
      <div
        className={`animate-aurora absolute -top-40 -left-40 size-[36rem] rounded-full bg-[#7c6cff] blur-[120px] ${opacity}`}
      />
      <div
        className={`animate-aurora absolute top-1/3 -right-32 size-[30rem] rounded-full bg-[#22d3ee] blur-[120px] ${opacity}`}
        style={{ animationDelay: "-6s" }}
      />
      <div
        className={`animate-aurora absolute -bottom-40 left-1/4 size-[28rem] rounded-full bg-[#f472b6] blur-[130px] ${opacity}`}
        style={{ animationDelay: "-12s" }}
      />
      <div className="noise-overlay absolute inset-0" />
    </div>
  );
}
