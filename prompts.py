prompt_1 = """You are a research assistant analyzing a query before beginning research.

Analyze this query and extract:
1. The main topic
2. Specific aspects the user wants covered
3. Any constraints (time period, depth, source types)
4. Whether clarification is needed (only if genuinely ambiguous)

If clarification is needed, ask up to 3 focused questions.
If not needed, state your assumptions clearly.

Query: {user_query}

Respond with ONLY valid JSON:
{{
    "topic": "main subject",
    "aspects": ["specific areas to cover"],
    "constraints": ["any limitations"],
    "needs_clarification": true/false,
    "clarifying_questions": ["if needed"],
    "assumptions": ["assumptions you're making"]
}}
"""

prompt_1_1 = """You are a research assistant finalizing your understanding of a query.

Original query: {user_query}

Your initial understanding:
{{
    "topic": {topic},
    "aspects": {aspects},
    "constraints": {constraints},
    "assumptions": {assumptions}
}}

Your clarifying questions: {clarifying_questions}

User's answers: {user_answers}

Update your understanding based on their responses. Keep what was correct, modify what needs changing, add any new information.

Respond with ONLY valid JSON:
{{
    "topic": "main subject (updated if needed)",
    "aspects": ["updated areas to cover"],
    "constraints": ["updated limitations"],
    "assumptions": ["final assumptions incorporating user's answers"]
}}
"""

prompt_2 = """You are a research assistant creating a research plan.

Query understanding:
- Topic: {topic}
- Aspects to cover: {aspects}
- Constraints: {constraints}
- Assumptions: {assumptions}

Create 3-6 distinct research angles that collectively cover the query. Each angle should be:
- Specific enough to guide a focused search
- Non-overlapping with other angles
- Answerable through research (not opinion)

Respond with ONLY valid JSON:
{{
    "research_angles": [
        {{
            "angle": "<specific question or area to investigate>",
            "why_needed": "<how this contributes to answering the overall query>",
            "success_criteria": "<what specific information or evidence would complete this angle>"
        }}
    ]
}}
"""

prompt_3 = """You are a research assistant investigating one angle of a research query.

User Query: {user_query}
Angle: {angle}
Success Criteria: {success_criteria}

Use the available tools to gather information. When success criteria is met, stop using tools and provide your final summary.

Available tools:

- arxiv_search: Search academic papers on arXiv
- fetch_url: Fetch content from URLs

If you have gathered enough information, respond with ONLY valid JSON:
{{
    "final_summary": "<summarize all relevant information for this angle>",
    "sources_used": ["<only URLs referenced in the summary>"]
}}

Otherwise, continue using tools to gather more information.
"""

prompt_4 = """You are a research assistant reflecting on the research quality.

Original Query: {user_query}

Research Plan (Angles Investigated):
{angles_investigated}

Synthesized Information:
{synthesized_info}

Evaluate whether the gathered information adequately answers the user's query.

Respond with ONLY valid JSON:
{{
    "is_sufficient": <true or false>,
    "reasoning": "<why the information is sufficient or what's missing>",
    "new_angles": [
        {{
            "angle": "<area to investigate>",
            "why_needed": "<what gap this fills>",
            "success_criteria": "<what would complete this angle>"
        }}
    ]
}}

If is_sufficient is true, new_angles should be an empty array.
"""

prompt_5 = """You are a research assistant creating a final report.

User Query: {user_query}

Synthesized Information:
{synthesized_info}

Sources Used:
{sources}

Create a well-structured final report in markdown format with the following structure:

# [Relevant Title Based on Query]

## Executive Summary
Brief 2-3 sentence overview answering the core query.

## Key Findings
Main findings organized by theme. Cite sources using [1], [2], etc.

## Detailed Analysis
Deeper analysis connecting the findings with evidence from sources.

## Conclusion
Direct, concise answer to the user's query with key takeaways.

## References
Numbered list of all sources cited:
[1] Source title - URL
[2] Source title - URL

Important:
- Use proper markdown formatting (headers, bullet points, bold for emphasis)
- Cite sources inline using [1], [2] format
- Ensure all claims are supported by the synthesized information
- Keep the report focused and relevant to the user's query
"""