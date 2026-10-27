import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("docs/images", exist_ok=True)
plt.style.use('dark_background')

# -------------------------------------------------------------
# FIGURE 1: 4-Agent Pipeline Architecture
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.set_facecolor('#0b0f19')
fig.patch.set_facecolor('#0b0f19')

# Orchestrator Bar at top
orch_box = patches.FancyBboxPatch((1.0, 5.2), 10.0, 0.9, boxstyle="round,pad=0.15",
                                 facecolor="#1e1b4b", edgecolor="#6366f1", linewidth=2)
ax.add_patch(orch_box)
ax.text(6.0, 5.65, "CENTRAL ORCHESTRATOR (State Machine, Retry Loop, Safety Limits, Max 5 Iterations)",
        color="#c7d2fe", fontsize=11, fontweight='bold', ha='center', va='center')

# Agent Boxes
agents = [
    {
        "name": "AGENT 1: SCOUT",
        "role": "Repository & Error Analysis",
        "owner": "Member 1",
        "color": "#0284c7",
        "border": "#38bdf8",
        "x": 0.5,
        "tools": "• list_files()\n• detect_project_type()\n• run_tests()\n• inspect_error_log()",
        "output": "Output: Structured JSON\n(failures, stack trace,\naffected files, symbols)"
    },
    {
        "name": "AGENT 2: DETECTIVE",
        "role": "Root Cause Reasoning",
        "owner": "Member 2",
        "color": "#7c3aed",
        "border": "#a855f7",
        "x": 3.5,
        "tools": "• read_file()\n• search_code()\n• Hypotheses ranking\n• Evidence synthesis",
        "output": "Output: Diagnostic Report\n(root cause, confidence,\nevidence, repair strategy)"
    },
    {
        "name": "AGENT 3: REPAIRER",
        "role": "Code Patch & Git Repair",
        "owner": "Member 3",
        "color": "#d97706",
        "border": "#fbbf24",
        "x": 6.5,
        "tools": "• create_git_checkpoint()\n• apply_patch()\n• get_git_diff()\n• rollback_changes()",
        "output": "Output: Patch Package\n(patch_id, unified diff,\ncheckpoint commit hash)"
    },
    {
        "name": "AGENT 4: GUARDIAN",
        "role": "Testing & Validation",
        "owner": "Member 4",
        "color": "#059669",
        "border": "#34d399",
        "x": 9.5,
        "tools": "• run_command()\n• run_tests()\n• get_test_results()\n• rollback_changes()",
        "output": "Output: Validation Verdict\n(VERIFIED or REJECTED,\nregressions, final report)"
    }
]

for a in agents:
    # Outer box
    box = patches.FancyBboxPatch((a["x"], 1.3), 2.3, 3.4, boxstyle="round,pad=0.1",
                                facecolor="#0f172a", edgecolor=a["border"], linewidth=2)
    ax.add_patch(box)
    
    # Header box
    h_box = patches.FancyBboxPatch((a["x"] + 0.05, 4.0), 2.2, 0.6, boxstyle="round,pad=0.05",
                                  facecolor=a["color"], edgecolor="none")
    ax.add_patch(h_box)
    ax.text(a["x"] + 1.15, 4.35, a["name"], color="white", fontsize=9.5, fontweight='bold', ha='center', va='center')
    ax.text(a["x"] + 1.15, 4.12, f"({a['owner']})", color="#e2e8f0", fontsize=8, ha='center', va='center')
    
    ax.text(a["x"] + 1.15, 3.75, a["role"], color="#94a3b8", fontsize=8.5, fontweight='semibold', ha='center')
    
    # Tools text
    ax.text(a["x"] + 0.15, 2.9, a["tools"], color="#cbd5e1", fontsize=7.5, va='top', family='monospace')
    
    # Divider line
    ax.plot([a["x"] + 0.1, a["x"] + 2.2], [2.15, 2.15], color="#334155", linewidth=1)
    
    # Output text
    ax.text(a["x"] + 0.15, 2.0, a["output"], color=a["border"], fontsize=7.2, va='top')

# Forward Arrows between Agents
for i in range(3):
    x_start = agents[i]["x"] + 2.3
    x_end = agents[i+1]["x"]
    ax.annotate("", xy=(x_end, 3.0), xytext=(x_start, 3.0),
                arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=2.5, mutation_scale=15))

# Feedback loop arrow (Guardian FAIL -> Detective)
ax.annotate("", xy=(4.65, 1.25), xytext=(10.65, 1.25),
            arrowprops=dict(arrowstyle="->", color="#f43f5e", lw=2, linestyle="--",
                            connectionstyle="arc3,rad=0.25", mutation_scale=15))
