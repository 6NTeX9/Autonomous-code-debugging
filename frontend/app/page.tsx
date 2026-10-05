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
import { FolderGit2, Cpu, FileCode2, FlaskConical, Award } from "lucide-react";

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
    startDebugging,
    submitHumanDecision,
    resetAll,
  } = useDebugSession();

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      {/* Navigation */}
      <Navbar
        mode={mode}
        onToggleMode={setMode}
        onLoadSample={loadSampleProject}
        onStartDebug={startDebugging}
        isRunning={isRunning}
        hasProject={!!project}
        onReset={resetAll}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Project Header Bar */}
        {project ? (
          <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
                <FolderGit2 className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-sm font-bold text-white tracking-wide">
                    {project.name}
                  </h2>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    ID: {project.id.slice(0, 8)}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">{project.description}</p>
              </div>
            </div>

            {/* Badges */}
            <div className="flex items-center space-x-3 text-xs">
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                <FileCode2 className="h-3.5 w-3.5 text-blue-400" />
                <span>{project.language || "TypeScript"}</span>
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                <Cpu className="h-3.5 w-3.5 text-purple-400" />
                <span>{project.framework || "Express"}</span>
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                <FlaskConical className="h-3.5 w-3.5 text-emerald-400" />
                <span>{project.test_framework || "Jest"}</span>
              </div>
              {report && (
                <button
                  onClick={() => setIsReportOpen(true)}
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold hover:bg-emerald-500/30 transition-colors"
                >
                  <Award className="h-3.5 w-3.5 text-emerald-400" />
                  <span>View Final Report</span>
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-[#0f172a] border border-dashed border-slate-800 rounded-xl p-8 text-center space-y-3">
            <Cpu className="h-8 w-8 text-sky-400 mx-auto opacity-70" />
            <h2 className="text-sm font-bold text-white">No Repository Loaded</h2>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Click <strong>&quot;Load Demo Project&quot;</strong> in the navigation header to load the realistic E-commerce microservice with 3 intentional bugs (21 tests: 18 passing, 3 failing).
            </p>
            <button
              onClick={loadSampleProject}
              className="px-4 py-2 rounded-lg text-xs font-bold bg-sky-500 hover:bg-sky-400 text-white shadow-lg shadow-sky-500/20 transition-all inline-flex items-center space-x-2"
            >
              <Cpu className="h-4 w-4" />
              <span>Load Demo Project Now</span>
            </button>
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
