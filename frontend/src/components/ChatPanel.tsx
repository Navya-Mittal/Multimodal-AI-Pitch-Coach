import { useState } from "react";
import { askPitch } from "../api";

export default function ChatPanel({ sessionId }: { sessionId: string }) {
  const [messages, setMessages] = useState<{ role: "user" | "ai"; text: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const suggestions = [
    "What would a Google engineer ask me here?",
    "Where did I lose clarity?",
    "Rewrite my opening line",
  ];

  async function send(question: string) {
    if (!question.trim()) return;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const { answer } = await askPitch(sessionId, question);
      setMessages((m) => [...m, { role: "ai", text: answer }]);
    } catch {
      setMessages((m) => [...m, { role: "ai", text: "Sorry, something went wrong answering that." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-surface border border-white/10 rounded-xl p-5 flex flex-col h-full">
      <h3 className="font-semibold mb-3">Ask my pitch</h3>

      {messages.length === 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="text-xs px-3 py-1.5 rounded-full border border-white/15 text-white/60 hover:border-accent hover:text-accent transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-3 mb-3 min-h-[120px]">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : ""}>
            <span
              className={`inline-block rounded-lg px-3 py-2 text-sm max-w-[85%] ${
                m.role === "user" ? "bg-accent text-white" : "bg-white/5 text-white/80"
              }`}
            >
              {m.text}
            </span>
          </div>
        ))}
        {loading && <p className="text-white/40 text-sm">Thinking...</p>}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send(input)}
          placeholder="Ask about your pitch..."
          className="flex-1 bg-bg border border-white/15 rounded-lg px-3 py-2 text-sm outline-none focus:border-accent"
        />
        <button
          onClick={() => send(input)}
          className="bg-accent px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90"
        >
          Send
        </button>
      </div>
    </div>
  );
}