ax.text(7.65, 0.45, "REINVESTIGATE LOOP (Tests Fail / Regression Detected) — max 5 retries",
        color="#fb7185", fontsize=8.5, fontweight='bold', ha='center', va='center')

# Pass arrow (Guardian PASS -> Final Report)
ax.annotate("", xy=(11.0, 0.8), xytext=(11.0, 1.3),
            arrowprops=dict(arrowstyle="->", color="#34d399", lw=2.5, mutation_scale=15))
ax.text(11.0, 0.5, "VERIFIED (All Pass)\nGenerate Final Report", color="#34d399",
        fontsize=8.5, fontweight='bold', ha='center', va='center')

# Orchestrator connections
for a in agents:
    ax.annotate("", xy=(a["x"] + 1.15, 4.7), xytext=(a["x"] + 1.15, 5.2),
                arrowprops=dict(arrowstyle="<->", color="#818cf8", lw=1.2, linestyle=":"))

ax.set_xlim(-0.1, 12.2)
ax.set_ylim(0.1, 6.3)
ax.axis('off')
plt.title("Autonomous Code Debugging Agent: Four-Agent Pipeline & Control Architecture",
          color="white", fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig("docs/images/architecture_pipeline.png", bbox_inches='tight', facecolor='#0b0f19')
plt.close()
print("Saved docs/images/architecture_pipeline.png")

# -------------------------------------------------------------
# FIGURE 2: UI Dashboard Mockup Visual
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7.0), dpi=300)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')

# Browser Header Bar
header_bg = patches.Rectangle((0, 6.4), 12, 0.8, facecolor='#1e293b', edgecolor='#334155')
ax.add_patch(header_bg)
# Mac buttons
for i, c in enumerate(['#ef4444', '#f59e0b', '#10b981']):
    circle = plt.Circle((0.4 + i*0.25, 6.8), 0.08, color=c)
    ax.add_patch(circle)
ax.text(6.0, 6.8, "Autonomous Code Debugging Agent Dashboard — http://localhost:3001",
        color="#cbd5e1", fontsize=9, ha='center', va='center', family='monospace')

# Pipeline Status Banner
pipe_bg = patches.Rectangle((0.4, 5.4), 11.2, 0.8, facecolor='#0b0f19', edgecolor='#38bdf8', linewidth=1.5)
ax.add_patch(pipe_bg)
stage_names = ["[1] SCOUT (Complete)", "[2] DETECTIVE (Root Cause Found)", "[3] REPAIRER (Patch Applied)", "[4] GUARDIAN (21/21 Verified)"]
for i, name in enumerate(stage_names):
    pill = patches.FancyBboxPatch((0.6 + i*2.75, 5.55), 2.5, 0.5, boxstyle="round,pad=0.08",
                                 facecolor='#065f46' if i==3 else '#0369a1', edgecolor='#34d399' if i==3 else '#38bdf8')
    ax.add_patch(pill)
    ax.text(1.85 + i*2.75, 5.8, name, color="white", fontsize=7.5, fontweight='bold', ha='center', va='center')

# Left Column 1: Agent Activity Log
card1 = patches.FancyBboxPatch((0.4, 2.7), 5.4, 2.5, boxstyle="round,pad=0.08", facecolor='#1e293b', edgecolor='#334155')
ax.add_patch(card1)
ax.text(0.6, 5.0, "AGENT ACTIVITY STREAM (Live WebSocket)", color="#38bdf8", fontsize=9, fontweight='bold')
logs = [
    "[SCOUT] Discovered TypeScript/Jest project (21 tests)",
    "[SCOUT] Ran test suite: 18 passed, 3 failed. Captured stack trace.",
    "[DETECTIVE] Formulated 3 ranked root-cause hypotheses (Confidence: 94%)",
    "[REPAIRER] Created safe Git checkpoint: 3f8a91b",
    "[REPAIRER] Applied surgical patch to userController.ts & orderService.ts",
    "[GUARDIAN] Re-tested: 21 passed, 0 failed, 0 regressions -> VERIFIED!"
]
for j, log in enumerate(logs):
    ax.text(0.6, 4.65 - j*0.35, log, color="#94a3b8" if j<4 else "#4ade80", fontsize=7.2, family='monospace')

