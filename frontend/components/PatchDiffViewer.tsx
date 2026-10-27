"use client";

import React from "react";
import { GitCommit, GitBranch, FileDiff, Check } from "lucide-react";
import { DiffData } from "@/types";

interface PatchDiffViewerProps {
  diffData?: DiffData;
  checkpoint?: string;
}

export const PatchDiffViewer: React.FC<PatchDiffViewerProps> = ({ diffData, checkpoint }) => {
  const diffLines = (diffData?.diff || "").split("\n");

  return (
    <div className="bg-[#111116] border border-[#22222d] rounded-xl p-5 shadow-lg shadow-black/30 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-[#22222d]">
        <div className="flex items-center space-x-2">
          <FileDiff className="h-4 w-4 text-amber-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Agent 3 (Repairer) Code Patch & Unified Git Diff
          </h3>
        </div>
        {checkpoint && (
          <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-[#1c1c28] border border-[#2c2c3d] text-zinc-300 text-xs font-mono">
            <GitBranch className="h-3 w-3 text-emerald-400" />
            <span>{checkpoint}</span>
          </div>
        )}
      </div>

      {/* Summary and modified files header */}
      {diffData?.summary && (
        <div className="bg-[#16161f] border border-[#232330] rounded-lg p-3 text-xs space-y-2">
          <div className="flex items-center space-x-2 text-zinc-300 font-medium">
            <GitCommit className="h-3.5 w-3.5 text-amber-400" />
            <span>Patch Summary: {diffData.summary}</span>
          </div>
          {diffData.modified_files.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              <span className="text-[11px] text-zinc-500 mr-1 self-center">Modified:</span>
              {diffData.modified_files.map((file, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded text-[11px] font-mono bg-amber-500/10 text-amber-300 border border-amber-500/20"
                >
                  {file}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Diff Viewer */}
      {diffLines.length > 0 && diffData?.diff ? (
        <div className="bg-black/80 border border-[#232330] rounded-lg p-3 font-mono text-[12px] max-h-72 overflow-y-auto overflow-x-auto leading-relaxed shadow-inner">
          {diffLines.map((line, idx) => {
            let lineClass = "text-slate-400";
            let bgClass = "bg-transparent";

            if (line.startsWith("+") && !line.startsWith("+++")) {
              lineClass = "text-emerald-300";
              bgClass = "bg-emerald-950/30";
            } else if (line.startsWith("-") && !line.startsWith("---")) {
              lineClass = "text-rose-300";
              bgClass = "bg-rose-950/30";
            } else if (line.startsWith("@@")) {
              lineClass = "text-cyan-400";
              bgClass = "bg-cyan-950/20";
            }

            return (
              <div
                key={idx}
                className={`px-1.5 py-0.2 rounded-sm ${bgClass} ${lineClass} whitespace-pre`}
              >
                {line}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="py-8 text-center text-slate-500 text-xs italic">
          No code patches generated yet. Awaiting Repairer execution.
        </div>
      )}
    </div>
  );
};
