import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeFile } from "../api";

export default function UploadPage() {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  async function handleFile(file: File) {
    setUploading(true);
    setError(null);
    try {
      const { session_id } = await analyzeFile(file);
      navigate(`/results/${session_id}`);
    } catch (e: any) {
      setError(e.message || "Something went wrong");
    } finally {
      setUploading(false);
    }
  }

  if (uploading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin mb-6" />
        <p className="text-lg font-medium">Gemini is watching your pitch...</p>
        <p className="text-white/50 text-sm mt-2">This usually takes 30–60 seconds.</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Get an AI critique on your pitch</h1>
      <p className="text-white/60 mb-8">
        Upload a demo video (≤3 min) or a slide deck + audio. Powered by Gemini's multimodal API.
      </p>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          const file = e.dataTransfer.files[0];
          if (file) handleFile(file);
        }}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-colors ${
          dragOver ? "border-accent bg-accent/5" : "border-white/20 hover:border-white/40"
        }`}
      >
        <p className="text-white/70 mb-2">Drag & drop your video here, or click to browse</p>
        <p className="text-white/40 text-sm">MP4, MOV, or WebM · up to 200MB</p>
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />
      </div>

      {error && <p className="text-red-400 mt-4 text-sm">{error}</p>}
    </div>
  );
}
