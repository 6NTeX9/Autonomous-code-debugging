"use client";

import React from "react";
import { ShieldCheck, CheckCircle2, XCircle, AlertOctagon, ArrowRight } from "lucide-react";

interface ValidationPanelProps {
  testsBefore?: { total: number; passed: number; failed: number };
  testsAfter?: { total: number; passed: number; failed: number };
  regressions?: number;
  decision?: string;
  summary?: string;
}

export const ValidationPanel: React.FC<ValidationPanelProps> = ({
  testsBefore = { total: 21, passed: 18, failed: 3 },
  testsAfter,
  regressions = 0,
  decision,
  summary,
}) => {
  const getDecisionBadge = () => {
    switch (decision) {
      case "PATCH_VERIFIED":
        return (
          <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            <span>PATCH VERIFIED</span>
          </span>
        );
      case "PARTIALLY_VERIFIED":
        return (
          <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30">
            <CheckCircle2 className="h-3.5 w-3.5 text-sky-400" />
            <span>PARTIALLY VERIFIED</span>
          </span>
        );
      case "PATCH_REJECTED":
        return (
          <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
            <XCircle className="h-3.5 w-3.5 text-rose-400" />
            <span>PATCH REJECTED</span>
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
            Awaiting Validation
          </span>
        );
    }
  };

  const beforePassedPct = Math.round((testsBefore.passed / (testsBefore.total || 1)) * 100);
  const afterPassedPct = testsAfter ? Math.round((testsAfter.passed / (testsAfter.total || 1)) * 100) : beforePassedPct;

  return (
    <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Agent 4 (Guardian) Test Suite Validation & Regression Gate
          </h3>
        </div>
        {getDecisionBadge()}
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Before Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-3.5 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold uppercase tracking-wider">Tests Baseline (Before)</span>
            <span className="font-mono text-slate-300">{testsBefore.total} Total</span>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono">
            <span className="text-emerald-400 font-semibold">{testsBefore.passed} Passed</span>
            <span className="text-rose-400 font-semibold">{testsBefore.failed} Failed</span>
          </div>
          {/* Progress bar */}
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full"
              style={{ width: `${beforePassedPct}%` }}
            />
          </div>
        </div>

        {/* After Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-3.5 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold uppercase tracking-wider">Tests Post-Repair (After)</span>
            <span className="font-mono text-slate-300">
              {testsAfter ? `${testsAfter.total} Total` : "Pending"}
            </span>
          </div>
          {testsAfter ? (
            <div className="flex items-center space-x-4 text-xs font-mono">
              <span className="text-emerald-400 font-semibold">{testsAfter.passed} Passed</span>
              <span className="text-rose-400 font-semibold">{testsAfter.failed} Failed</span>
            </div>
          ) : (
            <div className="text-xs text-slate-500 italic">Validation run pending patch application...</div>
          )}
          {/* Progress bar */}
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                testsAfter?.failed === 0 ? "bg-emerald-400" : "bg-sky-400"
              }`}
              style={{ width: `${afterPassedPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Regression & Decision Note */}
      <div className="flex items-center justify-between bg-slate-900/60 border border-slate-800 rounded-lg p-3 text-xs">
        <div className="flex items-center space-x-2">
          <AlertOctagon className={`h-4 w-4 ${regressions > 0 ? "text-rose-400" : "text-emerald-400"}`} />
          <span className="text-slate-300">
            Regressions Detected: <strong className={regressions > 0 ? "text-rose-400" : "text-emerald-400"}>{regressions}</strong>
          </span>
        </div>
        {summary && (
          <span className="text-slate-400 italic text-[11px] truncate max-w-md">
            {summary}
          </span>
        )}
      </div>
    </div>
  );
};
