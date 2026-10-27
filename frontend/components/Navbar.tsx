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
    <header className="border-b border-[#22222d] bg-[#0a0a0e]/85 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5 shadow-md shadow-black/40">
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
          <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-emerald-500 to-violet-600 flex items-center justify-center shadow-lg shadow-emerald-500/25">
            <Terminal className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-bold text-lg text-white tracking-wide">
                AUTONOMOUS CODE DEBUGGING AGENT
              </h1>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                ILP CCA 2
              </span>
            </div>
            <p className="text-xs text-zinc-400">
              Four-Agent Autonomous Self-Healing Pipeline (Scout • Detective • Repairer • Guardian)
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          {/* Mode Switcher */}
          <div className="flex items-center bg-[#13131a] border border-[#272736] rounded-lg p-1 text-xs">
            <button
              onClick={() => onToggleMode("AUTO")}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                mode === "AUTO"
                  ? "bg-emerald-500 text-white shadow-sm shadow-emerald-500/25"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Autonomous (AUTO)
            </button>
            <button
              onClick={() => onToggleMode("APPROVAL_REQUIRED")}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                mode === "APPROVAL_REQUIRED"
                  ? "bg-amber-500 text-white shadow-sm shadow-amber-500/25"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Approval Required
            </button>
          </div>

          {/* Quick Demo Project Button */}
          <button
            onClick={onLoadSample}
            disabled={isRunning}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#181822] hover:bg-[#222230] border border-[#2c2c3c] text-zinc-200 transition-all disabled:opacity-50"
          >
            <Cpu className="h-3.5 w-3.5 text-emerald-400" />
            <span>Load Demo</span>
          </button>

          {/* Upload Project (.zip) Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isRunning}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#181822] hover:bg-[#222230] border border-violet-500/40 text-violet-300 hover:text-violet-200 transition-all disabled:opacity-50"
            title="Upload custom repository (.zip)"
          >
            <Upload className="h-3.5 w-3.5 text-violet-400" />
            <span>Upload (.zip)</span>
          </button>

          {/* Reset Button */}
          <button
            onClick={onReset}
            disabled={isRunning}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-[#1d1d28] border border-transparent hover:border-[#2f2f40] transition-all disabled:opacity-50"
            title="Reset Workspace"
          >
            <RefreshCw className="h-4 w-4" />
          </button>

          {/* Start Debugging Action */}
          <button
            onClick={onStartDebug}
            disabled={isRunning || !hasProject}
            className="flex items-center space-x-2 px-4 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/25 transition-all disabled:opacity-50 cursor-pointer"
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
