"use client";

import React, { useRef } from "react";
import { Terminal, Shield, Play, Pause, RefreshCw, Cpu, Activity, Upload } from "lucide-react";

interface NavbarProps {
  mode: "AUTO" | "APPROVAL_REQUIRED";
  onToggleMode: (newMode: "AUTO" | "APPROVAL_REQUIRED") => void;
  onLoadSample: () => void;
  onUploadProject: (file: File) => void;
  onStartDebug: () => void;
  isRunning: boolean;
  hasProject: boolean;
  onReset: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  mode,
  onToggleMode,
  onLoadSample,
  onUploadProject,
  onStartDebug,
  isRunning,
  hasProject,
  onReset,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUploadProject(e.target.files[0]);
      e.target.value = "";
    }
  };

  return (
    <header className="border-b border-slate-800 bg-[#0f172a]/80 backdrop-blur sticky top-0 z-50 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Hidden File Input for Project Upload */}
        <input
          type="file"
          ref={fileInputRef}
          accept=".zip"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Brand / Title */}
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Terminal className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-bold text-lg text-white tracking-wide">
                AUTONOMOUS CODE DEBUGGING AGENT
              </h1>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                ILP CCA 2
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Four-Agent Autonomous Self-Healing Pipeline (Scout • Detective • Repairer • Guardian)
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          {/* Mode Switcher */}
          <div className="flex items-center bg-slate-900 border border-slate-700/60 rounded-lg p-1 text-xs">
            <button
              onClick={() => onToggleMode("AUTO")}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                mode === "AUTO"
                  ? "bg-sky-500 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Autonomous (AUTO)
            </button>
            <button
              onClick={() => onToggleMode("APPROVAL_REQUIRED")}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                mode === "APPROVAL_REQUIRED"
                  ? "bg-amber-500 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Approval Required
            </button>
          </div>

          {/* Quick Demo Project Button */}
          <button
            onClick={onLoadSample}
            disabled={isRunning}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 transition-all disabled:opacity-50"
          >
            <Cpu className="h-3.5 w-3.5 text-sky-400" />
            <span>Load Demo</span>
          </button>

          {/* Upload Project (.zip) Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isRunning}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 border border-slate-700 text-emerald-300 transition-all disabled:opacity-50"
            title="Upload custom repository (.zip)"
          >
            <Upload className="h-3.5 w-3.5 text-emerald-400" />
            <span>Upload (.zip)</span>
          </button>

          {/* Reset Button */}
          <button
            onClick={onReset}
            disabled={isRunning}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-transparent hover:border-slate-700 transition-all disabled:opacity-50"
            title="Reset Workspace"
          >
            <RefreshCw className="h-4 w-4" />
          </button>

          {/* Start Debugging Action */}
          <button
            onClick={onStartDebug}
            disabled={isRunning || !hasProject}
            className="flex items-center space-x-2 px-4 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/20 transition-all disabled:opacity-50 cursor-pointer"
          >
            {isRunning ? (
              <>
                <Activity className="h-3.5 w-3.5 animate-spin" />
                <span>Debugging in Progress...</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-white" />
                <span>Start Autonomous Debug</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
