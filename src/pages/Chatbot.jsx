import React, { useState, useRef, useEffect } from "react";
import { callAI } from "@/lib/ai";
import { Send, Loader2, User, Sparkles, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! I'm HireBot, your AI career assistant. Ask me about CVs, interviews, job search, salary negotiation, or anything career-related!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const reply = await callAI(userMsg.content, history);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const resetChat = () => {
    setMessages([{
      role: "assistant",
      content: "Chat reset! How can I help you with your career today?",
    }]);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen p-8 lg:p-12 bg-background text-foreground">
      <div className="max-w-4xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
        <div className="flex items-start justify-between mb-8">
          <div>
            <p className="text-sm text-primary font-medium mb-2">AI Assistant</p>
            <h1 className="text-3xl font-bold">Career Advisor</h1>
            <p className="text-muted-foreground mt-2">Ask anything about your job search.</p>
          </div>
          <Button variant="outline" size="sm" onClick={resetChat} className="mt-2">
            <RotateCcw className="w-4 h-4 mr-2" /> New Chat
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <Sparkles className="w-4 h-4 text-primary" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 whitespace-pre-line text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-card border border-border"
                }`}
              >
                {msg.content}
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0">
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
            onKeyDown={handleKeyDown}
            placeholder="Ask about CV, interviews, salary..."
            disabled={loading}
          />
          <Button onClick={sendMessage} disabled={!input.trim() || loading}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
