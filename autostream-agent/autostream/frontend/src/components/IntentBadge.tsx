"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { Intent } from "@/types";

interface IntentBadgeProps {
  intent: Intent;
}

const CONFIG: Record<
  Intent,
  { label: string; dot: string; ring: string; bg: string; text: string }
> = {
  greeting: {
    label: "Greeting",
    dot: "bg-slate-400",
    ring: "ring-slate-300",
    bg: "bg-slate-100",
    text: "text-slate-500",
  },
  inquiry: {
    label: "Exploring",
    dot: "bg-blue-400",
    ring: "ring-blue-200",
    bg: "bg-blue-50",
    text: "text-blue-600",
  },
  high_intent: {
    label: "High Intent",
    dot: "bg-amber-400 animate-pulse",
    ring: "ring-amber-200",
    bg: "bg-amber-50",
    text: "text-amber-700",
  },
};

export function IntentBadge({ intent }: IntentBadgeProps) {
  const c = CONFIG[intent];

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={intent}
        initial={{ opacity: 0, scale: 0.85, y: -4 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.85, y: 4 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
        className={`
          inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold
          ring-1 ${c.ring} ${c.bg} ${c.text}
        `}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
        {c.label}
      </motion.div>
    </AnimatePresence>
  );
}
