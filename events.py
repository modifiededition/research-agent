"""Event system for workflow progress tracking."""
from dataclasses import dataclass
from typing import Any, Callable, Optional
from enum import Enum


class PhaseStatus(Enum):
    """Phase execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseEvent:
    """Event emitted during phase execution."""
    phase_number: str  # "1", "1.1", "2", "3", "4", "5"
    phase_name: str
    status: PhaseStatus
    data: Optional[dict] = None
    message: Optional[str] = None


@dataclass
class ToolCallEvent:
    """Event emitted during tool calls in Phase 3."""
    tool_name: str
    arguments: dict
    result_preview: str  # First 100 chars of result
    timestamp: str


class WorkflowEventHandler:
    """Handler for workflow events with callback support."""

    def __init__(
        self,
        on_phase_update: Optional[Callable[[PhaseEvent], None]] = None,
        on_tool_call: Optional[Callable[[ToolCallEvent], None]] = None,
        on_clarification_needed: Optional[Callable[[str], str]] = None,
    ):
        self.on_phase_update = on_phase_update or self._default_phase_handler
        self.on_tool_call = on_tool_call or self._default_tool_handler
        self.on_clarification_needed = on_clarification_needed or self._default_clarification_handler

    def _default_phase_handler(self, event: PhaseEvent):
        """Default handler prints to console."""
        status_symbol = {
            PhaseStatus.PENDING: "⏳",
            PhaseStatus.RUNNING: "🔄",
            PhaseStatus.COMPLETED: "✅",
            PhaseStatus.FAILED: "❌",
        }
        symbol = status_symbol.get(event.status, "")
        print(f"{symbol} Phase {event.phase_number}: {event.phase_name} - {event.status.value}")
        if event.message:
            print(f"  {event.message}")

    def _default_tool_handler(self, event: ToolCallEvent):
        """Default handler prints to console."""
        print(f"🔧 Tool Call: {event.tool_name}({event.arguments})")
        print(f"   Result: {event.result_preview}...")

    def _default_clarification_handler(self, questions: str) -> str:
        """Default handler uses console input."""
        print(f"\nClarification needed:")
        print(questions)
        return input("Your answers: ")

    def emit_phase(self, phase_number: str, phase_name: str, status: PhaseStatus,
                   data: Optional[dict] = None, message: Optional[str] = None):
        """Emit phase event."""
        event = PhaseEvent(phase_number, phase_name, status, data, message)
        self.on_phase_update(event)

    def emit_tool_call(self, tool_name: str, arguments: dict, result: str):
        """Emit tool call event."""
        from datetime import datetime
        event = ToolCallEvent(
            tool_name=tool_name,
            arguments=arguments,
            result_preview=result[:100] if result else "",
            timestamp=datetime.now().isoformat()
        )
        self.on_tool_call(event)

    def request_clarification(self, questions: str) -> str:
        """Request clarification from user."""
        return self.on_clarification_needed(questions)
