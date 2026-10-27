"use client";

import React from "react";
import { AlertTriangle, FileCode, CheckCircle } from "lucide-react";
import { TestFailure } from "@/types";

interface ErrorPanelProps {
  failures: TestFailure[];
  stackTrace?: string;
}

export const ErrorPanel: React.FC<ErrorPanelProps> = ({ failures, stackTrace }) => {
  return (
    <div className="bg-[#111116] border border-[#22222d] rounded-xl p-5 shadow-lg shadow-black/30 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-[#22222d]">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4 text-rose-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Failing Test Assertions & Stack Trace
          </h3>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
          {failures.length} Failure(s)
        </span>
      </div>

      {failures.length === 0 ? (
        <div className="flex items-center justify-center space-x-2 py-8 text-emerald-400 text-xs">
          <CheckCircle className="h-4 w-4" />
          <span>Zero failing assertions detected in current test run.</span>
        </div>
      ) : (
        <div className="space-y-3">
          {failures.map((fail, i) => (
            <div
              key={i}
              className="bg-[#16161f] border border-rose-950/80 rounded-lg p-3 space-y-2 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-rose-300 font-mono">
                  ✕ {fail.test}
                </span>
                {fail.file && (
                  <span className="flex items-center space-x-1 text-[11px] text-zinc-400 font-mono">
                    <FileCode className="h-3 w-3" />
                    <span>{fail.file.split("/").pop()}</span>
                  </span>
                )}
              </div>
              <div className="bg-black/50 border border-[#262634] rounded p-2 text-zinc-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap leading-relaxed">
                {fail.error}
              </div>
            </div>
          ))}
        </div>
      )}

      {stackTrace && (
        <div className="space-y-1.5 pt-2 border-t border-[#22222d]">
          <span className="text-[11px] uppercase font-bold text-zinc-400 tracking-wider">
            Raw Test Runner Log / Trace
          </span>
          <div className="bg-black/50 border border-slate-800/80 rounded-lg p-3 text-[11px] font-mono text-slate-400 max-h-48 overflow-y-auto whitespace-pre-wrap leading-tight">
            {stackTrace}
          </div>
        </div>
      )}
    </div>
  );
};
