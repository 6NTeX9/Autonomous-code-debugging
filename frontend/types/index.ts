export interface Project {
  id: string;
  name: string;
  description?: string;
  language?: string;
  framework?: string;
  test_framework?: string;
  workspace_path: string;
  created_at: string;
  updated_at: string;
}

export type AgentName = "SCOUT" | "DETECTIVE" | "REPAIRER" | "GUARDIAN" | "ORCHESTRATOR";

export interface AgentEvent {
  id: string;
  session_id: string;
  agent: AgentName;
  event: string;
  iteration: number;
  tool?: string;
  payload?: any;
  message?: string;
  timestamp: string;
}

export interface DebugSession {
  id: string;
  project_id: string;
  status: string;
  current_agent: AgentName;
  mode: "AUTO" | "APPROVAL_REQUIRED";
  iteration: number;
  max_iterations: number;
  current_error?: string;
  stack_trace?: string;
  active_checkpoint?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface TestFailure {
  test: string;
  error: string;
  file?: string;
  line?: number;
}

export interface TestRunLog {
  iteration: number;
  phase: string;
  passed: number;
  failed: number;
  stdout?: string;
  stderr?: string;
}

export interface DiffData {
  patch_id?: string;
  modified_files: string[];
  summary?: string;
  diff: string;
}

export interface DebugReport {
  id: string;
  session_id: string;
  project_name: string;
  language?: string;
  framework?: string;
  status: "SUCCESS" | "FAILED" | "HUMAN_INTERVENTION_REQUIRED";
  original_error?: string;
  root_cause?: string;
  evidence: string[];
  affected_files: string[];
  files_modified: string[];
  patch_summary?: string;
  tests_before: { total: number; passed: number; failed: number };
  tests_after: { total: number; passed: number; failed: number };
  iterations: number;
  regressions: number;
  validation_result: string;
  confidence: string;
  remaining_issues: string[];
  created_at: string;
}
