from prompts import prompt_1, prompt_1_1, prompt_2, prompt_3, prompt_4, prompt_5
from utils import generate_response, extract_content, prepare_message, convert_response_to_json, generate_response_with_fn_calls
from config import get_config, ConfigurationError
from events import WorkflowEventHandler, PhaseStatus
from typing import Optional

def phase_1_fn(query, event_handler: Optional[WorkflowEventHandler] = None):
    if event_handler:
        event_handler.emit_phase("1", "Understanding Query", PhaseStatus.RUNNING)

    prompt = prompt_1.format(user_query=query)
    response = generate_response(messages=prepare_message(
        user_message=prompt),
        thinking_level="medium"
        )

    content = extract_content(response)
    response_json = convert_response_to_json(content)

    if event_handler:
        event_handler.emit_phase(
            "1", "Understanding Query", PhaseStatus.COMPLETED,
            message=f"Clarification needed: {response_json.get('needs_clarification', False)}"
        )

    return response_json

def phase_1_1_fn(query, response_phase_1, user_answer: Optional[str] = None, event_handler: Optional[WorkflowEventHandler] = None):
    if event_handler:
        event_handler.emit_phase("1.1", "Clarification", PhaseStatus.RUNNING)

    # Get user answer via callback or parameter
    if user_answer is None:
        questions = response_phase_1["clarifying_questions"]
        if event_handler:
            user_answer = event_handler.request_clarification(str(questions))
        else:
            # Fallback to input for CLI mode
            user_answer = input(f"Before we start deep research, could you answer to these questions ?: \n{questions}\nYour answers: ")
    prompt = prompt_1_1.format(
    user_query = query,
    topic = response_phase_1["topic"],
    aspects = response_phase_1["aspects"],
    clarifying_questions = response_phase_1["clarifying_questions"],
    constraints = response_phase_1["constraints"],
    assumptions = response_phase_1["assumptions"],
    user_answers = user_answer
    )
    response = generate_response(messages=prepare_message(user_message=prompt),thinking_level="medium")
    content = extract_content(response)
    response_json = convert_response_to_json(content)

    if event_handler:
        event_handler.emit_phase("1.1", "Clarification", PhaseStatus.COMPLETED)

    return response_json

def phase_2_fn(query, response_phase_1, event_handler: Optional[WorkflowEventHandler] = None):
    if event_handler:
        event_handler.emit_phase("2", "Research Planning", PhaseStatus.RUNNING)

    prompt = prompt_2.format(
    topic = response_phase_1["topic"],
    aspects = response_phase_1["aspects"],
    constraints = response_phase_1["constraints"],
    assumptions = response_phase_1["assumptions"],
    )

    response = generate_response(messages=prepare_message(user_message=prompt),thinking_level="medium")
    content = extract_content(response)
    response_json = convert_response_to_json(content)

    if event_handler:
        angle_count = len(response_json.get("research_angles", []))
        event_handler.emit_phase(
            "2", "Research Planning", PhaseStatus.COMPLETED,
            message=f"Created {angle_count} research angles"
        )

    return response_json

def phase_3_fn(query, response_phase_2, event_handler: Optional[WorkflowEventHandler] = None):
    if event_handler:
        event_handler.emit_phase("3", "Research Execution", PhaseStatus.RUNNING)

    if "research_angles" in response_phase_2:
        angles = response_phase_2["research_angles"]
    else:
        angles = response_phase_2["new_angles"]

    synthesis_info = ""
    sources_used = []
    angles_investigated = []

    for idx, d in enumerate(angles, 1):
        if event_handler:
            event_handler.emit_phase(
                "3", "Research Execution", PhaseStatus.RUNNING,
                message=f"Investigating angle {idx}/{len(angles)}: {d['angle']}"
            )

        angles_investigated.append(d["angle"])
        prompt = prompt_3.format(
            user_query=query,
            angle=d["angle"],
            success_criteria=d["success_criteria"],
            )

        content = generate_response_with_fn_calls(
            [prepare_message(user_message = prompt)],
            event_handler=event_handler
        )
        response_json = convert_response_to_json(content)
        synthesis_info = synthesis_info + "\n\n" + response_json["final_summary"]
        sources_used.extend(response_json["sources_used"])

    if event_handler:
        event_handler.emit_phase(
            "3", "Research Execution", PhaseStatus.COMPLETED,
            message=f"Investigated {len(angles_investigated)} angles, found {len(sources_used)} sources"
        )

    return synthesis_info, sources_used, angles_investigated

