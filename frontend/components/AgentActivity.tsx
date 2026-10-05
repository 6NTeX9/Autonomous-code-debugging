"use client";

import React, { useEffect, useRef } from "react";
import { Terminal, Check, AlertCircle, Wrench, Shield, Play } from "lucide-react";
import { AgentEvent } from "@/types";

interface AgentActivityProps {
  events: AgentEvent[];
}

export const AgentActivity: React.FC<AgentActivityProps> = ({ events }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  const getEventBadge = (event: AgentEvent) => {
    switch (event.event) {
      case "AGENT_STARTED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-500/20 text-sky-400">AGENT START</span>;
      case "AGENT_COMPLETED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400">AGENT DONE</span>;
      case "TOOL_CALL":
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-500/20 text-indigo-300">TOOL CALL</span>;
      case "TOOL_RESULT":
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">TOOL RESULT</span>;
      case "REPOSITORY_ANALYZED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-600/30 text-sky-300">REPO ANALYZED</span>;
      case "ERROR_DETECTED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400">ERROR DETECTED</span>;
      case "HYPOTHESIS_CREATED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300">HYPOTHESIS</span>;
      case "ROOT_CAUSE_IDENTIFIED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-fuchsia-500/20 text-fuchsia-300">ROOT CAUSE</span>;
      case "PATCH_GENERATED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300">PATCH CREATED</span>;
      case "PATCH_APPLIED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-600/20 text-amber-200">PATCH APPLIED</span>;
      case "TEST_STARTED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300">TEST RUN</span>;
      case "TEST_COMPLETED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-500/20 text-teal-300">TEST DONE</span>;
      case "PATCH_REJECTED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/30 text-rose-300">REJECTED</span>;
      case "ROLLBACK":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-600/30 text-red-300">ROLLBACK</span>;
      case "DEBUGGING_COMPLETED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/30 text-emerald-300">COMPLETED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400">{event.event}</span>;
    }
  };

  const formatTime = (ts: string) => {
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch {
      return "";
    }
  };

  return (
    <div className="bg-[#0f172a] border border-slate-800 rounded-xl flex flex-col h-[380px] shadow-sm">
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
        <div className="flex items-center space-x-2">
          <Terminal className="h-4 w-4 text-sky-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Agent Activity & Tool Event Stream
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          {events.length} events logged
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2.5 font-mono text-xs">
        {events.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-500 italic">
            Awaiting agent pipeline execution...
          </div>
        ) : (
          events.map((ev, index) => (
            <div
              key={ev.id || index}
              className="flex items-start space-x-2.5 py-1 border-b border-slate-800/40 last:border-0 hover:bg-slate-800/30 rounded px-1.5 transition-colors"
            >
              <span className="text-slate-500 text-[11px] shrink-0 pt-0.5">
                {formatTime(ev.timestamp)}
              </span>
              <span className="text-sky-400 font-semibold text-[11px] shrink-0">
                [{ev.agent}]
              </span>
              <div className="shrink-0">{getEventBadge(ev)}</div>
              {ev.tool && (
                <span className="text-amber-400/90 font-mono text-[11px] shrink-0">
                  {ev.tool}()
                </span>
              )}
              <span className="text-slate-300 break-words flex-1">
                {ev.message || (ev.payload ? JSON.stringify(ev.payload) : "")}
              </span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
