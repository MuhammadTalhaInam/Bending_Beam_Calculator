# workflow.py
"""AI orchestration layer: Planning -> Content -> Assessment -> Review -> Refinement."""

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from openai import OpenAI

from prompts import (
    PLANNING_PROMPT, CONTENT_PROMPT, ASSESSMENT_PROMPT,
    REVIEW_PROMPT, REFINEMENT_PROMPT,
    PLAN_SCHEMA, CONTENT_SCHEMA, ASSESSMENT_SCHEMA,
    REVIEW_SCHEMA, REFINEMENT_SCHEMA,
)


@dataclass
class WorkflowState:
    learner: Dict[str, Any]
    plan: Dict[str, Any] = field(default_factory=dict)
    content: Dict[str, Any] = field(default_factory=dict)
    assessment: Dict[str, Any] = field(default_factory=dict)
    review: Dict[str, Any] = field(default_factory=dict)
    refinement: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    attempts: Dict[str, int] = field(default_factory=dict)


def call_llm(
    client: OpenAI,
    model: str,
    stage: str,
    context: Dict[str, Any],
    schema: Dict[str, Any],
    instructions: str,
    max_retries: int = 2,
) -> Dict[str, Any]:
    """Call the model with Structured Outputs and retry failed calls."""

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input=json.dumps(context, ensure_ascii=False),
                text={
                    "format": {
                        "type": "json_schema",
                        "name": f"{stage}_output",
                        "schema": schema,
                        "strict": True,
                    }
                },
            )

            if not response.output_text:
                raise ValueError("The model returned an empty response.")

            data = json.loads(response.output_text)

            if not isinstance(data, dict):
                raise ValueError("The model output is not a JSON object.")

            return data

        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(1.5 * (attempt + 1))

    raise RuntimeError(
        f"{stage.capitalize()} failed after {max_retries + 1} attempt(s): "
        f"{last_error}"
    )


def run_planning(state, client, model, retries):
    return call_llm(
        client, model, "planning",
        {"learner": state.learner},
        PLAN_SCHEMA, PLANNING_PROMPT, retries
    )


def run_content(state, client, model, retries):
    return call_llm(
        client, model, "content",
        {"learner": state.learner, "plan": state.plan},
        CONTENT_SCHEMA, CONTENT_PROMPT, retries
    )


def run_assessment(state, client, model, retries):
    return call_llm(
        client, model, "assessment",
        {
            "learner": state.learner,
            "plan": state.plan,
            "content": state.content,
        },
        ASSESSMENT_SCHEMA, ASSESSMENT_PROMPT, retries
    )


def run_review(state, client, model, retries):
    return call_llm(
        client, model, "review",
        {
            "learner": state.learner,
            "plan": state.plan,
            "content": state.content,
            "assessment": state.assessment,
        },
        REVIEW_SCHEMA, REVIEW_PROMPT, retries
    )


def run_refinement(state, client, model, retries):
    return call_llm(
        client, model, "refinement",
        {
            "learner": state.learner,
            "plan": state.plan,
            "content": state.content,
            "assessment": state.assessment,
            "review": state.review,
        },
        REFINEMENT_SCHEMA, REFINEMENT_PROMPT, retries
    )


STAGES = [
    ("planning", run_planning, "Creates objectives and the personalized study plan."),
    ("content", run_content, "Generates explanations, examples, and activities."),
    ("assessment", run_assessment, "Creates objective-aligned assessment questions."),
    ("review", run_review, "Audits accuracy, alignment, difficulty, and completeness."),
    ("refinement", run_refinement, "Applies review feedback to create the final pack."),
]


def run_workflow(
    learner_profile: Dict[str, Any],
    api_key: str,
    model: str = "gpt-5-mini",
    max_retries: int = 2,
    progress_callback=None,
) -> WorkflowState:
    """Execute all five stages with explicit context passing and error handling."""

    if not api_key:
        raise ValueError("OpenAI API key is missing.")

    client = OpenAI(api_key=api_key)
    state = WorkflowState(learner=learner_profile)

    for index, (name, function, description) in enumerate(STAGES, start=1):
        state.attempts[name] = 0

        if progress_callback:
            progress_callback(index - 1, name, description)

        success = False

        for attempt in range(max_retries + 1):
            state.attempts[name] += 1

            try:
                result = function(state, client, model, 0)

                if name == "planning":
                    state.plan = result
                elif name == "content":
                    state.content = result
                elif name == "assessment":
                    state.assessment = result
                elif name == "review":
                    state.review = result
                elif name == "refinement":
                    state.refinement = result

                success = True
                break

            except Exception as exc:
                state.errors.append({
                    "stage": name,
                    "attempt": attempt + 1,
                    "error": str(exc),
                })

                if attempt < max_retries:
                    time.sleep(1.5 * (attempt + 1))

        if not success:
            raise RuntimeError(
                f"Workflow stopped at '{name}' after "
                f"{max_retries + 1} attempt(s)."
            )

    if progress_callback:
        progress_callback(5, "complete", "All workflow stages completed.")

    return state
