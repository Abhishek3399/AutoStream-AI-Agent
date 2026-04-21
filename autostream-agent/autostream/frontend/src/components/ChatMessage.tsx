"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ChatMessage as ChatMessageType } from "@/types";

interface ChatMessageProps {
  message: ChatMessageType;
  isLatest?: boolean;
}

export function ChatMessage({ message, isLatest }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
      className={cn("flex items-end gap-3 mb-4", isUser && "flex-row-reverse")}
    >
      {/* Agent avatar */}
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex-shrink-0 flex items-center justify-center text-white text-[10px] font-bold shadow-md shadow-violet-200">
          S
        </div>
      )}

      {/* Bubble */}
      <div
        className={cn(
          "max-w-[78%] px-4 py-3 rounded-2xl text-sm leading-relaxed",
          isUser
            ? "bg-gradient-to-br from-indigo-600 to-indigo-500 text-white rounded-br-sm shadow-md shadow-indigo-200"
            : "bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm",
          isLatest && !isUser && "shadow-md"
        )}
      >
        {message.content}

        <p
          className={cn(
            "text-[10px] mt-1.5 select-none",
            isUser ? "text-indigo-200/80 text-right" : "text-slate-400"
          )}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </motion.div>
  );
}
