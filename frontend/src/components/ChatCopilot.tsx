import React, { useState, useRef, useEffect } from "react";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface ChatCopilotProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function ChatCopilot({ isOpen, onClose }: ChatCopilotProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: "Hello! I am your OpenAI powered Specialized Occupancy Analyst. Ask me anything about property occupancy trends, vacancy concentrations, or upcoming lease expiration risks.",
        },
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage: Message = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try{
            const response = await fetch("http://localhost:8000/api/copilot/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ messages: [...messages, userMessage ]}),
            });
            const data = await response.json();
            if (data.success) {
                setMessages((prev) => [...prev, data.message]);
            } else {
                setMessages((prev) => [
                    ...prev,
                    { role: "assistant", content: "Apologies, I encountered a connection error. Please verify the backend is running and OPENAI_API_KEY is configured in your .env."},
                ]);
            }
        } catch {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: "Failed to establish a handshake connection with the orchestrator engine."},
            ]);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
    <div className="fixed inset-y-0 right-0 w-96 bg-slate-950 border-l border-slate-800 shadow-2xl flex flex-col z-50 animate-slide-in">
      {/* Header */}
      <div className="bg-slate-900 px-4 py-3.5 border-b border-slate-800 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></span>
          <h2 className="text-sm font-bold tracking-wide text-white uppercase font-mono">OpenAI Copilot</h2>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white transition text-xs font-semibold px-2 py-1">
          Close ✕
        </button>
      </div>
      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans text-xs">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-xl p-3.5 leading-relaxed ${
              m.role === "user" 
                ? "bg-indigo-600 text-white rounded-br-none" 
                : "bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none"
            }`}>
              <p className="whitespace-pre-line">{m.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-900 border border-slate-800 rounded-xl rounded-bl-none p-3.5 max-w-[85%] flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
              <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
              <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
              <span className="text-[10px] text-slate-500 font-mono pl-1">Executing Tool Calls...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      {/* Input Tray */}
      <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-800 bg-slate-900/50 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask occupancy, expirations, target rate..."
          className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 placeholder-slate-600"
        />
        <button type="submit" disabled={loading} className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-medium text-xs px-3 py-2 rounded-lg transition">
          Send
        </button>
      </form>
    </div>
  );
}