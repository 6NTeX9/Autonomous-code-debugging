"use client";

import React from "react";
import { Brain, CheckCircle2, ShieldAlert, Cpu, Sparkles } from "lucide-react";

interface Hypothesis {
  description: string;
  evidence: string[];
  confidence: number;
}

interface ReasoningSummaryProps {
  rootCause?: string;
  confidence?: number;
  evidence?: string[];
  repairStrategy?: string;
  hypotheses?: Hypothesis[];
  summaryText?: string;
}

export const ReasoningSummary: React.FC<ReasoningSummaryProps> = ({
  rootCause,
  confidence = 0.94,
  evidence = [],
  repairStrategy,
  hypotheses = [],
  summaryText,
}) => {
  return (
    <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Brain className="h-4 w-4 text-purple-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Agent 2 (Detective) Reasoning & Evidence Analysis
          </h3>
        </div>
        {confidence !== undefined && (
          <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold">
            <Sparkles className="h-3 w-3" />
            <span>Confidence: {Math.round(confidence * 100)}%</span>
          </div>
        )}
      </div>

      {/* Concise Evidence-Based Summary */}
      {summaryText && (
        <div className="bg-purple-950/20 border border-purple-800/40 rounded-lg p-3 text-xs text-purple-200 leading-relaxed font-sans">
          <p className="font-semibold text-purple-300 mb-1 flex items-center space-x-1">
            <span>Detective Synthesis:</span>
          </p>
          <p>{summaryText}</p>
        </div>
      )}

      {/* Root Cause Decision */}
      {rootCause ? (
        <div className="space-y-1.5">
          <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
            Verified Root Cause
          </span>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs text-slate-200">
            {rootCause}
          </div>
        </div>
      ) : (
        <div className="py-6 text-center text-slate-500 text-xs italic">
          Root cause analysis will appear once Detective finishes source inspection.
        </div>
      )}

      {/* Ranked Hypotheses */}
      {hypotheses.length > 0 && (
        <div className="space-y-2">
          <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
            Investigated Hypotheses ({hypotheses.length})
          </span>
          <div className="space-y-2">
            {hypotheses.map((h, i) => (
              <div
                key={i}
                className="bg-slate-900/80 border border-slate-800 rounded-lg p-2.5 text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200">
                    Hypothesis {i + 1}
                  </span>
                  <span className="font-mono text-[11px] text-purple-400">
                    {Math.round(h.confidence * 100)}%
                  </span>
                </div>
                <p className="text-slate-400">{h.description}</p>
                {/* Confidence bar */}
                <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                  <div
                    className="bg-purple-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.round(h.confidence * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empirical Evidence */}
      {evidence.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
            Supporting Evidence
          </span>
          <ul className="space-y-1 text-xs text-slate-300">
            {evidence.map((ev, i) => (
              <li key={i} className="flex items-start space-x-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-sky-400 shrink-0 mt-0.5" />
                <span>{ev}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Repair Strategy */}
      {repairStrategy && (
        <div className="space-y-1.5 pt-1 border-t border-slate-800/80">
          <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
            Repair Strategy for Agent 3 (Repairer)
          </span>
          <p className="text-xs text-emerald-300 bg-emerald-950/20 border border-emerald-800/30 p-2.5 rounded-lg font-mono">
            {repairStrategy}
          </p>
        </div>
      )}
    </div>
  );
};