# Left Column 2: Test Failures Panel
card2 = patches.FancyBboxPatch((0.4, 0.3), 5.4, 2.2, boxstyle="round,pad=0.08", facecolor='#1e293b', edgecolor='#ef4444')
ax.add_patch(card2)
ax.text(0.6, 2.25, "TEST FAILURES & REGRESSION MONITOR (3 Initial Bugs)", color="#f87171", fontsize=9, fontweight='bold')
fails = [
    "FAIL tests/user.test.ts: TypeError: Cannot read property of undefined",
    "FAIL tests/discount.test.ts: Expected: 20, Received: 10 (Inverted logic)",
    "FAIL tests/order.test.ts: Expected: 0, Received: 10 (Shipping fee defect)",
    "--> GUARDIAN OUTCOME: ALL 3 DEFECTS AUTONOMOUSLY RESOLVED"
]
for j, f in enumerate(fails):
    ax.text(0.6, 1.9 - j*0.38, f, color="#fca5a5" if j<3 else "#34d399", fontsize=7.2, family='monospace',
            fontweight='bold' if j==3 else 'normal')

# Right Column 1: Reasoning & Hypotheses
card3 = patches.FancyBboxPatch((6.2, 2.7), 5.4, 2.5, boxstyle="round,pad=0.08", facecolor='#1e293b', edgecolor='#a855f7')
ax.add_patch(card3)
ax.text(6.4, 5.0, "ROOT CAUSE REASONING & RANKED HYPOTHESES", color="#c084fc", fontsize=9, fontweight='bold')
hyp = [
    "H1: Missing null check when user ID not found in DB [Conf: 94% - TOP]",
    "H2: VIP discount threshold comparison inverted '<' vs '>=' [Conf: 91%]",
    "H3: Free shipping condition checks total instead of discount [Conf: 88%]",
    "Repair Strategy: Smallest safe patch; preserve existing public APIs"
]
for j, h in enumerate(hyp):
    ax.text(6.4, 4.65 - j*0.36, h, color="#e9d5ff", fontsize=7.2, family='monospace')

# Right Column 2: Interactive Patch Diff Viewer
card4 = patches.FancyBboxPatch((6.2, 0.3), 5.4, 2.2, boxstyle="round,pad=0.08", facecolor='#0b0f19', edgecolor='#10b981')
ax.add_patch(card4)
ax.text(6.4, 2.25, "INTERACTIVE UNIFIED DIFF VIEWER (userController.ts)", color="#34d399", fontsize=9, fontweight='bold')
diff_lines = [
    "--- a/src/controllers/userController.ts",
    "+++ b/src/controllers/userController.ts",
    "- const user = userRepository.findById(id);",
    "- return res.json({ name: user.name });",
    "+ const user = userRepository.findById(id);",
    "+ if (!user) return res.status(404).json({ error: 'User not found' });",
    "+ return res.json({ name: user.name });"
]
for j, d in enumerate(diff_lines):
    color = "#f87171" if d.startswith("-") else ("#4ade80" if d.startswith("+") else "#64748b")
    ax.text(6.4, 1.95 - j*0.25, d, color=color, fontsize=7.0, family='monospace')

ax.set_xlim(0, 12)
ax.set_ylim(0, 7.2)
ax.axis('off')
plt.title("Next.js Developer Dashboard: Live Real-Time Multi-Agent Observability",
          color="white", fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig("docs/images/dashboard_ui_mockup.png", bbox_inches='tight', facecolor='#0f172a')
plt.close()
print("Saved docs/images/dashboard_ui_mockup.png")

# -------------------------------------------------------------
# FIGURE 3: Orchestrator State Machine Flowchart
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')

states = [
    ("INITIALIZING", 1.0, 4.5, "#475569"),
    ("ANALYZING_REPO", 3.2, 4.5, "#0284c7"),
    ("RUNNING_TESTS", 5.4, 4.5, "#0284c7"),
    ("INVESTIGATING", 7.6, 4.5, "#7c3aed"),
    ("GENERATING_PATCH", 9.8, 4.5, "#d97706"),
    ("APPLYING_PATCH", 9.8, 2.5, "#d97706"),
    ("VALIDATING_PATCH", 7.6, 2.5, "#059669"),
    ("FIXED (PASS)", 5.0, 1.0, "#10b981"),
    ("RETRYING", 7.6, 0.9, "#f59e0b"),
    ("HUMAN_INTERV.", 10.0, 1.0, "#ef4444")
]

for name, x, y, col in states:
    box = patches.FancyBboxPatch((x-0.9, y-0.35), 1.8, 0.7, boxstyle="round,pad=0.08",
                                facecolor=col, edgecolor="white", linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, y, name, color="white", fontsize=7.5, fontweight='bold', ha='center', va='center')

# Arrows
arrows = [
    ((1.9, 4.5), (2.3, 4.5)),
    ((4.1, 4.5), (4.5, 4.5)),
    ((6.3, 4.5), (6.7, 4.5)),
    ((8.5, 4.5), (8.9, 4.5)),
    ((9.8, 4.15), (9.8, 2.85)),
    ((8.9, 2.5), (8.5, 2.5)),
]
for start, end in arrows:
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=2, mutation_scale=12))

