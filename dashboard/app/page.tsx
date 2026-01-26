"use client";

import { useState, useEffect, useRef } from "react";

export default function Home() {
  const [status, setStatus] = useState<any>(null);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState<{ role: string, text: string }[]>([]);
  const [sending, setSending] = useState(false);

  const videoRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const res = await fetch("http://localhost:8080/status");
        const data = await res.json();
        setStatus(data);
      } catch (e) {
        console.error("Connection error");
      }
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleSend = async () => {
    if (!chatInput.trim()) return;
    const text = chatInput;
    setChatInput("");
    setChatHistory(prev => [...prev, { role: "user", text }]);
    setSending(true);

    try {
      const res = await fetch("http://localhost:8080/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      setChatHistory(prev => [...prev, { role: "bot", text: data.response }]);
    } catch (e) {
      console.error(e);
      setChatHistory(prev => [...prev, { role: "system", text: "Error communicating with Reachy." }]);
    }
    setSending(false);
  };

  const getEmotionColor = (emo: string) => {
    switch (emo) {
      case "happy": return "bg-yellow-400 shadow-yellow-500/50";
      case "sad": return "bg-blue-400 shadow-blue-500/50";
      case "angry": return "bg-red-500 shadow-red-500/50";
      case "surprise": return "bg-orange-400 shadow-orange-500/50";
      case "fear": return "bg-purple-400 shadow-purple-500/50";
      case "disgust": return "bg-green-400 shadow-green-500/50";
      case "neutral": return "bg-gray-400 shadow-gray-500/50";
      default: return "bg-white shadow-white/50";
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gradient-to-b from-gray-900 via-purple-950 to-black text-white relative">
      {/* Soft overlay */}
      <div className="absolute inset-0 bg-[url('/noise.png')] opacity-5 pointer-events-none mix-blend-overlay"></div>

      {/* Content Container */}
      <div className="z-10 w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 h-[90vh]">

        {/* Left: Visual Connection */}
        <div className="flex flex-col gap-6 h-full">
          <header>
            <h1 className="text-5xl font-thin tracking-widest text-white/90">REACHY</h1>
            <h2 className="text-xl text-purple-300 font-light tracking-widest">EMPATH INTERFACE</h2>
          </header>

          <div className="relative flex-grow rounded-3xl overflow-hidden glass shadow-2xl border border-white/10 group">
            {/* Live Feed */}
            <img
              src="http://localhost:8080/video_feed"
              className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-700"
              alt="Reachy Vision"
            />

            {/* Emotion Overlay */}
            <div className="absolute bottom-8 left-8 right-8 flex justify-between items-end">
              <div>
                <div className="text-xs uppercase tracking-widest text-white/50 mb-2">Current Resonance</div>
                <div className="flex items-center gap-4">
                  <div className={`w-4 h-4 rounded-full shadow-[0_0_20px] ${getEmotionColor(status?.emotion)} transition-colors duration-1000`}></div>
                  <span className="text-4xl font-light capitalize text-white drop-shadow-lg">{status?.emotion || "Scanning..."}</span>
                </div>
              </div>

              <div className="text-right">
                <div className="text-xs uppercase tracking-widest text-white/50 mb-1">Brain Status</div>
                <div className={`text-sm font-mono ${status?.brain_online ? "text-green-400" : "text-yellow-400"}`}>
                  {status?.brain_online ? "ONLINE // GEMMA-2B" : "LOADING..."}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Conversation */}
        <div className="glass rounded-3xl p-8 flex flex-col h-full border border-white/5 bg-black/20 backdrop-blur-xl">
          <div className="flex-grow overflow-y-auto space-y-4 pr-2 mb-4 scrollbar-hide">
            {chatHistory.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-white/20 text-center gap-4">
                <div className="w-16 h-16 rounded-full border border-white/20 flex items-center justify-center text-3xl">❤️</div>
                <p className="font-light">"How are you feeling right now?"</p>
              </div>
            )}
            {chatHistory.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${msg.role === "user"
                  ? "bg-white/10 text-white rounded-tr-none"
                  : "bg-purple-600/20 text-purple-100 border border-purple-500/20 rounded-tl-none shadow-[0_0_30px_rgba(147,51,234,0.1)]"
                  }`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-purple-600/10 p-4 rounded-2xl rounded-tl-none flex gap-2 items-center">
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></span>
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100"></span>
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-200"></span>
                </div>
              </div>
            )}
          </div>

          <div className="relative">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type to Reachy..."
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-4 pr-12 text-white placeholder:text-white/20 focus:outline-none focus:bg-white/10 focus:border-purple-500/50 transition-all shadow-inner"
            />
            <button
              onClick={handleSend}
              disabled={sending || !status?.brain_online}
              className="absolute right-2 top-2 bottom-2 aspect-square rounded-lg bg-white/10 hover:bg-white/20 text-white/50 hover:text-white transition-all flex items-center justify-center disabled:opacity-50"
            >
              ➤
            </button>
          </div>
        </div>

      </div>
    </main>
  );
}
