"use client";

import React from "react";
import { Search, Brain, Wrench, ShieldCheck, ArrowRight, CheckCircle2, Loader2 } from "lucide-react";
import { AgentName } from "@/types";

interface AgentPipelineProps {
  currentAgent: AgentName;
  status: string;
  iteration: number;
}

const AGENTS = [
  {
    id: "SCOUT",
    name: "Agent 1: SCOUT",
    role: "Repository & Error Analysis",
    member: "Member 1",
    icon: Search,
    color: "emerald",
    description: "Inspects codebase, runs baseline tests, isolates failing modules"
  },
  {
    id: "DETECTIVE",
    name: "Agent 2: DETECTIVE",
    role: "Root Cause & Reasoning",
    member: "Member 2",
    icon: Brain,
    color: "violet",
    description: "Traces call sites, generates hypotheses, isolates defect root cause"
  },
  {
    id: "REPAIRER",
    name: "Agent 3: REPAIRER",
    role: "Fix Generation & Code Repair",
    member: "Member 3",
    icon: Wrench,
    color: "amber",
    description: "Checkpoints git state, crafts minimal safe patch, applies diff"
  },
  {
    id: "GUARDIAN",
    name: "Agent 4: GUARDIAN",
    role: "Validation & Testing",
    member: "Member 4",
    icon: ShieldCheck,
    color: "teal",
    description: "Re-runs tests, checks regressions, verifies fix or triggers rollback"
  }
];

export const AgentPipeline: React.FC<AgentPipelineProps> = ({ currentAgent, status, iteration }) => {
  const getAgentIndex = (agent: AgentName) => {
    switch (agent) {
      case "SCOUT": return 0;
      case "DETECTIVE": return 1;
      case "REPAIRER": return 2;
      case "GUARDIAN": return 3;
      default: return 0;
    }
  };

  const activeIndex = getAgentIndex(currentAgent);

  return (
    <div className="bg-[#111116] border border-[#22222d] rounded-xl p-5 shadow-lg shadow-black/30">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#22222d]">
        <div className="flex items-center space-x-2">
          <span className="text-xs uppercase font-bold tracking-wider text-zinc-400">
            Primary Agentic AI Pipeline
          </span>
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#1c1c26] text-zinc-300 font-mono border border-[#2c2c3a]">
            Iteration {iteration} / 5
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-zinc-400 font-medium">State:</span>
          <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 uppercase">
            {status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
        {AGENTS.map((agent, index) => {
          const Icon = agent.icon;
          const isActive = currentAgent === agent.id && status !== "FIXED" && status !== "FAILED";
          const isCompleted = index < activeIndex || status === "FIXED";

          return (
            <div
              key={agent.id}
              className={`relative rounded-xl p-4 border transition-all duration-300 ${
                isActive
                  ? "bg-[#181824] border-emerald-400 ring-2 ring-emerald-500/30 shadow-lg shadow-emerald-500/15"
                  : isCompleted
                  ? "bg-[#14141c] border-emerald-500/40 opacity-90"
                  : "bg-[#111116] border-[#22222d] opacity-60"
              }`}
            >
              {/* Header Badge */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                  {agent.member}
                </span>
                {isActive ? (
                  <span className="flex items-center space-x-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500 text-white animate-pulse">
                    <Loader2 className="h-2.5 w-2.5 animate-spin" />
                    <span>Active</span>
                  </span>
                ) : isCompleted ? (
                  <span className="flex items-center space-x-1 text-[10px] font-medium text-emerald-400">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>Done</span>
                  </span>
                ) : (
                  <span className="text-[10px] text-zinc-500">Standby</span>
                )}
              </div>

              {/* Title & Icon */}
              <div className="flex items-center space-x-3 mb-2">
                <div
                  className={`p-2 rounded-lg ${
                    isActive
                      ? "bg-emerald-500/20 text-emerald-400"
                      : isCompleted
                      ? "bg-emerald-500/15 text-emerald-400"
                      : "bg-[#1c1c26] text-zinc-400"
                  }`}
                >
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white tracking-tight">{agent.name}</h3>
                  <p className="text-[11px] text-zinc-300 font-medium">{agent.role}</p>
                </div>
              </div>

              {/* Description */}
              <p className="text-xs text-zinc-400 leading-relaxed mt-1">
                {agent.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
