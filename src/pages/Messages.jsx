import { useState, useRef, useEffect } from "react";
import { callAI } from "@/lib/ai";
import { Send, Loader2, User, Sparkles, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Messages() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm HireBot, your AI career assistant. Ask me anything about CVs, interviews, salary, or job search strategy!" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: "user", content: input.trim() };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    setLoading(true);
    try {
      const reply = await callAI(userMsg.content, messages);
      setMessages([...history, { role: "assistant", content: reply }]);
    } catch {
      setMessages([...history, { role: "assistant", content: "Sorry, something went wrong. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setMessages([{ role: "assistant", content: "Chat reset! How can I help you today?" }]);
  };

  return (
    <div className="p-8 lg:p-12 h-screen flex flex-col max-w-4xl">
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-primary mb-1">AI Assistant</p>
          <h1 className="text-3xl font-bold">Career Advisor</h1>
          <p className="text-muted-foreground mt-1 text-sm">Ask anything about your job search.</p>
        </div>
        <Button variant="outline" size="sm" onClick={reset} className="mt-1">
          <RotateCcw className="w-4 h-4 mr-1.5" /> New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                <Sparkles className="w-4 h-4 text-primary" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-line ${
              msg.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-card border border-border"
            }`}>
              {msg.content}
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-4 h-4 text-muted-foreground" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4 text-primary" />
            </div>
            <div className="bg-card border border-border rounded-2xl px-4 py-3">
              <Loader2 className="w-4 h-4 text-primary animate-spin" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="flex gap-2 pt-4 border-t border-border">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
          placeholder="Ask about CV, interviews, salary..."
          disabled={loading}
        />
        <Button onClick={send} disabled={!input.trim() || loading}>
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
