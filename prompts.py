# prompts.py
"""Prompts and Structured Output schemas for the AI study-pack workflow."""

PLANNING_PROMPT = """
You are the Planning Agent in a personalized study-pack workflow.

Use the learner profile to design a focused, realistic learning plan.
Create measurable learning objectives, prerequisites, a logical topic sequence,
estimated study time, and a clear personalization strategy.

Do not invent learner facts. Keep the plan appropriate to the learner's level,
goals, available time, language, and preferred learning styles.
Return only the required structured JSON object.
"""

CONTENT_PROMPT = """
You are the Content Generation Agent.

Use the learner profile and the approved study plan as authoritative context.
Generate accurate, clear, personalized instructional content for every planned topic.

For each topic provide:
- a concise explanation,
- key points,
- a useful example,
- an active practice activity.

Adapt vocabulary, depth, examples, and presentation to the learner.
Do not skip planned objectives. Return only the required structured JSON object.
"""

ASSESSMENT_PROMPT = """
You are the Assessment Agent.

Use the learner profile, approved plan, and generated content.
Create an objective-aligned assessment that checks understanding and application.

Include a mixture of conceptual and practical questions where appropriate.
Every question must have an answer and a useful explanation.
State the target difficulty and the learning objective tested.
Use multiple-choice options when appropriate; otherwise use an empty options list.
Return only the required structured JSON object.
"""

REVIEW_PROMPT = """
You are the Quality Review Agent.

Audit the study plan, generated lessons, and assessment as a single educational
product.

Check:
1. factual accuracy and internal consistency,
2. objective alignment,
3. completeness,
4. learner-level appropriateness,
5. difficulty,
6. assessment coverage,
7. clarity and usefulness,
8. personalization.

Give an overall quality score from 0 to 100.
Identify concrete issues and provide actionable refinement instructions.
Return only the required structured JSON object.
"""

REFINEMENT_PROMPT = """
You are the Final Refinement Agent.

Produce the final personalized study pack using the learner profile, plan,
content, assessment, and review findings.

Treat review findings as quality-control requirements. Fix important problems,
preserve correct material, improve weak explanations, and ensure the final quiz
matches the lessons and learning objectives.

The final output must be directly usable by a student.
Return only the required structured JSON object.
"""

PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "learning_objectives": {"type": "array", "items": {"type": "string"}},
        "prerequisites": {"type": "array", "items": {"type": "string"}},
        "study_sequence": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "order": {"type": "integer"},
                    "topic": {"type": "string"},
                    "purpose": {"type": "string"},
                    "estimated_minutes": {"type": "integer"},
                },
                "required": ["order", "topic", "purpose", "estimated_minutes"],
            },
        },
        "personalization_strategy": {"type": "string"},
    },
    "required": [
        "title",
        "learning_objectives",
        "prerequisites",
        "study_sequence",
        "personalization_strategy",
    ],
}

CONTENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "topic": {"type": "string"},
                    "explanation": {"type": "string"},
                    "key_points": {"type": "array", "items": {"type": "string"}},
                    "example": {"type": "string"},
                    "practice_activity": {"type": "string"},
                },
                "required": [
                    "topic", "explanation", "key_points",
                    "example", "practice_activity"
                ],
            },
        },
        "study_tips": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["sections", "study_tips"],
}

ASSESSMENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "question": {"type": "string"},
                    "type": {"type": "string"},
                    "options": {"type": "array", "items": {"type": "string"}},
                    "answer": {"type": "string"},
                    "explanation": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "objective": {"type": "string"},
                },
                "required": [
                    "question", "type", "options", "answer",
                    "explanation", "difficulty", "objective"
                ],
            },
        },
        "answer_key_summary": {"type": "string"},
    },
    "required": ["questions", "answer_key_summary"],
}

REVIEW_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "overall_score": {"type": "integer"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "severity": {"type": "string"},
                    "area": {"type": "string"},
                    "issue": {"type": "string"},
                    "recommendation": {"type": "string"},
                },
                "required": ["severity", "area", "issue", "recommendation"],
            },
        },
        "refinement_instructions": {
            "type": "array", "items": {"type": "string"}
        },
    },
    "required": [
        "overall_score", "strengths", "issues", "refinement_instructions"
    ],
}

REFINEMENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "study_pack": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "learning_objectives": {
                    "type": "array", "items": {"type": "string"}
                },
                "lessons": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "topic": {"type": "string"},
                            "summary": {"type": "string"},
                            "key_points": {
                                "type": "array", "items": {"type": "string"}
                            },
                            "example": {"type": "string"},
                            "practice": {"type": "string"},
                        },
                        "required": [
                            "topic", "summary", "key_points",
                            "example", "practice"
                        ],
                    },
                },
                "quiz": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "question": {"type": "string"},
                            "options": {
                                "type": "array", "items": {"type": "string"}
                            },
                            "answer": {"type": "string"},
                            "explanation": {"type": "string"},
                        },
                        "required": [
                            "question", "options", "answer", "explanation"
                        ],
                    },
                },
                "revision_plan": {
                    "type": "array", "items": {"type": "string"}
                },
            },
            "required": [
                "learning_objectives", "lessons", "quiz", "revision_plan"
            ],
        },
        "quality_summary": {"type": "string"},
    },
    "required": ["title", "study_pack", "quality_summary"],
}
