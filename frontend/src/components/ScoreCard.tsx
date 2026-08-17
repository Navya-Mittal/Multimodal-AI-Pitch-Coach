import type { Axis } from "../api";

function scoreColor(score: number) {
  if (score >= 8) return "text-green-400";
  if (score >= 5) return "text-yellow-400";
  return "text-red-400";
}

export default function ScoreCard({ axis }: { axis: Axis }) {
  return (
    <div className="bg-surface border border-white/10 rounded-xl p-5">
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="font-semibold text-lg">{axis.name}</h3>
        <span className={`text-2xl font-bold ${scoreColor(axis.score)}`}>{axis.score}/10</span>
      </div>
      <ul className="space-y-2 mb-3">
        {axis.critiques.map((c, i) => (
          <li key={i} className="text-sm text-white/70 flex gap-2">
            <span className="text-accent font-mono text-xs mt-0.5 shrink-0">
              {Math.floor(c.timestamp_seconds / 60)}:{String(c.timestamp_seconds % 60).padStart(2, "0")}
            </span>
            <span>{c.note}</span>
          </li>
        ))}
      </ul>
      <div className="text-sm bg-accent/10 border border-accent/20 rounded-lg p-3">
        <span className="text-accent font-medium">Try this: </span>
        <span className="text-white/80">{axis.rewrite_suggestion}</span>
      </div>
    </div>
  );
}
