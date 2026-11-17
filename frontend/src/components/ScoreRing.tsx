import { CSSProperties } from "react";

export function ScoreRing({ score, label = "overall match", size = "large" }: { score: number; label?: string; size?: "large" | "small" }) {
  const value = Math.max(0, Math.min(100, score));
  return <div className={`score-ring score-ring-${size}`} style={{ "--score": `${value * 3.6}deg` } as CSSProperties} role="img" aria-label={`${Math.round(value)} percent ${label}`}>
    <div className="score-ring-inner"><strong>{Math.round(value)}<small>%</small></strong>{size === "large" && <span>{label}</span>}</div>
  </div>;
}
