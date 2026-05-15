import React, { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MessageSquare, Send, Loader2, User, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { chat } from "@/api/client";

const getCurrentUserId = () => {
  try {
    const rawUser = localStorage.getItem("user");

    if (rawUser) {
      const user = JSON.parse(rawUser);
      if (user?.id) return user.id;
    }

    const token = localStorage.getItem("access_token");

    if (!token) return null;

    return JSON.parse(atob(token.split(".")[1])).user_id;
  } catch {
    return null;
  }
};

export default function Messages() {
  const qc = useQueryClient();

  const [selectedUser, setSelectedUser] = useState(null);
  const [text, setText] = useState("");
  const [search, setSearch] = useState("");

  const endRef = useRef(null);
  const currentUserId = getCurrentUserId();

  const {
    data: allUsers = [],
    isLoading: loadingUsers,
    error: usersError,
  } = useQuery({
    queryKey: ["all-users"],
    queryFn: chat.listUsers,
  });

  const {
    data: messages = [],
    isLoading: loadingMsgs,
    error: messagesError,
  } = useQuery({
    queryKey: ["chat", selectedUser?.id],
    queryFn: () => chat.listMessages(selectedUser.id),
    enabled: !!selectedUser?.id,
    refetchInterval: 3000,
  });

  const sendMutation = useMutation({
    mutationFn: (msg) => chat.sendMessage(selectedUser.id, msg),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["chat", selectedUser?.id] });
      setText("");
    },
  });

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const otherUsers = allUsers.filter((u) => {
    const isNotMe = u.id !== currentUserId;
    const label = `${u.username || ""} ${u.email || ""}`.toLowerCase();
    const matchesSearch = search === "" || label.includes(search.toLowerCase());

    return isNotMe && matchesSearch;
  });

  const handleSend = () => {
    if (!selectedUser?.id || !text.trim()) return;

    sendMutation.mutate(text.trim());
  };

  return (
    <div className="flex h-screen overflow-hidden">
      <div className="w-64 border-r border-border flex flex-col shrink-0">
        <div className="p-4 border-b border-border">
          <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-2">
            Messaging
          </p>

          <h2 className="text-lg font-bold flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Conversations
          </h2>
        </div>

        <div className="p-3 border-b border-border">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />

            <Input
              placeholder="Search users…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 h-8 text-sm"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loadingUsers ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
            </div>
          ) : usersError ? (
            <p className="text-xs text-red-600 text-center py-8 px-4">
              {usersError.message || "Failed to load users."}
            </p>
          ) : otherUsers.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-8 px-4">
              No users found.
            </p>
          ) : (
            otherUsers.map((u) => (
              <button
                key={u.id}
                type="button"
                onClick={() => setSelectedUser(u)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-secondary transition ${
                  selectedUser?.id === u.id ? "bg-secondary" : ""
                }`}
              >
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4 text-primary" />
                </div>

                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">
                    {u.username || u.email}
                  </p>

                  <p className="text-xs text-muted-foreground capitalize">
                    {u.role || "user"}
                  </p>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        {!selectedUser ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageSquare className="w-12 h-12 text-muted-foreground mx-auto mb-3" />

              <p className="font-semibold text-lg">Select a conversation</p>

              <p className="text-sm text-muted-foreground mt-1">
                Choose a user from the list to start messaging.
              </p>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-3 px-6 py-4 border-b border-border">
              <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center">
                <User className="w-4 h-4 text-primary" />
              </div>

              <div>
                <p className="font-semibold">
                  {selectedUser.username || selectedUser.email}
                </p>

                <p className="text-xs text-muted-foreground capitalize">
                  {selectedUser.role || "user"}
                </p>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-3">
              {loadingMsgs ? (
                <div className="flex justify-center py-10">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : messagesError ? (
                <div className="text-center py-10">
                  <p className="text-sm text-red-600">
                    {messagesError.message || "Failed to load messages."}
                  </p>
                </div>
              ) : messages.length === 0 ? (
                <div className="text-center py-10">
                  <p className="text-sm text-muted-foreground">
                    No messages yet — say hello!
                  </p>
                </div>
              ) : (
                messages.map((msg) => {
                  const mine =
                    msg.sender === currentUserId ||
                    msg.sender?.id === currentUserId;

                  return (
                    <div
                      key={msg.id}
                      className={`flex ${mine ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[70%] px-4 py-2 rounded-2xl text-sm ${
                          mine
                            ? "bg-primary text-primary-foreground rounded-br-sm"
                            : "bg-card border border-border rounded-bl-sm"
                        }`}
                      >
                        <p>{msg.encrypted_text || msg.content || msg.message}</p>

                        {msg.timestamp && (
                          <p
                            className={`text-[10px] mt-1 ${
                              mine
                                ? "text-primary-foreground/70"
                                : "text-muted-foreground"
                            }`}
                          >
                            {new Date(msg.timestamp).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })
              )}

              <div ref={endRef} />
            </div>

            {sendMutation.error && (
              <div className="px-4 py-2 text-sm text-red-600 border-t border-border">
                {sendMutation.error.message || "Failed to send message."}
              </div>
            )}

            <div className="p-4 border-t border-border flex gap-3">
              <Input
                placeholder={`Message ${selectedUser.username || selectedUser.email}…`}
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                className="flex-1"
              />

              <Button
                type="button"
                onClick={handleSend}
                disabled={!text.trim() || sendMutation.isPending}
                size="icon"
              >
                {sendMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}