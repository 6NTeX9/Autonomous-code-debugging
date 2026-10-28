"use client";

import React from "react";
import { Navbar } from "@/components/Navbar";
import { AgentPipeline } from "@/components/AgentPipeline";
import { AgentActivity } from "@/components/AgentActivity";
import { ReasoningSummary } from "@/components/ReasoningSummary";
import { ErrorPanel } from "@/components/ErrorPanel";
import { PatchDiffViewer } from "@/components/PatchDiffViewer";
import { ValidationPanel } from "@/components/ValidationPanel";
import { IterationTimeline } from "@/components/IterationTimeline";
import { ReportModal } from "@/components/ReportModal";
import { ApprovalModal } from "@/components/ApprovalModal";
import { useDebugSession } from "@/hooks/useDebugSession";
import { FolderGit2, Cpu, FileCode2, FlaskConical, Award, Upload, Download } from "lucide-react";

export default function Home() {
  const {
    project,
    session,
    events,
    currentAgent,
    status,
    iteration,
    mode,
    setMode,
    rootCause,
    confidence,
    evidence,
    repairStrategy,
    hypotheses,
    reasoningSummary,
    failures,
    stackTrace,
    diffData,
    checkpoint,
    testsBefore,
    testsAfter,
    regressions,
    validationDecision,
    validationSummary,
    iterationRecords,
    report,
    isReportOpen,
    setIsReportOpen,
    isApprovalOpen,
    isRunning,
    loadSampleProject,
    uploadProject,
    startDebugging,
    submitHumanDecision,
    resetAll,
  } = useDebugSession();

  const emptyFileInputRef = React.useRef<HTMLInputElement>(null);

  const handleEmptyFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadProject(e.target.files[0]);
      e.target.value = "";
    }
  };

  return (
    <div className="min-h-screen bg-[#070709] text-zinc-100 flex flex-col font-sans">
      {/* Navigation */}
      <Navbar
        mode={mode}
        onToggleMode={setMode}
        onLoadSample={loadSampleProject}
        onUploadProject={uploadProject}
        onStartDebug={startDebugging}
        isRunning={isRunning}
        hasProject={!!project}
        onReset={resetAll}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Project Header Bar */}
        {project ? (
          <div className="bg-[#111116] border border-[#22222a] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-lg shadow-black/40">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <FolderGit2 className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-sm font-bold text-white tracking-wide">
                    {project.name}
                  </h2>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1c1c24] text-zinc-300 border border-[#2e2e38]">
                    ID: {project.id.slice(0, 8)}
                  </span>
                </div>
                <p className="text-xs text-zinc-400 mt-0.5">{project.description}</p>
              </div>
            </div>

            {/* Badges */}
            <div className="flex items-center space-x-3 text-xs">
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#16161d] border border-[#262632] text-zinc-300">
                <FileCode2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>{project.language || "TypeScript"}</span>
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#16161d] border border-[#262632] text-zinc-300">
                <Cpu className="h-3.5 w-3.5 text-violet-400" />
                <span>{project.framework || "Express"}</span>
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#16161d] border border-[#262632] text-zinc-300">
                <FlaskConical className="h-3.5 w-3.5 text-amber-400" />
                <span>{project.test_framework || "Jest"}</span>
              </div>
              <a
                href={`/api/projects/${project.id}/download`}
                download
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#16161d] hover:bg-[#20202a] border border-emerald-500/30 text-emerald-300 hover:text-emerald-200 text-xs font-semibold transition-all shadow-sm shadow-emerald-500/10 cursor-pointer"
                title="Download the repaired project workspace (.zip) with all agent patches applied"
              >
                <Download className="h-3.5 w-3.5 text-emerald-400" />
                <span>Download Repaired Code (.zip)</span>
              </a>
              {report && (
                <button
                  onClick={() => setIsReportOpen(true)}
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold hover:bg-emerald-500/30 transition-colors shadow-sm shadow-emerald-500/20"
                >
                  <Award className="h-3.5 w-3.5 text-emerald-400" />
                  <span>View Final Report</span>
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-[#111116] border border-dashed border-[#272734] rounded-xl p-8 text-center space-y-4 shadow-xl">
            <div className="h-12 w-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto shadow-inner">
              <Cpu className="h-6 w-6" />
            </div>
            <h2 className="text-sm font-bold text-white tracking-wide">No Repository Loaded</h2>
            <p className="text-xs text-zinc-400 max-w-md mx-auto">
              Load our built-in 21-test E-commerce service with 3 realistic defects, or upload any custom Python or TypeScript/Node project (.zip) to debug autonomously.
            </p>
            <input
              type="file"
              ref={emptyFileInputRef}
              accept=".zip"
              onChange={handleEmptyFileChange}
              className="hidden"
            />
            <div className="flex items-center justify-center space-x-3 pt-1">
              <button
                onClick={loadSampleProject}
                className="px-4 py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/20 transition-all inline-flex items-center space-x-2 cursor-pointer"
              >
                <Cpu className="h-4 w-4" />
                <span>Load Demo Project Now</span>
              </button>
              <button
                onClick={() => emptyFileInputRef.current?.click()}
                className="px-4 py-2 rounded-lg text-xs font-bold bg-[#181822] hover:bg-[#222230] border border-violet-500/40 text-violet-300 hover:text-violet-200 shadow-md transition-all inline-flex items-center space-x-2 cursor-pointer"
              >
                <Upload className="h-4 w-4 text-violet-400" />
                <span>Upload Custom Project (.zip)</span>
              </button>
            </div>
          </div>
        )}

        {/* Primary Agent Pipeline Visualization */}
        <AgentPipeline
          currentAgent={currentAgent}
          status={status}
          iteration={iteration}
        />

        {/* Grid Panels Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Observability, Errors, Timeline */}
          <div className="space-y-6">
            <AgentActivity events={events} />
            <ErrorPanel failures={failures} stackTrace={stackTrace} />
            <IterationTimeline
              currentIteration={iteration}
              records={iterationRecords}
            />
          </div>

          {/* Right Column: Reasoning, Code Patch, Validation */}
          <div className="space-y-6">
            <ReasoningSummary
              rootCause={rootCause}
              confidence={confidence}
              evidence={evidence}
              repairStrategy={repairStrategy}
              hypotheses={hypotheses}
              summaryText={reasoningSummary}
            />
            <PatchDiffViewer diffData={diffData} checkpoint={checkpoint} />
            <ValidationPanel
              testsBefore={testsBefore}
              testsAfter={testsAfter}
              regressions={regressions}
              decision={validationDecision}
              summary={validationSummary}
            />
          </div>
        </div>
      </main>

      {/* Modals */}
      <ReportModal
        report={report}
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
      />

      <ApprovalModal
        isOpen={isApprovalOpen}
        iteration={iteration}
        rootCause={rootCause}
        proposedFix={repairStrategy}
        diff={diffData?.diff}
        confidence={confidence}
        onDecision={submitHumanDecision}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-[#0f172a]/40 py-4 px-6 text-center text-xs text-slate-500">
        Autonomous Code Debugging Agent • ILP CCA 2 • Group 4 Students Autonomous Agentic Architecture
      </footer>
    </div>
  );
}
