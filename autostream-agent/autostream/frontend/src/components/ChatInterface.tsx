"use client";

import { useEffect, useRef, useState, KeyboardEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, RotateCcw, Zap, ChevronDown } from "lucide-react";
import TextareaAutosize from "react-textarea-autosize";
import { cn } from "@/lib/utils";

import { useChat } from "@/hooks/useChat";
import { ChatMessage } from "./ChatMessage";
import { TypingIndicator } from "./TypingIndicator";
import { IntentBadge } from "./IntentBadge";
import { LeadPanel } from "./LeadPanel";

const SUGGESTIONS = [
  "What's included in the Pro plan?",
  "How much does Basic cost?",
  "Do you offer a free trial?",
  "I want to sign up for Pro",
];

export function ChatInterface() {
  const { state, sendUserMessage, reset } = useChat();
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [state.messages]);

  const handleScroll = () => {
    const el = scrollContainerRef.current;
    if (!el) return;
    setShowScrollBtn(el.scrollHeight - el.scrollTop - el.clientHeight > 80);
  };

  const scrollToBottom = () =>
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });

  const handleSend = async () => {
    if (!input.trim() || state.isLoading) return;
    const text = input.trim();
    setInput("");
    await sendUserMessage(text);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isHighIntent = state.intent === "high_intent";
  const showSuggestions = state.messages.length === 1 && !state.isLoading;

  return (
    <div className="flex gap-5 w-full max-w-5xl mx-auto h-full">
      {/* ── Chat column ─────────────────────────────────────────────────── */}
      <div className="flex flex-col flex-1 min-w-0 h-full">

        {/* Header */}
        <header className={cn(
          "flex items-center justify-between px-5 py-4 border-b transition-colors duration-500",
          isHighIntent ? "border-amber-200 bg-amber-50/40" : "border-slate-200 bg-transparent"
        )}>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-md shadow-violet-200">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-slate-900 leading-none">AutoStream AI</h1>
              <p className="text-[11px] text-slate-400 mt-0.5">Sales Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <IntentBadge intent={state.intent} />
            <button
              onClick={reset}
              className="w-7 h-7 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-200 flex items-center justify-center transition-colors text-slate-500 hover:text-slate-700"
              title="New conversation"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* Messages */}
        <div
          ref={scrollContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto px-5 py-5 scroll-smooth"
        >
          <AnimatePresence initial={false}>
            {state.messages.map((msg, idx) =>
              msg.isTyping ? (
                <TypingIndicator key="typing" />
              ) : (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  isLatest={idx === state.messages.length - 1}
                />
              )
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Scroll button */}
        <AnimatePresence>
          {showScrollBtn && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={scrollToBottom}
              className="absolute bottom-24 right-8 w-8 h-8 rounded-full bg-white border border-slate-200 shadow-md flex items-center justify-center z-10"
            >
              <ChevronDown className="w-4 h-4 text-slate-500" />
            </motion.button>
          )}
        </AnimatePresence>

        {/* Suggestion chips */}
        <AnimatePresence>
          {showSuggestions && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="px-5 pb-3 flex flex-wrap gap-2"
            >
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendUserMessage(s)}
                  className="text-xs px-3 py-1.5 rounded-full border border-slate-200 bg-white text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 hover:border-indigo-200 transition-all duration-200 shadow-sm"
                >
                  {s}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input bar */}
        <div className={cn(
          "px-4 py-3 border-t transition-colors duration-500",
          isHighIntent ? "border-amber-200" : "border-slate-200"
        )}>
          <div className={cn(
            "flex items-end gap-3 rounded-2xl border px-4 py-3 bg-white transition-all duration-300 shadow-sm",
            state.isLoading
              ? "border-slate-200"
              : isHighIntent
              ? "border-amber-300 shadow-md shadow-amber-100"
              : "border-slate-200 focus-within:border-indigo-400 focus-within:shadow-md focus-within:shadow-indigo-100"
          )}>
            <TextareaAutosize
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={state.isLoading ? "Stream is thinking…" : "Ask me about AutoStream…"}
              disabled={state.isLoading}
              minRows={1}
              maxRows={4}
              className="flex-1 bg-transparent text-sm text-slate-800 placeholder:text-slate-400 resize-none outline-none leading-relaxed disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || state.isLoading}
              className={cn(
                "w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200",
                input.trim() && !state.isLoading
                  ? "bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-200"
                  : "bg-slate-100 text-slate-400 cursor-not-allowed"
              )}
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
          <p className="text-[10px] text-slate-400 text-center mt-2">
            Press Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>

      {/* ── Lead panel ──────────────────────────────────────────────────── */}
      <LeadPanel
        stage={state.stage}
        leadData={state.leadData}
        leadCaptured={state.leadCaptured}
      />
    </div>
  );
}
