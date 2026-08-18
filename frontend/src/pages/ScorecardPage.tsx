import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getSession, Scorecard } from "../api";
import ScoreCard from "../components/ScoreCard";
import ChatPanel from "../components/ChatPanel";

export default function ScorecardPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    getSession(sessionId)
      .then((data) => setScorecard(data.scorecard))
      .catch((e) => setError(e.message));
  }, [sessionId]);

  function copyShareLink() {
    const url = `${window.location.origin}/share/${sessionId}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (error) return <p className="text-red-400">{error}</p>;
  if (!scorecard) return <p className="text-white/50">Loading scorecard...</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Your Scorecard</h1>
        <button
          onClick={copyShareLink}
          className="text-sm border border-white/15 rounded-lg px-4 py-2 hover:border-accent hover:text-accent transition-colors"
        >
          {copied ? "Link copied!" : "Copy shareable link"}
        </button>
      </div>

      <p className="text-white/70 mb-8 bg-surface border border-white/10 rounded-xl p-4">
        {scorecard.overall_summary}
      </p>

      <div className="grid md:grid-cols-2 gap-4 mb-8">
        {scorecard.axes.map((axis) => (
          <ScoreCard key={axis.name} axis={axis} />
        ))}
      </div>

      <div className="h-96">{sessionId && <ChatPanel sessionId={sessionId} />}</div>
    </div>
  );
}
