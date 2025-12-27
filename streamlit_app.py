"""Streamlit frontend for Research Agent."""
import streamlit as st
from datetime import datetime
from pathlib import Path

from main import run_worklow
from config import get_config, ConfigurationError
from events import WorkflowEventHandler, PhaseEvent, ToolCallEvent, PhaseStatus

# Page configuration
st.set_page_config(
    page_title="Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .phase-container {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .phase-pending {
        background-color: #f0f2f6;
        border-color: #9e9e9e;
    }
    .phase-running {
        background-color: #e3f2fd;
        border-color: #2196f3;
    }
    .phase-completed {
        background-color: #e8f5e9;
        border-color: #4caf50;
    }
    .phase-failed {
        background-color: #ffebee;
        border-color: #f44336;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        'workflow_running': False,
        'workflow_complete': False,
        'query': '',
        'phases': {
            "1": {"name": "Understanding Query", "status": PhaseStatus.PENDING, "message": ""},
            "1.1": {"name": "Clarification", "status": PhaseStatus.PENDING, "message": ""},
            "2": {"name": "Research Planning", "status": PhaseStatus.PENDING, "message": ""},
            "3": {"name": "Research Execution", "status": PhaseStatus.PENDING, "message": ""},
            "4": {"name": "Reflection", "status": PhaseStatus.PENDING, "message": ""},
            "5": {"name": "Final Report", "status": PhaseStatus.PENDING, "message": ""},
        },
        'tool_calls': [],
        'final_report': None,
        'clarification_needed': False,
        'clarification_questions': "",
        'user_clarification': None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_phases_vertical(phase_placeholder):
    """Render phases as simple expandable list."""
    with phase_placeholder.container():
        for phase_num, phase_data in st.session_state.phases.items():
            status = phase_data["status"]
            name = phase_data["name"]
            message = phase_data["message"]

            # Skip pending phases and Phase 1.1 (integrate clarification into Phase 1)
            if status == PhaseStatus.PENDING or phase_num == "1.1":
                continue

            # Icon based on status
            if status == PhaseStatus.RUNNING:
                icon = "🔄"
            elif status == PhaseStatus.COMPLETED:
                icon = "✅"
            elif status == PhaseStatus.FAILED:
                icon = "❌"
            else:
                icon = "⏳"

            # All phases use expander - running phases are expanded, completed are collapsed
            is_expanded = (status == PhaseStatus.RUNNING)

            with st.expander(f"{icon} **Phase {phase_num}: {name}**", expanded=is_expanded):
                # Show progress message inside expander
                if message:
                    st.info(message)

                # Show tool calls if Phase 3
                if phase_num == "3" and st.session_state.tool_calls:
                    st.markdown("**🔧 Tool Calls:**")
                    for idx, call in enumerate(st.session_state.tool_calls, 1):
                        with st.expander(f"Tool #{idx}: {call['tool_name']}", expanded=(idx == len(st.session_state.tool_calls) and status == PhaseStatus.RUNNING)):
                            st.code(f"Arguments: {call['arguments']}", language="python")
                            st.text(call['result_preview'][:200] + "..." if len(call['result_preview']) > 200 else call['result_preview'])
                            st.caption(call['timestamp'])


class StreamlitEventHandler(WorkflowEventHandler):
    """Event handler that updates Streamlit session state."""

    def __init__(self, phase_placeholder):
        self.phase_placeholder = phase_placeholder
        super().__init__(
            on_phase_update=self.handle_phase_update,
            on_tool_call=self.handle_tool_call,
            on_clarification_needed=self.handle_clarification
        )

    def handle_phase_update(self, event: PhaseEvent):
        """Update phase status and re-render all phases."""
        st.session_state.phases[event.phase_number] = {
            "name": event.phase_name,
            "status": event.status,
            "message": event.message or ""
        }
        # Re-render all phases vertically
        render_phases_vertical(self.phase_placeholder)

    def handle_tool_call(self, event: ToolCallEvent):
        """Add tool call and re-render phases (tools shown in Phase 3)."""
        st.session_state.tool_calls.append({
            "tool_name": event.tool_name,
            "arguments": event.arguments,
            "result_preview": event.result_preview,
            "timestamp": event.timestamp
        })
        # Re-render to show new tool under Phase 3
        render_phases_vertical(self.phase_placeholder)

    def handle_clarification(self, questions: str) -> str:
        """Handle clarification request."""
        st.session_state.clarification_needed = True
        st.session_state.clarification_questions = questions

        # Return existing answer if available
        if st.session_state.user_clarification:
            return st.session_state.user_clarification

        # Signal that we need clarification
        raise Exception("CLARIFICATION_NEEDED")


def main():
    """Main Streamlit app."""
    initialize_session_state()

    # Sidebar
    with st.sidebar:
        st.title("🔬 Research Agent")
        st.markdown("---")

        # Configuration status
        st.subheader("Configuration")
        try:
            config = get_config()
            st.success("✅ API keys configured")
            st.info(f"Model: {config.GEMINI_MODEL}")
            st.info(f"Max iterations: {config.MAX_TOOL_ITERATIONS}")
        except ConfigurationError as e:
            st.error("❌ Configuration error")
            st.error(str(e))
            st.info("""Create a .env file with:
```
GEMINI_API_KEY=your_key
TAVILY_API_KEY=your_key
```""")
            st.stop()

        st.markdown("---")

        # Reset button
        if st.button("Reset", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.subheader("About")
        st.markdown("""
        This research agent performs multi-phase research:
        1. **Understanding** - Analyzes your query
        2. **Clarification** - Asks questions if needed
        3. **Planning** - Creates research angles
        4. **Execution** - Investigates using tools
        5. **Reflection** - Validates completeness
        6. **Synthesis** - Generates final report
        """)

    # Main content
    st.title("🔬 AI Research Agent")
    st.markdown("Enter your research query below. The agent will analyze, plan, and execute comprehensive research.")

    # Query input
    if not st.session_state.workflow_running and not st.session_state.workflow_complete:
        query = st.text_area(
            "Research Query",
            placeholder="e.g., What are the latest developments in quantum computing for drug discovery?",
            height=100,
            key="query_input"
        )

        # Start research button
        col1, col2 = st.columns([1, 4])
        with col1:
            start_button = st.button(
                "Start Research",
                type="primary",
                disabled=(not query),
                use_container_width=True
            )

        if start_button:
            st.session_state.query = query
            st.session_state.workflow_running = True
            st.session_state.workflow_complete = False
            st.session_state.tool_calls = []
            st.session_state.final_report = None
            st.session_state.clarification_needed = False
            st.session_state.user_clarification = None

            # Reset phases
            for phase_num in st.session_state.phases:
                st.session_state.phases[phase_num]["status"] = PhaseStatus.PENDING
                st.session_state.phases[phase_num]["message"] = ""

            st.rerun()

    else:
        st.info(f"**Query:** {st.session_state.query}")

    # Clarification handling
    if st.session_state.clarification_needed and not st.session_state.user_clarification:
        st.markdown("---")
        st.warning("🤔 Clarification Needed")

        # Format questions nicely
        questions = st.session_state.clarification_questions
        if isinstance(questions, str):
            # Try to parse if it's a string representation of a list
            import ast
            try:
                questions_list = ast.literal_eval(questions)
                if isinstance(questions_list, list):
                    for idx, q in enumerate(questions_list, 1):
                        st.markdown(f"**{idx}.** {q}")
                else:
                    st.markdown(questions)
            except:
                st.markdown(questions)
        elif isinstance(questions, list):
            for idx, q in enumerate(questions, 1):
                st.markdown(f"**{idx}.** {q}")
        else:
            st.markdown(str(questions))

        user_answer = st.text_area(
            "Your answers",
            placeholder="Please answer the questions above...",
            height=150,
            key="clarification_input"
        )

        if st.button("Submit Clarification", type="primary"):
            st.session_state.user_clarification = user_answer
            st.session_state.clarification_needed = False
            st.session_state.workflow_running = True
            st.rerun()

    # Progress section - vertical layout
    if st.session_state.workflow_running or st.session_state.workflow_complete:
        st.markdown("---")
        phase_placeholder = st.empty()
        render_phases_vertical(phase_placeholder)

    # Execute workflow
    if st.session_state.workflow_running and not st.session_state.clarification_needed:
        try:
            # Create event handler
            event_handler = StreamlitEventHandler(phase_placeholder)

            # Run workflow
            final_report = run_worklow(
                query=st.session_state.query,
                user_clarification=st.session_state.user_clarification,
                event_handler=event_handler
            )

            st.session_state.final_report = final_report
            st.session_state.workflow_complete = True
            st.session_state.workflow_running = False
            st.rerun()

        except Exception as e:
            if "CLARIFICATION_NEEDED" in str(e):
                # Normal flow - wait for clarification
                st.session_state.workflow_running = False
                st.rerun()
            else:
                st.error(f"Error during research: {str(e)}")
                st.session_state.workflow_running = False
                st.session_state.workflow_complete = False

    # Display final report
    if st.session_state.workflow_complete and st.session_state.final_report:
        st.markdown("---")
        st.subheader("📄 Final Report")

        # Download button
        col1, col2 = st.columns([1, 4])
        with col1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="Download Report",
                data=st.session_state.final_report,
                file_name=f"research_report_{timestamp}.md",
                mime="text/markdown",
                use_container_width=True
            )

        # Display report
        st.markdown(st.session_state.final_report)


if __name__ == "__main__":
    main()
