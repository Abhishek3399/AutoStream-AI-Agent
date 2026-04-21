"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, User, Mail, Tv2 } from "lucide-react";
import type { ConversationStage, LeadData } from "@/types";

interface LeadPanelProps {
  stage: ConversationStage;
  leadData: LeadData;
  leadCaptured: boolean;
}

interface FieldStatus {
  icon: React.ElementType;
  label: string;
  value?: string;
  active: boolean;
  done: boolean;
}

function useFields(stage: ConversationStage, leadData: LeadData): FieldStatus[] {
  return [
    { icon: User,  label: "Full Name",        value: leadData.name,     active: stage === "collecting_name",     done: !!leadData.name     },
    { icon: Mail,  label: "Email Address",     value: leadData.email,    active: stage === "collecting_email",    done: !!leadData.email    },
    { icon: Tv2,   label: "Creator Platform",  value: leadData.platform, active: stage === "collecting_platform", done: !!leadData.platform },
  ];
}

export function LeadPanel({ stage, leadData, leadCaptured }: LeadPanelProps) {
  const visible =
    stage !== "chat" ||
    leadCaptured ||
    !!(leadData.name || leadData.email || leadData.platform);

  const fields = useFields(stage, leadData);
  const completedCount = fields.filter((f) => f.done).length;

  return (
    <AnimatePresence>
      {visible && (
        <motion.aside
          initial={{ opacity: 0, x: 32 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 32 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="w-64 flex-shrink-0 hidden lg:flex flex-col gap-4"
        >
          {/* Progress card */}
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
                Lead Capture
              </span>
              <span className="text-xs text-slate-400 font-semibold">
                {completedCount}/3
              </span>
            </div>

            {/* Progress bar */}
            <div className="h-1 bg-slate-100 rounded-full mb-5 overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-violet-500 to-amber-400 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${(completedCount / 3) * 100}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
            </div>

            {/* Fields */}
            <ul className="space-y-3">
              {fields.map((f) => {
                const Icon = f.icon;
                return (
                  <li key={f.label} className="flex items-center gap-3">
                    <motion.div
                      animate={{
                        backgroundColor: f.done
                          ? "rgba(124,58,237,0.10)"
                          : f.active
                          ? "rgba(79,70,229,0.07)"
                          : "rgba(0,0,0,0.04)",
                      }}
                      className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                    >
                      {f.done ? (
                        <CheckCircle className="w-3.5 h-3.5 text-violet-600" />
                      ) : (
                        <Icon className={`w-3.5 h-3.5 ${f.active ? "text-indigo-500" : "text-slate-400"}`} />
                      )}
                    </motion.div>
                    <div className="min-w-0">
                      <p className={`text-xs font-medium truncate ${
                        f.done ? "text-slate-700" : f.active ? "text-slate-900" : "text-slate-400"
                      }`}>
                        {f.done && f.value ? f.value : f.label}
                      </p>
                      {f.active && !f.done && (
                        <p className="text-[10px] text-indigo-500 mt-0.5">Waiting…</p>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Success card */}
          <AnimatePresence>
            {leadCaptured && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 text-center shadow-sm"
              >
                <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                </div>
                <p className="text-sm font-semibold text-emerald-800 mb-1">
                  Lead Captured!
                </p>
                <p className="text-xs text-emerald-600">
                  Our team will reach out within 24 hours.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
