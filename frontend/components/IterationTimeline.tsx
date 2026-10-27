"use client";

import React from "react";
import { History, CheckCircle2, XCircle, ArrowRight, RotateCcw } from "lucide-react";

interface IterationRecord {
  iteration: number;
  decision: string;
  passed: number;
  failed: number;
  timestamp?: string;
}

interface IterationTimelineProps {
  currentIteration: number;
  records: IterationRecord[];
}

export const IterationTimeline: React.FC<IterationTimelineProps> = ({ currentIteration, records }) => {
  return (
    <div className="bg-[#111116] border border-[#22222d] rounded-xl p-5 shadow-lg shadow-black/30 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-[#22222d]">
        <div className="flex items-center space-x-2">
          <History className="h-4 w-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Autonomous Debugging Loop & Iteration Timeline
          </h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">
          Max Iterations: 5
        </span>
      </div>

      <div className="space-y-3">
        {records.length === 0 ? (
          <div className="py-6 text-center text-zinc-500 text-xs italic">
            Iteration history will populate as the loop executes.
          </div>
        ) : (
          records.map((rec, i) => {
            const isSuccess = rec.decision === "PATCH_VERIFIED";
            const isPartial = rec.decision === "PARTIALLY_VERIFIED";
            return (
              <div
                key={i}
                className="bg-[#16161f] border border-[#232330] rounded-lg p-3 flex items-center justify-between text-xs"
              >
                <div className="flex items-center space-x-3">
                  <span className="font-bold text-white bg-[#1c1c28] px-2.5 py-1 rounded font-mono border border-[#2b2b3b]">
                    Iteration {rec.iteration}
                  </span>
                  <div className="flex items-center space-x-1.5 text-zinc-400 text-[11px] font-mono">
                    <span>SCOUT</span>
                    <ArrowRight className="h-2.5 w-2.5" />
                    <span>DETECTIVE</span>
                    <ArrowRight className="h-2.5 w-2.5" />
                    <span>REPAIRER</span>
                    <ArrowRight className="h-2.5 w-2.5" />
                    <span className="text-emerald-400 font-bold">GUARDIAN</span>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="font-mono text-zinc-300">
                    <span className="text-emerald-400 font-semibold">{rec.passed} P</span> /{" "}
                    <span className="text-rose-400 font-semibold">{rec.failed} F</span>
                  </span>
                  {isSuccess ? (
                    <span className="flex items-center space-x-1 text-emerald-400 font-bold text-xs bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      <CheckCircle2 className="h-3 w-3" />
                      <span>SUCCESS</span>
                    </span>
                  ) : isPartial ? (
                    <span className="flex items-center space-x-1 text-amber-400 font-semibold text-xs bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                      <RotateCcw className="h-3 w-3" />
                      <span>RETRY</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-1 text-rose-400 font-semibold text-xs bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                      <XCircle className="h-3 w-3" />
                      <span>FAILED</span>
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
