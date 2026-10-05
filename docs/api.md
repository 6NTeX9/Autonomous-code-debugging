# REST & WebSocket API Documentation

The backend exposes a high-performance REST and WebSocket API built with **FastAPI**.

Base URL: `http://localhost:8000/api`  
WebSocket URL: `ws://localhost:8000/ws`

---

## Project Endpoints

### 1. Upload Repository Archive
- **Method:** `POST /api/projects/upload`
- **Content-Type:** `multipart/form-data`
- **Fields:**
  - `name`: string (e.g. `"my-repo"`)
  - `file`: binary ZIP file
  - `description`: optional string
- **Response:** `ProjectResponse`

### 2. Load Built-in Demo Project
- **Method:** `POST /api/projects/sample`
- **Description:** Instantiates a fresh isolated copy of `sample-buggy-project` (TypeScript / Express / Jest, 21 tests: 18 passed, 3 failed).
- **Response:** `ProjectResponse`

### 3. Get Project
- **Method:** `GET /api/projects/{project_id}`
- **Response:** `ProjectResponse`

---

## Debugging Endpoints

### 4. Start Autonomous Debugging Session
- **Method:** `POST /api/debug/{project_id}/start`
- **Body:**
  ```json
  {
    "mode": "AUTO",          // or "APPROVAL_REQUIRED"
    "max_iterations": 5
  }
  ```
- **Response:** `SessionResponse`

### 5. Get Session Status
- **Method:** `GET /api/debug/{session_id}/status`
- **Response:** `SessionResponse`

### 6. Get Event Stream
- **Method:** `GET /api/debug/{session_id}/events`
- **Response:** `List[AgentEventResponse]`

### 7. Get Latest Git Diff
- **Method:** `GET /api/debug/{session_id}/diff`
- **Response:**
  ```json
  {
    "patch_id": "patch_user_controller_null_check_01",
    "modified_files": ["src/controllers/userController.ts"],
    "summary": "Added defensive missing-user check",
    "diff": "--- a/src/controllers/userController.ts\n..."
  }
  ```

### 8. Get Autonomous Debugging Report
- **Method:** `GET /api/debug/{session_id}/report`
- **Response:** `DebugReportResponse`

### 9. Cancel Debugging Session
- **Method:** `POST /api/debug/{session_id}/cancel`

### 10. Manual Rollback
- **Method:** `POST /api/debug/{session_id}/rollback`

### 11. Submit Human Decision (Approval Mode)
- **Method:** `POST /api/debug/{session_id}/decide`
- **Body:**
  ```json
  {
    "action": "APPROVE",     // "APPROVE", "REJECT", or "CANCEL"
    "feedback": "Optional notes"
  }
  ```

---

## WebSocket Real-Time Endpoint

### 12. Live Event Stream
- **Endpoint:** `ws://localhost:8000/ws/debug/{session_id}`
- **Description:** Streams instant `AgentEvent` payloads as agents execute tools and transition states in real-time.