# Guardian decision branches
# 1. Pass -> FIXED
ax.annotate("", xy=(5.0, 1.35), xytext=(7.0, 2.2),
            arrowprops=dict(arrowstyle="->", color="#34d399", lw=2.5, mutation_scale=12))
ax.text(5.7, 1.9, "0 Failed\nVERIFIED", color="#34d399", fontsize=8, fontweight='bold')

# 2. Fail & iter < 5 -> RETRYING -> INVESTIGATING
ax.annotate("", xy=(7.6, 1.25), xytext=(7.6, 2.15),
            arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=2, mutation_scale=12))
ax.text(7.8, 1.7, "Failures > 0\niter < 5", color="#f59e0b", fontsize=7.5)

ax.annotate("", xy=(7.0, 4.2), xytext=(7.0, 1.2),
            arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=1.8, linestyle="--",
                            connectionstyle="arc3,rad=-0.2", mutation_scale=12))

# 3. Fail & iter >= 5 -> HUMAN_INTERVENTION_REQUIRED
ax.annotate("", xy=(10.0, 1.35), xytext=(8.4, 2.2),
            arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5, mutation_scale=12))
ax.text(9.5, 1.9, "Failures > 0\niter >= 5", color="#ef4444", fontsize=7.5, fontweight='bold')

ax.set_xlim(0, 11.2)
ax.set_ylim(0.2, 5.5)
ax.axis('off')
plt.title("Central Orchestrator State Transition & Autonomous Self-Healing Flow",
          color="white", fontsize=12, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig("docs/images/state_machine.png", bbox_inches='tight', facecolor='#0f172a')
plt.close()
print("Saved docs/images/state_machine.png")

# -------------------------------------------------------------
# FIGURE 4: Test Verification & Before/After Metrics
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
ax1.set_facecolor('#0f172a')
ax2.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')

# Subplot 1: Bar Chart of Passing vs Failing across Iterations
phases = ['Initial Run\n(Scout)', 'Iteration 1\n(Partial Fix)', 'Final Verified\n(Guardian)']
passed = [18, 20, 21]
failed = [3, 1, 0]

x = np.arange(len(phases))
width = 0.35

rects1 = ax1.bar(x - width/2, passed, width, label='Passing Tests', color='#10b981', edgecolor='white', lw=1)
rects2 = ax1.bar(x + width/2, failed, width, label='Failing Tests', color='#ef4444', edgecolor='white', lw=1)

ax1.set_ylabel('Number of Tests', color='#cbd5e1', fontsize=9)
ax1.set_title('Test Suite Evolution (21 Total Jest Tests)', color='white', fontsize=10, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(phases, color='#cbd5e1', fontsize=8.5)
ax1.legend(facecolor='#1e293b', edgecolor='#475569', labelcolor='white')
ax1.set_ylim(0, 25)
ax1.grid(axis='y', color='#334155', linestyle=':', alpha=0.7)
ax1.tick_params(colors='#94a3b8')

for r in rects1:
    h = r.get_height()
    ax1.annotate(f'{h}', xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 3),
                textcoords="offset points", ha='center', va='bottom', color='#34d399', fontweight='bold', fontsize=8.5)
for r in rects2:
    h = r.get_height()
    ax1.annotate(f'{h}', xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 3),
                textcoords="offset points", ha='center', va='bottom', color='#f87171', fontweight='bold', fontsize=8.5)

# Subplot 2: Automated Pytest Test Coverage of Architecture
suites = ['Pipeline E2E', 'Git & Code Tools', 'Docker Sandbox', '4 Agent Units', 'FastAPI REST/WS']
test_counts = [1, 5, 2, 3, 2]
colors = ['#6366f1', '#0ea5e9', '#14b8a6', '#f59e0b', '#ec4899']

ax2.barh(suites, test_counts, color=colors, edgecolor='white', lw=1)
ax2.set_xlabel('Automated Test Cases Passed', color='#cbd5e1', fontsize=9)
ax2.set_title('Backend Test Suite Coverage (13/13 Passed)', color='white', fontsize=10, fontweight='bold')
ax2.grid(axis='x', color='#334155', linestyle=':', alpha=0.7)
ax2.tick_params(colors='#94a3b8')

for i, v in enumerate(test_counts):
    ax2.text(v + 0.1, i, f'{v} passed (100%)', color='white', va='center', fontsize=8, fontweight='bold')
ax2.set_xlim(0, 6.5)

plt.tight_layout()
plt.savefig("docs/images/test_verification_chart.png", bbox_inches='tight', facecolor='#0f172a')
plt.close()
print("Saved docs/images/test_verification_chart.png")
