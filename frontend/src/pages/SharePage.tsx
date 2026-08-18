import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getSharedSession, Scorecard } from "../api";
import ScoreCard from "../components/ScoreCard";

export default function SharePage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    getSharedSession(sessionId)
      .then((data) => setScorecard(data.scorecard))
      .catch((e) => setError(e.message));
  }, [sessionId]);

  if (error) return <p className="text-red-400">{error}</p>;
  if (!scorecard) return <p className="text-white/50">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Pitch Scorecard</h1>
      <p className="text-white/40 text-sm mb-6">Shared via Pitch Perfect</p>
      <p className="text-white/70 mb-8 bg-surface border border-white/10 rounded-xl p-4">
        {scorecard.overall_summary}
      </p>
      <div className="grid md:grid-cols-2 gap-4">
        {scorecard.axes.map((axis) => (
          <ScoreCard key={axis.name} axis={axis} />
        ))}
      </div>
    </div>
  );
}
