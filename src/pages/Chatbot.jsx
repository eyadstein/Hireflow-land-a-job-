import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2, User, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI career assistant. Ask me about CVs, interviews, job search, or salary tips.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const getDemoReply = (text) => {
    const msg = text.toLowerCase();

    if (msg.includes("cv") || msg.includes("resume")) {
      return `Here’s a strong CV tip:

Use numbers in your achievements.

Bad:
"Worked on a project"

Good:
"Built a React dashboard that improved task tracking by 30%"

This makes your CV look more professional.`;
    }

    if (msg.includes("interview")) {
      return `For interviews, use the STAR method:

S — Situation  
T — Task  
A — Action  
R — Result  

Example: explain the problem, what you had to do, what you did, and the final result.`;
    }

    if (msg.includes("salary")) {
      return `Salary negotiation tip:

Do not say a number too early. First ask about the salary range, then explain your value using your skills, projects, and experience.`;
    }

    return `Good question.

For your career, focus on:
1. A clean CV
2. Strong LinkedIn profile
3. Real projects on GitHub
4. Practicing interview answers
5. Applying consistently`;
  };

  const sendMessage = () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: "user", content: input.trim() };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    setTimeout(() => {
      const reply = getDemoReply(userMsg.content);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: reply,
        },
      ]);

      setLoading(false);
    }, 600);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen p-8 lg:p-12 bg-background text-foreground">
      <div className="max-w-4xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
        <div className="mb-8">
          <p className="text-sm text-primary font-medium mb-2">AI Assistant</p>
          <h1 className="text-3xl font-bold">Career Advisor</h1>
          <p className="text-muted-foreground mt-2">
            Ask anything about your job search.
          </p>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex gap-3 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
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