def phase_4_fn(query, angles_investigated, synthesis_info, event_handler: Optional[WorkflowEventHandler] = None):
    if event_handler:
        event_handler.emit_phase("4", "Reflection", PhaseStatus.RUNNING)

    prompt = prompt_4.format(
    user_query=query,
    angles_investigated=angles_investigated,
    synthesized_info=synthesis_info,
    )

    response = generate_response(
        messages=prepare_message(user_message = prompt ),
        thinking_level="medium",
        )

    content = extract_content(response)
    response_json = convert_response_to_json(content)

    if event_handler:
        is_sufficient = response_json.get("is_sufficient", False)
        status_msg = "Research sufficient" if is_sufficient else "Additional research needed"
        event_handler.emit_phase("4", "Reflection", PhaseStatus.COMPLETED, message=status_msg)

    return response_json

def phase_5_fn(query,synthesis_info,sources_used, event_handler: Optional[WorkflowEventHandler] = None):
    if event_handler:
        event_handler.emit_phase("5", "Final Report", PhaseStatus.RUNNING)

    prompt = prompt_5.format(
        user_query=query,
        synthesized_info=synthesis_info,
        sources = sources_used
        )

    response = generate_response(
        messages=prepare_message(user_message = prompt ),
        thinking_level="medium",
        )

    content = extract_content(response)

    if event_handler:
        event_handler.emit_phase("5", "Final Report", PhaseStatus.COMPLETED)

    return content

def run_worklow(query: str, user_clarification: Optional[str] = None, event_handler: Optional[WorkflowEventHandler] = None) -> str:
    """
    Run the complete research workflow.

    Args:
        query: User's research query
        user_clarification: Optional pre-provided clarification answers
        event_handler: Optional event handler for progress tracking

    Returns:
        Final markdown report
    """
    # Phase 1: Understanding user query
    response_json = phase_1_fn(query=query, event_handler=event_handler)

    # Phase 1.1: Human-in-the-loop clarification
    if response_json["needs_clarification"]:
        response_json = phase_1_1_fn(
            query=query,
            response_phase_1=response_json,
            user_answer=user_clarification,
            event_handler=event_handler
        )

    # Phase 2: Planning
    response_json = phase_2_fn(query=query, response_phase_1=response_json, event_handler=event_handler)

    # Phase 3: Execution and Tool Use
    final_synthesis_info = ""
    synthesis_info, sources_used, angles_investigated = phase_3_fn(
        query, response_json, event_handler=event_handler
    )
    final_synthesis_info = synthesis_info

    # Phase 4: Reflection
    response_json = phase_4_fn(query, angles_investigated, synthesis_info, event_handler=event_handler)

    if not response_json["is_sufficient"]:
        # Go back to phase 3 with new angles
        synthesis_info, sources_used, angles_investigated = phase_3_fn(
            query, response_json, event_handler=event_handler
        )
        final_synthesis_info = final_synthesis_info + "\n\n" + synthesis_info

    # Phase 5: Synthesizer
    content = phase_5_fn(query, final_synthesis_info, sources_used, event_handler=event_handler)

    return content

def main():
    """CLI entry point."""
    try:
        config = get_config()
    except ConfigurationError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease create a .env file with required API keys.")
        print("See .env.example for template.")
        return

    print("Research Agent - CLI Mode")
    query = input("Enter your research query: ")

    # Use default event handler (console output)
    event_handler = WorkflowEventHandler()

    final_report = run_worklow(query, event_handler=event_handler)

    # Save report
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = config.REPORTS_DIR / f"report_{timestamp}.md"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_report)

    print(f"\nReport saved to: {filename}")

if __name__ == "__main__":
    main()