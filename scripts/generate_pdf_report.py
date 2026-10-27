import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------
# Numbered Canvas for Running Headers and "Page X of Y" Footers
# ----------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip header/footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header
        self.drawString(54, 750, "AUTONOMOUS CODE DEBUGGING AGENT — ILP CCA 2 PROJECT REPORT")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)

        # Running Footer
        self.line(54, 45, 558, 45)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 32, "Confidential — Academic & Technical Evaluation Document")
        self.drawRightString(558, 32, page_text)
        self.restoreState()


def build_pdf(filename="Autonomous_Code_Debugging_Agent_Documentation.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0f172a")     # Slate 900
    SECONDARY = colors.HexColor("#1e293b")   # Slate 800
    ACCENT_BLUE = colors.HexColor("#0284c7") # Sky 600
    ACCENT_PURPLE = colors.HexColor("#7c3aed")
    SUCCESS = colors.HexColor("#059669")
    WARNING = colors.HexColor("#d97706")
    DANGER = colors.HexColor("#dc2626")
    TEXT_DARK = colors.HexColor("#1e293b")
    TEXT_MUTED = colors.HexColor("#64748b")
    BG_LIGHT = colors.HexColor("#f8fafc")
    BORDER_LIGHT = colors.HexColor("#e2e8f0")

    # Typography Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        alignment=0,
        spaceAfter=8
    )

    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=ACCENT_BLUE,
        alignment=0,
        spaceAfter=15
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=ACCENT_BLUE,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.2,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    style_body_bold = ParagraphStyle(
        'BodyBold_Custom',
        parent=style_body,
        fontName='Helvetica-Bold'
    )

    style_caption = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=1,
        spaceAfter=8
    )

    style_code = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=PRIMARY,
        spaceAfter=4
    )

    style_callout = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.5,
        textColor=PRIMARY
    )

    elements = []

    # ------------------------------------------------------------------
    # COVER / HEADER BANNER
    # ------------------------------------------------------------------
    badge_table = Table(
        [[
            Paragraph("<b>AGENTIC AI MINI PROJECT</b>", ParagraphStyle('B1', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#4338ca'))),
            Paragraph("<b>ILP CCA 2</b>", ParagraphStyle('B2', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#047857'))),
            Paragraph("<b>STATUS: PRODUCTION VERIFIED</b>", ParagraphStyle('B3', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#b45309')))
        ]],
        colWidths=[130, 80, 160]
    )
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#e0e7ff')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#d1fae5')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#fef3c7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(badge_table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("AUTONOMOUS CODE DEBUGGING AGENT", style_cover_title))
    elements.append(Paragraph("Closed-Loop Self-Healing Software Repair System with Four Specialized AI Agents", style_cover_subtitle))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_BLUE, spaceAfter=10))

    # Meta Info Card
    meta_data = [
        [
            Paragraph("<b>Project Architecture:</b>", style_body_bold),
            Paragraph("Four-Agent Specialized Pipeline + Central Orchestrator", style_body),
            Paragraph("<b>Primary Language Support:</b>", style_body_bold),
            Paragraph("TypeScript, JavaScript, Python (Java-Ready)", style_body)
        ],
        [
            Paragraph("<b>Team Structure:</b>", style_body_bold),
            Paragraph("4 Students (Scout • Detective • Repairer • Guardian)", style_body),
            Paragraph("<b>Evaluation Benchmark:</b>", style_body_bold),
            Paragraph("21-Test E-Commerce Suite (3 Real Bugs) + 13 Pytests", style_body)
        ],
        [
            Paragraph("<b>Key Technology Stack:</b>", style_body_bold),
            Paragraph("FastAPI, Next.js 14, Docker Sandbox, SQLite, Git, WS", style_body),
            Paragraph("<b>Max Autonomous Iterations:</b>", style_body_bold),
            Paragraph("5 Iterations before Human-in-the-Loop Fallback", style_body)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[110, 155, 110, 129])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # ------------------------------------------------------------------
    # 1. EXECUTIVE SUMMARY & OBJECTIVE
    # ------------------------------------------------------------------
    elements.append(Paragraph("1. Executive Summary & Project Objective", style_h1))
    elements.append(Paragraph(
        "Modern automated programming assistants frequently operate as passive conversational chatbots that only explain error traces or propose speculative text snippets. The <b>Autonomous Code Debugging Agent</b> is an enterprise-grade agentic AI system designed for the <b>ILP CCA 2 Mini Project</b>. Rather than generating unverified advice, the system actively inspects repositories, runs tests in isolated execution sandboxes, analyzes stack traces, formulates and ranks root-cause hypotheses, creates surgical unified Git diff patches, applies changes, and autonomously validates outcomes across iterative feedback cycles.",
        style_body
    ))
    elements.append(Paragraph(
        "The project demonstrates complete agentic autonomy across all 17 required core capabilities: repository ingestion (ZIP/sample), technology detection, test discovery, error localization, structured reasoning, Git checkpointing, regression detection, automated rollback, and final report compilation.",
        style_body
    ))
    elements.append(Spacer(1, 6))

    # ------------------------------------------------------------------
    # 2. FOUR-AGENT ARCHITECTURE & TEAM ALLOCATION
    # ------------------------------------------------------------------
    elements.append(Paragraph("2. Four-Agent Architecture & Team Ownership", style_h1))
    elements.append(Paragraph(
        "The architecture is strictly partitioned into four primary specialized agents, mapping directly to a group of four students. No agent performs another agent's duties, and communication occurs solely via validated Pydantic JSON contracts:",
        style_body
    ))

    # Agent Table
    agent_rows = [
        [
            Paragraph("<b>Agent Name & Role</b>", style_body_bold),
            Paragraph("<b>Team Owner</b>", style_body_bold),
            Paragraph("<b>Core Responsibilities</b>", style_body_bold),
            Paragraph("<b>Assigned Production Tools</b>", style_body_bold)
        ],
        [
            Paragraph("<b>AGENT 1: SCOUT</b><br/><i>Repository & Error Analysis</i>", style_body),
            Paragraph("Member 1", style_body_bold),
            Paragraph("Analyzes repository structure, detects language/framework, discovers test harness, executes initial test suites, captures stdout/stderr, and maps failing symbols.", style_body),
            Paragraph("<font name='Courier' size='7.5'>list_files, read_file, search_code, get_file_metadata, detect_project_type, analyze_dependencies, run_tests, inspect_error_log</font>", style_body)
        ],
        [
            Paragraph("<b>AGENT 2: DETECTIVE</b><br/><i>Root Cause & Reasoning</i>", style_body),
            Paragraph("Member 2", style_body_bold),
            Paragraph("Inspects source call-trees, compares expected vs actual behavior, formulates multiple ranked hypotheses with confidence scores, gathers evidence, and writes repair instructions.", style_body),
            Paragraph("<font name='Courier' size='7.5'>read_file, search_code, get_file_metadata, inspect_error_log</font><br/><i>(Heuristic & LLM reasoning engine)</i>", style_body)
        ],
        [
            Paragraph("<b>AGENT 3: REPAIRER</b><br/><i>Fix Generation & Code Patch</i>", style_body),
            Paragraph("Member 3", style_body_bold),
            Paragraph("Drafts minimal surgical patches preserving public APIs, creates Git checkpoints, applies unified diffs, verifies syntax, and issues rollback commands if required.", style_body),
            Paragraph("<font name='Courier' size='7.5'>read_file, search_code, create_git_checkpoint, apply_patch, get_git_diff, rollback_changes</font>", style_body)
        ],
        [
            Paragraph("<b>AGENT 4: GUARDIAN</b><br/><i>Validation & Testing</i>", style_body),
            Paragraph("Member 4", style_body_bold),
            Paragraph("Executes targeted and complete test suites, detects regressions, evaluates before/after metrics, issues VERIFIED or REJECTED verdicts, and triggers rollback upon failure.", style_body),
            Paragraph("<font name='Courier' size='7.5'>run_command, run_tests, get_test_results, get_git_diff, rollback_changes</font>", style_body)
        ]
    ]
    agent_table = Table(agent_rows, colWidths=[105, 55, 175, 169])
    agent_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(agent_table)
    elements.append(Spacer(1, 10))

    # Architecture Image Figure
    if os.path.exists("docs/images/architecture_pipeline.png"):
        elements.append(Image("docs/images/architecture_pipeline.png", width=500, height=270))
        elements.append(Paragraph("<b>Figure 1:</b> Four-Agent Autonomous Closed-Loop Debugging Pipeline and Feedback Controls.", style_caption))
    elements.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 3. CENTRAL ORCHESTRATOR & FINITE STATE MACHINE
    # ------------------------------------------------------------------
    elements.append(Paragraph("3. Central Orchestrator & State Flow", style_h1))
    elements.append(Paragraph(
        "The <b>Central Orchestrator</b> is deliberately designed not as an unpredictable 5th LLM agent, but as a deterministic Finite State Machine (FSM). It maintains centralized session state in SQLite, routes typed data contracts between agents, enforces safety bounds, coordinates retries, and invokes human intervention when necessary.",
        style_body
    ))

    # FSM Image Figure
    if os.path.exists("docs/images/state_machine.png"):
        elements.append(Image("docs/images/state_machine.png", width=490, height=255))
        elements.append(Paragraph("<b>Figure 2:</b> Orchestrator State Transitions, Retry Conditions, and Human Fallback Flow.", style_caption))

    elements.append(Paragraph(
        "<b>Workflow Rules & Safety Constraints:</b><br/>"
        "• <b>Max Iterations:</b> Capped at <font name='Courier'>MAX_ITERATIONS = 5</font>. If defects persist beyond 5 cycles, state shifts to <font name='Courier'>HUMAN_INTERVENTION_REQUIRED</font>.<br/>"
        "• <b>Dual Operating Modes:</b> In <font name='Courier'>AUTO</font> mode, the system heals autonomously end-to-end. In <font name='Courier'>APPROVAL_REQUIRED</font> mode, the orchestrator pauses before patch application, surfacing diffs and reasoning for human sign-off.<br/>"
        "• <b>Cheating Prevention:</b> The Repairer agent is strictly forbidden from deleting tests, modifying assertions, commenting out assertions, or altering test inputs.",
        style_body
    ))
    elements.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 4. KEY TECHNOLOGY STACKS & ARCHITECTURAL COMPONENTS
    # ------------------------------------------------------------------
    elements.append(Paragraph("4. Key Technology Stacks & Components", style_h1))
    
    tech_data = [
        [
            Paragraph("<b>Subsystem</b>", style_body_bold),
            Paragraph("<b>Technologies Used</b>", style_body_bold),
            Paragraph("<b>Architecture & Implementation Highlights</b>", style_body_bold)
        ],
        [
            Paragraph("<b>Frontend Dashboard</b>", style_body),
            Paragraph("Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons", style_body),
            Paragraph("Real-time reactive developer dashboard featuring agent pipeline visualization, live WebSocket stream, interactive syntax-highlighted diff viewer, and report modal.", style_body)
        ],
        [
            Paragraph("<b>Backend API & Engine</b>", style_body),
            Paragraph("Python 3.13, FastAPI, Uvicorn, Pydantic v2, SQLite, SQLAlchemy", style_body),
            Paragraph("High-performance asynchronous REST API with WebSocket broadcast manager, structured validation contracts, and relational persistence of sessions, patches, and logs.", style_body)
        ],
        [
            Paragraph("<b>Execution Sandbox</b>", style_body),
            Paragraph("Docker Sandbox + Secure Process Sandbox Factory", style_body),
            Paragraph("Multi-tier isolation with CPU/memory quotas, command execution timeouts, path traversal guards (anti-ZipSlip), and decompression limits (anti-ZipBomb).", style_body)
        ],
        [
            Paragraph("<b>Version Control & Storage</b>", style_body),
            Paragraph("Git CLI, SQLite, Per-Session Isolated Workspaces", style_body),
            Paragraph("Automated Git branch creation, atomic checkpoint commits before any patch, unified diff extraction, and hard rollback on failed validation.", style_body)
        ],
        [
            Paragraph("<b>Reasoning & LLM Provider</b>", style_body),
            Paragraph("Pluggable Provider: Mock Engine + OpenAI/Gemini Ready", style_body),
            Paragraph("Deterministic zero-cost mock reasoning engine reproducing authentic multi-hypothesis diagnostics alongside live external LLM API bridge.", style_body)
        ]
    ]
    tech_table = Table(tech_data, colWidths=[100, 130, 274])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(tech_table)
    elements.append(Spacer(1, 10))

    # Dashboard Screenshot Mockup Figure
    if os.path.exists("docs/images/dashboard_ui_mockup.png"):
        elements.append(Image("docs/images/dashboard_ui_mockup.png", width=500, height=280))
        elements.append(Paragraph("<b>Figure 3:</b> Full-Stack Developer Dashboard Mockup displaying Pipeline, WebSocket Stream, Reasoning, and Interactive Diff.", style_caption))
    elements.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 5. AGENT TOOLS CATALOG (14 PRODUCTION TOOLS)
    # ------------------------------------------------------------------
    elements.append(Paragraph("5. Agent Tools Catalog (14 Tools Implemented)", style_h1))
    elements.append(Paragraph(
        "Each tool is implemented as an explicit Python function with JSON serialization, execution event emission, and error handling:",
        style_body
    ))

    tools_list = [
        [
            Paragraph("<b>Tool Function</b>", style_body_bold),
            Paragraph("<b>Target Agent(s)</b>", style_body_bold),
            Paragraph("<b>Input Parameters</b>", style_body_bold),
            Paragraph("<b>Operation Description & Output</b>", style_body_bold)
        ],
        [
            Paragraph("<font name='Courier'>list_files</font>", style_body),
            Paragraph("Scout", style_body),
            Paragraph("subpath, max_depth", style_body),
            Paragraph("Recursively traverses directory tree, respecting ignore lists.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>read_file</font>", style_body),
            Paragraph("Scout, Detective, Repairer", style_body),
            Paragraph("file_path, start_line, end_line", style_body),
            Paragraph("Safely reads content within workspace with line range limits.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>search_code</font>", style_body),
            Paragraph("All Agents", style_body),
            Paragraph("query, file_pattern", style_body),
            Paragraph("Fast regex/string search across source files with line numbers.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>get_file_metadata</font>", style_body),
            Paragraph("Scout, Detective", style_body),
            Paragraph("file_path", style_body),
            Paragraph("Extracts size, line count, permissions, and modification time.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>detect_project_type</font>", style_body),
            Paragraph("Scout", style_body),
            Paragraph("workspace_path", style_body),
            Paragraph("Identifies TypeScript, JavaScript, Python, Java, and frameworks.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>analyze_dependencies</font>", style_body),
            Paragraph("Scout", style_body),
            Paragraph("workspace_path", style_body),
            Paragraph("Parses package.json or requirements.txt for dependencies.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>run_command</font>", style_body),
            Paragraph("Scout, Guardian", style_body),
            Paragraph("command, timeout_sec", style_body),
            Paragraph("Executes shell command inside sandbox with resource caps.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>run_tests</font>", style_body),
            Paragraph("Scout, Guardian", style_body),
            Paragraph("test_filter", style_body),
            Paragraph("Executes Jest, Pytest, or JUnit; captures exit code & stdout.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>get_test_results</font>", style_body),
            Paragraph("Scout, Guardian", style_body),
            Paragraph("test_output_text", style_body),
            Paragraph("Parses test output into structured passed/failed counts & errors.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>inspect_error_log</font>", style_body),
            Paragraph("Scout, Detective", style_body),
            Paragraph("log_text", style_body),
            Paragraph("Extracts failing assertions, file paths, line numbers, and traces.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>create_git_checkpoint</font>", style_body),
            Paragraph("Repairer", style_body),
            Paragraph("message", style_body),
            Paragraph("Stages and commits all files to create an atomic rollback hash.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>apply_patch</font>", style_body),
            Paragraph("Repairer", style_body),
            Paragraph("patch_diff_or_files", style_body),
            Paragraph("Surgically updates target files and validates syntax.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>get_git_diff</font>", style_body),
            Paragraph("Repairer, Guardian", style_body),
            Paragraph("checkpoint_hash", style_body),
            Paragraph("Generates unified git diff showing exact before/after changes.", style_body)
        ],
        [
            Paragraph("<font name='Courier'>rollback_changes</font>", style_body),
            Paragraph("Repairer, Guardian", style_body),
            Paragraph("checkpoint_hash", style_body),
            Paragraph("Performs <font name='Courier'>git reset --hard</font> to discard failed patch safely.", style_body)
        ]
    ]
    tools_table = Table(tools_list, colWidths=[105, 95, 110, 194])
    tools_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(tools_table)
    elements.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 6. DEMO PROJECT, TEST CASES, & EVALUATION
    # ------------------------------------------------------------------
    elements.append(Paragraph("6. Demo Project & Comprehensive Test Cases", style_h1))
    elements.append(Paragraph(
        "To rigorously validate the agent system without superficial mocks, a full realistic TypeScript/Express e-commerce service was engineered with 21 unit and integration tests across three intentional, realistic bugs:",
        style_body
    ))

    # Bug Breakdown Table
    bugs_data = [
        [
            Paragraph("<b>Defect Location</b>", style_body_bold),
            Paragraph("<b>Bug Description & Symptoms</b>", style_body_bold),
            Paragraph("<b>Agent 2 Root Cause Diagnosis</b>", style_body_bold),
            Paragraph("<b>Agent 3 Surgical Patch</b>", style_body_bold)
        ],
        [
            Paragraph("<b>userController.ts</b><br/>(Line 21)", style_body),
            Paragraph("Missing entity check when querying user ID. Calling <font name='Courier'>user.name</font> causes 500 <font name='Courier'>TypeError: Cannot read properties of undefined</font>.", style_body),
            Paragraph("Controller assumes database query always returns an object. Does not handle missing record.", style_body),
            Paragraph("Add conditional guard:<br/><font name='Courier' size='7.5'>if (!user) return res.status(404).json({ error: 'User not found' });</font>", style_body)
        ],
        [
            Paragraph("<b>discountService.ts</b><br/>(Line 18)", style_body),
            Paragraph("VIP discount tier condition inverted (<font name='Courier'>orderTotal &lt; 100</font> instead of <font name='Courier'>&gt;= 100</font>). Test fails expecting 20%, receiving 10%.", style_body),
            Paragraph("Comparison operator inverted during discount threshold qualification.", style_body),
            Paragraph("Invert relational operator:<br/><font name='Courier' size='7.5'>if (orderTotal &gt;= 100 &amp;&amp; isVip) discount = 0.20;</font>", style_body)
        ],
        [
            Paragraph("<b>orderService.ts</b><br/>(Line 28)", style_body),
            Paragraph("Free shipping coupon code <font name='Courier'>FREE_SHIP</font> logic flaw. Test expects $0 shipping fee, receives $10.", style_body),
            Paragraph("Condition checked gross subtotal without factoring coupon entitlement.", style_body),
            Paragraph("Include coupon code predicate in shipping qualification boolean expression.", style_body)
        ]
    ]
    bugs_table = Table(bugs_data, colWidths=[95, 135, 135, 139])
    bugs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(bugs_table)
    elements.append(Spacer(1, 10))

    # Test Metrics Image Figure
    if os.path.exists("docs/images/test_verification_chart.png"):
        elements.append(Image("docs/images/test_verification_chart.png", width=500, height=210))
        elements.append(Paragraph("<b>Figure 4:</b> Left: E-commerce Test Suite Evolution (18/21 -> 21/21 Pass). Right: Automated Pytest Coverage (13/13 Passed).", style_caption))
    elements.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 7. COMPLETE DIRECTORY STRUCTURE
    # ------------------------------------------------------------------
    elements.append(Paragraph("7. Complete Repository Directory Structure", style_h1))
    
    dir_text = """
<b>autonomous-code-debugger/</b>
├── <b>backend/</b>                       # FastAPI Backend Engine (Python 3.13)
│   ├── <b>app/</b>
│   │   ├── <b>agents/</b>                # Four Primary AI Agents
│   │   │   ├── <b>scout/</b>             # Agent 1: Repository inspection & test discovery
│   │   │   ├── <b>detective/</b>         # Agent 2: Root-cause reasoning & hypotheses
│   │   │   ├── <b>repairer/</b>          # Agent 3: Patch generation & Git rollback
│   │   │   └── <b>guardian/</b>          # Agent 4: Test validation & regression check
│   │   ├── <b>api/</b>                   # REST Endpoints (/projects, /debug) & WebSockets
│   │   ├── <b>core/</b>                  # Database configuration, settings, LLM provider
│   │   ├── <b>models/</b>                # SQLAlchemy models (Project, Session, Patch, Report)
│   │   ├── <b>orchestrator/</b>          # FSM Pipeline controller, retries, approval locks
│   │   ├── <b>sandbox/</b>               # Docker sandbox & process isolation factory
│   │   ├── <b>services/</b>              # Project service (ZIP extract & sample provisioning)
│   │   └── <b>tools/</b>                 # 14 Production Agent Tools (Git, Files, Test runner)
│   ├── <b>tests/</b>                     # 13 Automated Pytest suites (Unit, E2E, Sandbox)
│   └── <b>requirements.txt</b>           # Backend dependencies
├── <b>frontend/</b>                      # Next.js 14 Developer Dashboard (TypeScript)
│   ├── <b>app/</b>                       # App router (page.tsx, layout.tsx, globals.css)
│   ├── <b>components/</b>                # Pipeline, Activity stream, Diff viewer, Validation
│   ├── <b>hooks/</b>                     # useDebugSession (WebSocket & REST state manager)
│   └── <b>package.json</b>               # Frontend dependencies & Tailwind configuration
├── <b>sample-project/</b>                # Realistic E-Commerce Microservice (TypeScript/Jest)
│   ├── <b>src/</b>                       # Controllers, Repositories, and Business Services
│   ├── <b>tests/</b>                     # 21 Jest test cases (User, Order, Discount)
│   └── <b>package.json</b>               # Node/Jest configuration
├── <b>docs/</b>                          # System documentation & architectural specifications
├── <b>scripts/</b>                       # Automation scripts (run_demo.sh, generate_diagrams.py)
└── <b>docker-compose.yml</b>             # Full-stack production container orchestration
"""
    elements.append(Paragraph(dir_text, style_code))
    elements.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 8. HOW-TO-RUN GUIDE (START TO END)
    # ------------------------------------------------------------------
    elements.append(Paragraph("8. Step-by-Step How-To-Run Guide (Start to End)", style_h1))
    
    steps = [
        ("Step 1: Prerequisites & Environment",
         "Ensure <b>Node.js (v18+)</b>, <b>Python (v3.10+)</b>, and <b>Git</b> are installed on the host machine. Docker is optional for containerized sandbox mode."),
        ("Step 2: Start Backend Server",
         "Navigate to <font name='Courier'>backend/</font>, activate virtual environment, install dependencies, and launch:<br/>"
         "<font name='Courier'>cd backend &amp;&amp; source venv/bin/activate &amp;&amp; uvicorn app.main:app --host 0.0.0.0 --port 8001</font><br/>"
         "The FastAPI Swagger API docs will be live at <font name='Courier'>http://localhost:8001/docs</font>."),
        ("Step 3: Start Frontend Dashboard",
         "In a separate terminal, navigate to <font name='Courier'>frontend/</font> and launch the Next.js server:<br/>"
         "<font name='Courier'>cd frontend &amp;&amp; npm install &amp;&amp; npm run dev -- -p 3001</font><br/>"
         "Open browser at <font name='Courier'>http://localhost:3001</font> to interact with the dashboard."),
        ("Step 4: Execute Automated Pytest Suite",
         "Run all 13 backend unit, integration, and E2E test suites:<br/>"
         "<font name='Courier'>cd backend &amp;&amp; pytest tests/ -v</font><br/>"
         "All tests will execute in isolated temporary sandboxes and report 100% passing."),
        ("Step 5: Load Project & Run Debugging Pipeline",
         "1. Click <b>'Load Demo'</b> in the dashboard navbar (or click <b>'Upload (.zip)'</b> for custom repos).<br/>"
         "2. Choose operating mode: <b>Autonomous (AUTO)</b> or <b>Approval Required</b>.<br/>"
         "3. Click <b>'Start Autonomous Debugging'</b>.<br/>"
         "4. Observe live Scout discovery, Detective hypothesis ranking, Repairer Git patching, and Guardian test verification.<br/>"
         "5. Inspect the before/after unified diff and click <b>'View Final Report'</b> to download/review diagnostic results.")
    ]

    for title, desc in steps:
        elements.append(Paragraph(f"<b>{title}</b>", style_h2))
        elements.append(Paragraph(desc, style_body))
    elements.append(Spacer(1, 10))

    # ------------------------------------------------------------------
    # 9. SECURITY & DEFENSIVE ENGINEERING GUARANTEES
    # ------------------------------------------------------------------
    elements.append(Paragraph("9. Security & Defensive Engineering Guarantees", style_h1))
    elements.append(Paragraph(
        "• <b>Anti-ZipSlip Protection:</b> File extraction verifies canonical destination path resolution, rejecting archive entries attempting directory traversal (e.g., <font name='Courier'>../../etc/passwd</font>).<br/>"
        "• <b>Anti-ZipBomb Safeguard:</b> Enforces a hard 50MB uncompressed byte limit during project upload.<br/>"
        "• <b>Subprocess Sandbox Quotas:</b> Command executions are capped by strict timeouts (default: 60s) and non-root execution context.<br/>"
        "• <b>Atomic Git Checkpoint Invariant:</b> No file edit is ever performed without creating a baseline Git commit first, guaranteeing zero data loss via deterministic <font name='Courier'>git reset --hard</font> rollbacks.",
        style_body
    ))

    # Build Document with NumberedCanvas
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    build_pdf()
