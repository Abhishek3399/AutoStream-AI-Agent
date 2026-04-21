import { ChatInterface } from "@/components/ChatInterface";
import { Zap } from "lucide-react";

export default function HomePage() {
  return (
    <div className="relative min-h-screen flex flex-col bg-[#f5f4f0] overflow-hidden">
      {/* Ambient gradient */}
      <div className="pointer-events-none fixed inset-0 bg-radial-center" />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 md:px-12 py-5 border-b border-slate-200 bg-[#f5f4f0]/90 backdrop-blur-sm sticky top-0">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-md shadow-violet-200">
            <Zap className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-syne font-bold text-slate-900 tracking-tight">
            AutoStream
          </span>
        </div>

        <nav className="hidden md:flex items-center gap-6 text-sm text-slate-500">
          <a href="#" className="hover:text-slate-900 transition-colors">Features</a>
          <a href="#" className="hover:text-slate-900 transition-colors">Pricing</a>
          <a href="#" className="hover:text-slate-900 transition-colors">Docs</a>
        </nav>

        <div className="flex items-center gap-3">
          <a href="#" className="text-sm text-slate-500 hover:text-slate-900 transition-colors hidden md:block">
            Sign in
          </a>
          <a href="#" className="text-sm px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-colors shadow-sm shadow-indigo-200">
            Start free trial
          </a>
        </div>
      </nav>

      {/* Hero + Chat */}
      <main className="relative z-10 flex flex-col flex-1 items-center px-4 md:px-6 pt-12 pb-8">
        <div className="text-center mb-8 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-violet-200 bg-violet-50 text-violet-700 text-xs font-semibold mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-pulse" />
            AI-powered video editing
          </div>
          <h1 className="font-syne font-bold text-3xl md:text-4xl text-slate-900 leading-tight mb-3">
            Edit faster.
            <br />
            <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
              Publish smarter.
            </span>
          </h1>
          <p className="text-slate-500 text-sm md:text-base leading-relaxed">
            Ask Stream anything about AutoStream — pricing, features, or how to
            get started. Our AI assistant is here to help.
          </p>
        </div>

        {/* Chat container */}
        <div className="w-full max-w-5xl flex-1 flex flex-col min-h-0">
          <div
            className="flex-1 flex flex-col min-h-0 rounded-2xl border border-slate-200 bg-white/90 backdrop-blur-xl overflow-hidden shadow-xl shadow-slate-200/60"
            style={{ maxHeight: "calc(100vh - 280px)", minHeight: 480 }}
          >
            <ChatInterface />
          </div>
        </div>

        <p className="mt-6 text-[11px] text-slate-400">
          AutoStream AI assistant · Powered by Claude · Responses grounded in official documentation
        </p>
      </main>
    </div>
  );
}
