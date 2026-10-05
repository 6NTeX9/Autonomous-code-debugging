"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Project, DebugSession, AgentEvent, DiffData, DebugReport, TestFailure, AgentName } from "@/types";

const API_BASE = "http://localhost:8000/api";
const WS_BASE = "ws://localhost:8000/ws";

export function useDebugSession() {
  const [project, setProject] = useState<Project | null>(null);
  const [session, setSession] = useState<DebugSession | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<AgentName>("SCOUT");
  const [status, setStatus] = useState<string>("INITIALIZING");
  const [iteration, setIteration] = useState<number>(1);
  const [mode, setMode] = useState<"AUTO" | "APPROVAL_REQUIRED">("AUTO");

  // Reasoning & Detective State
  const [rootCause, setRootCause] = useState<string | undefined>();
  const [confidence, setConfidence] = useState<number>(0.94);
  const [evidence, setEvidence] = useState<string[]>([]);
  const [repairStrategy, setRepairStrategy] = useState<string | undefined>();
  const [hypotheses, setHypotheses] = useState<any[]>([]);
  const [reasoningSummary, setReasoningSummary] = useState<string | undefined>();

  // Failures & Errors
  const [failures, setFailures] = useState<TestFailure[]>([]);
  const [stackTrace, setStackTrace] = useState<string | undefined>();

  // Patch & Diff
  const [diffData, setDiffData] = useState<DiffData | undefined>();
  const [checkpoint, setCheckpoint] = useState<string | undefined>();

  // Validation
  const [testsBefore, setTestsBefore] = useState<{ total: number; passed: number; failed: number }>({
    total: 21,
    passed: 18,
    failed: 3
  });
  const [testsAfter, setTestsAfter] = useState<{ total: number; passed: number; failed: number } | undefined>();
  const [regressions, setRegressions] = useState<number>(0);
  const [validationDecision, setValidationDecision] = useState<string | undefined>();
  const [validationSummary, setValidationSummary] = useState<string | undefined>();

  // Timeline
  const [iterationRecords, setIterationRecords] = useState<any[]>([]);

  // Report & Human In The Loop
  const [report, setReport] = useState<DebugReport | null>(null);
  const [isReportOpen, setIsReportOpen] = useState<boolean>(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState<boolean>(false);

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);
  const pollIntervalRef = useRef<any>(null);

  // Load Built-in Demo Project
  const loadSampleProject = async () => {
    try {
      const res = await fetch(`${API_BASE}/projects/sample`, { method: "POST" });
      if (!res.ok) throw new Error("Failed to load sample project");
      const data: Project = await res.json();
      setProject(data);
      // Pre-set baseline test status for UI realism before run
      setFailures([
        {
          test: "should return 404 for missing user",
          error: "TypeError: Cannot read properties of undefined (reading 'name') at userController.ts:21",
          file: "src/controllers/userController.ts"
        },
        {
          test: "should apply 20% VIP tier discount for orders of $100 and above",
          error: "Expected: 20, Received: 10 at discountService.ts:18",
          file: "src/services/discountService.ts"
        },
        {
          test: "should calculate free shipping for orders with total >= 50 or coupon FREE_SHIP",
          error: "Expected: 0, Received: 10 at orderService.ts:28",
          file: "src/services/orderService.ts"
        }
      ]);
      setTestsBefore({ total: 21, passed: 18, failed: 3 });
      setEvents([]);
      setIterationRecords([]);
      setReport(null);
      setStatus("READY");
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend API: " + err);
    }
  };

  // Start Autonomous Debugging
  const startDebugging = async () => {
    if (!project) return;
    try {
      setIsRunning(true);
      setStatus("INITIALIZING");
      setEvents([]);
      setIterationRecords([]);
      setReport(null);
      setTestsAfter(undefined);
      setValidationDecision(undefined);

      const res = await fetch(`${API_BASE}/debug/${project.id}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, max_iterations: 5 })
      });
      if (!res.ok) throw new Error("Failed to start session");
      const newSession: DebugSession = await res.json();
      setSession(newSession);

      // Connect WebSocket for real-time streaming
      connectWebSocket(newSession.id);
      startPolling(newSession.id);
    } catch (err) {
      setIsRunning(false);
      console.error(err);
      alert("Failed to start debugging: " + err);
    }
  };

  // WebSocket connection handler
  const connectWebSocket = (sessionId: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    const ws = new WebSocket(`${WS_BASE}/debug/${sessionId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const raw = JSON.parse(event.data);
        handleAgentEvent(raw);
      } catch (err) {
        console.error("WS Parse error", err);
      }
    };

    ws.onerror = (err) => console.warn("WebSocket error, falling back to polling", err);
  };

  // Process incoming event from WebSocket or Polling
  const handleAgentEvent = useCallback((ev: AgentEvent) => {
    setEvents((prev) => {
      if (prev.some((p) => p.id === ev.id)) return prev;
      return [...prev, ev];
    });

    if (ev.agent) setCurrentAgent(ev.agent);
    if (ev.iteration) setIteration(ev.iteration);

    // Event type handlers
    if (ev.event === "ERROR_DETECTED" && ev.payload) {
      if (ev.payload.failures) setFailures(ev.payload.failures);
      if (ev.payload.stack_trace) setStackTrace(ev.payload.stack_trace);
    }

    if (ev.event === "HYPOTHESIS_CREATED" && ev.payload) {
      setHypotheses((prev) => [...prev, ev.payload]);
    }

    if (ev.event === "ROOT_CAUSE_IDENTIFIED" && ev.payload) {
      setRootCause(ev.payload.root_cause);
      setConfidence(ev.payload.confidence || 0.94);
      setEvidence(ev.payload.evidence || []);
      setRepairStrategy(ev.payload.strategy);
    }

    if (ev.event === "PATCH_GENERATED" && ev.payload) {
      setDiffData((prev) => ({
        ...prev,
        patch_id: ev.payload.patch_id,
        modified_files: ev.payload.modified_files || [],
        summary: ev.payload.summary,
        diff: prev?.diff || ""
      }));
    }

    if (ev.event === "PATCH_APPLIED" && ev.payload) {
      fetchDiff(ev.session_id);
    }

    if (ev.event === "APPROVAL_REQUESTED") {
      setIsApprovalOpen(true);
      setStatus("WAITING_FOR_APPROVAL");
    }

    if (ev.event === "ITERATION_COMPLETED" && ev.payload) {
      const rec = {
        iteration: ev.payload.iteration,
        decision: ev.payload.decision,
        passed: ev.payload.passed,
        failed: ev.payload.failed
      };
      setIterationRecords((prev) => [...prev, rec]);
      setValidationDecision(ev.payload.decision);
      setTestsAfter({
        total: (ev.payload.passed || 0) + (ev.payload.failed || 0),
        passed: ev.payload.passed || 0,
        failed: ev.payload.failed || 0
      });
    }

    if (ev.event === "DEBUGGING_COMPLETED" || ev.event === "HUMAN_INTERVENTION_REQUIRED") {
      setIsRunning(false);
      setStatus(ev.event === "DEBUGGING_COMPLETED" ? "FIXED" : "HUMAN_INTERVENTION_REQUIRED");
      fetchReport(ev.session_id);
    }
  }, []);

  const fetchDiff = async (sessionId: string) => {
    try {
      const res = await fetch(`${API_BASE}/debug/${sessionId}/diff`);
      if (res.ok) {
        const d = await res.json();
        setDiffData(d);
      }
    } catch {}
  };

  const fetchReport = async (sessionId: string) => {
    try {
      const res = await fetch(`${API_BASE}/debug/${sessionId}/report`);
      if (res.ok) {
        const r = await res.json();
        setReport(r);
        setIsReportOpen(true);
      }
    } catch {}
  };

  // Polling fallback to keep status synced
  const startPolling = (sessionId: string) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    pollIntervalRef.current = setInterval(async () => {
      try {
        const statusRes = await fetch(`${API_BASE}/debug/${sessionId}/status`);
        if (statusRes.ok) {
          const s: DebugSession = await statusRes.json();
          setSession(s);
          setStatus(s.status);
          setCurrentAgent(s.current_agent);
          setIteration(s.iteration);
          if (s.active_checkpoint) setCheckpoint(s.active_checkpoint);

          if (s.status === "FIXED" || s.status === "HUMAN_INTERVENTION_REQUIRED" || s.status === "FAILED") {
            setIsRunning(false);
            clearInterval(pollIntervalRef.current);
            fetchReport(sessionId);
          }
        }

        const eventsRes = await fetch(`${API_BASE}/debug/${sessionId}/events`);
        if (eventsRes.ok) {
          const evs: AgentEvent[] = await eventsRes.json();
          evs.forEach((e) => handleAgentEvent(e));
        }
      } catch {}
    }, 1500);
  };

  const submitHumanDecision = async (action: "APPROVE" | "REJECT" | "CANCEL") => {
    if (!session) return;
    try {
      await fetch(`${API_BASE}/debug/${session.id}/decide`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action })
      });
      setIsApprovalOpen(false);
      if (action === "CANCEL") {
        setIsRunning(false);
        setStatus("CANCELLED");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const resetAll = () => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    if (wsRef.current) wsRef.current.close();
    setSession(null);
    setEvents([]);
    setIterationRecords([]);
    setReport(null);
    setIsRunning(false);
    setStatus("READY");
  };

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return {
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
    resetAll
  };
}
