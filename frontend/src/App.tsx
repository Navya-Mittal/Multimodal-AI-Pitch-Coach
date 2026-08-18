import { Outlet, Link } from "react-router-dom";

export default function App() {
  return (
    <div className="min-h-screen bg-bg">
      <header className="border-b border-white/10 px-6 py-4">
        <Link to="/" className="text-lg font-semibold tracking-tight">
          Pitch <span className="text-accent">Perfect</span>
        </Link>
      </header>
      <main className="max-w-4xl mx-auto px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}
