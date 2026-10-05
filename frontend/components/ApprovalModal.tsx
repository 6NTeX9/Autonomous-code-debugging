"use client";

import React from "react";
import { AlertCircle, Check, X, ShieldAlert } from "lucide-react";

interface ApprovalModalProps {
  isOpen: boolean;
  iteration: number;
  rootCause?: string;
  proposedFix?: string;
  diff?: string;
  confidence?: number;
  onDecision: (action: "APPROVE" | "REJECT" | "CANCEL") => void;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({
  isOpen,
  iteration,
  rootCause,
  proposedFix,
  diff,
  confidence = 0.94,
  onDecision,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-[#0f172a] border border-amber-500/40 rounded-2xl max-w-xl w-full flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="px-6 py-4 border-b border-slate-800 bg-amber-500/10 flex items-center space-x-3">
          <ShieldAlert className="h-5 w-5 text-amber-400" />
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide uppercase">
              Human Intervention & Approval Required
            </h3>
            <p className="text-xs text-amber-200/80">
              Workflow paused before patch application for Iteration {iteration}
            </p>
          </div>
        </div>

        <div className="p-6 space-y-4 text-xs">
          <div>
            <span className="text-[11px] uppercase font-bold text-slate-400">Diagnosis</span>
            <p className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg text-slate-200 mt-1">
              {rootCause || "Defect identified in inspected files."}
            </p>
          </div>

          <div>
            <span className="text-[11px] uppercase font-bold text-slate-400">Proposed Fix & Strategy</span>
            <p className="bg-slate-900 border border-slate-800 p-2.5 rounded-lg text-emerald-300 font-mono mt-1">
              {proposedFix || "Apply defensive null check and correct formula."}
            </p>
          </div>

          {diff && (
            <div>
              <span className="text-[11px] uppercase font-bold text-slate-400">Patch Diff Preview</span>
              <div className="bg-black/60 border border-slate-800 p-2.5 rounded-lg font-mono text-[11px] max-h-36 overflow-y-auto text-slate-300 mt-1 whitespace-pre">
                {diff}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
            <span>Agent Confidence: <strong className="text-purple-400">{Math.round(confidence * 100)}%</strong></span>
            <span>Safety Rule: Git checkpoint active</span>
          </div>
        </div>

        <div className="px-6 py-3.5 border-t border-slate-800 bg-slate-900/50 flex items-center justify-end space-x-2">
          <button
            onClick={() => onDecision("CANCEL")}
            className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition-colors"
          >
            Cancel Session
          </button>
          <button
            onClick={() => onDecision("REJECT")}
            className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 border border-rose-500/40 transition-colors"
          >
            Reject Patch
          </button>
          <button
            onClick={() => onDecision("APPROVE")}
            className="px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-white shadow-lg shadow-emerald-500/20 transition-colors"
          >
            Approve & Apply Patch
          </button>
        </div>
      </div>
    </div>
  );
};
