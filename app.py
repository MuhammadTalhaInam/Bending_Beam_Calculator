# app.py
"""Main Streamlit application for the AI Personalized Study Pack Generator."""

import os
import json
import streamlit as st

from workflow import run_workflow, STAGES


st.set_page_config(
    page_title="AI Personalized Study Pack",
    page_icon="🧠",
    layout="wide",
)


def get_api_key():
    try:
        secret = st.secrets.get("OPENAI_API_KEY")
        if secret:
            return str(secret)
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY", "")


def show_workflow(stage_status):
    cols = st.columns(5)
    for col, (name, label, _) in zip(cols, STAGES):
        status = stage_status.get(name, "waiting")
        icon = {
            "waiting": "⏳",
            "running": "🔄",
            "done": "✅",
            "error": "❌",
        }.get(status, "⏳")
        with col:
            st.markdown(f"### {icon}")
            st.caption(label)


def render_final_pack(state):
    final = state.refinement
    pack = final.get("study_pack", {})

    st.header("🎓 Final Personalized Study Pack")
    st.subheader(final.get("title", "Study Pack"))

    if final.get("quality_summary"):
        st.info(final["quality_summary"])

    st.markdown("### Learning Objectives")
    for item in pack.get("learning_objectives", []):
        st.markdown(f"- {item}")

    st.markdown("### Lessons")
    for i, lesson in enumerate(pack.get("lessons", []), 1):
        with st.expander(f"{i}. {lesson.get('topic', 'Lesson')}", expanded=True):
            st.markdown(lesson.get("summary", ""))

            st.markdown("**Key Points**")
            for point in lesson.get("key_points", []):
                st.markdown(f"- {point}")

            st.markdown("**Example**")
            st.markdown(lesson.get("example", ""))

            st.markdown("**Practice**")
            st.markdown(lesson.get("practice", ""))

    st.markdown("### 📝 Quiz")
    for i, question in enumerate(pack.get("quiz", []), 1):
        st.markdown(f"**{i}. {question.get('question', '')}**")

        for option in question.get("options", []):
            st.markdown(f"- {option}")

        with st.expander(f"Show answer {i}"):
            st.markdown(f"**Answer:** {question.get('answer', '')}")
            st.markdown(f"**Explanation:** {question.get('explanation', '')}")

    st.markdown("### 🔁 Revision Plan")
    for item in pack.get("revision_plan", []):
        st.markdown(f"- {item}")


st.title("🧠 AI Personalized Study Pack Generator")
st.write(
    "A five-stage AI workflow: Planning → Content → Assessment → Review → Refinement"
)

with st.sidebar:
    st.header("👤 Learner Profile")

    subject = st.text_input("Subject", "Physics")
    topic = st.text_input("Topic", "Beam bending and deflection")

    level = st.selectbox(
        "Learning level",
        ["Beginner", "Intermediate", "Advanced"],
        index=1,
    )

    goals = st.text_area(
        "Learning goals",
        "Understand the concepts and solve practical problems.",
    )

    study_time = st.slider(
        "Available study time (minutes)",
        min_value=15,
        max_value=180,
        value=60,
        step=5,
    )

    learning_styles = st.multiselect(
        "Preferred learning styles",
        [
            "Step-by-step",
            "Examples",
            "Visual",
            "Practice questions",
            "Conceptual explanations",
        ],
        default=["Step-by-step", "Examples", "Practice questions"],
    )

    language = st.selectbox(
        "Output language",
        ["English", "Simple English", "Urdu"],
    )

    difficulty = st.select_slider(
        "Target difficulty",
        options=["Easy", "Moderate", "Challenging"],
        value="Moderate",
    )

    additional_context = st.text_area(
        "Additional learning context",
        "Focus on practical understanding.",
    )

    st.divider()

    model = st.text_input(
        "OpenAI model",
        "gpt-5-mini",
        help="Use a model available to your OpenAI API account.",
    )

    max_retries = st.slider(
        "Retries per failed stage",
        0, 3, 2,
    )

    generate = st.button(
        "🚀 Generate Study Pack",
        type="primary",
        use_container_width=True,
    )


if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None

if "stage_status" not in st.session_state:
    st.session_state.stage_status = {
        name: "waiting" for name, _, _ in STAGES
    }


if generate:
    if not subject.strip() or not topic.strip() or not goals.strip():
        st.error("Please provide the subject, topic, and learning goals.")
    elif not get_api_key():
        st.error(
            "OPENAI_API_KEY is missing. Add it to Streamlit Secrets before "
            "running the workflow."
        )
    else:
        learner_profile = {
            "subject": subject.strip(),
            "topic": topic.strip(),
            "level": level,
            "learning_goals": goals.strip(),
            "available_study_time_minutes": study_time,
            "preferred_learning_styles": learning_styles,
            "language": language,
            "target_difficulty": difficulty,
            "additional_context": additional_context.strip(),
        }

        status_box = st.empty()
        progress = st.progress(0)

        st.session_state.stage_status = {
            name: "waiting" for name, _, _ in STAGES
        }

        def progress_callback(completed, stage, description):
            if stage in st.session_state.stage_status:
                st.session_state.stage_status[stage] = "running"

            show_workflow(st.session_state.stage_status)

            if stage == "complete":
                progress.progress(1.0)
                status_box.success(description)
            else:
                progress.progress(completed / 5)
                status_box.info(
                    f"Stage {completed + 1}/5: **{stage.title()}** — {description}"
                )

        try:
            state = run_workflow(
                learner_profile=learner_profile,
                api_key=get_api_key(),
                model=model,
                max_retries=max_retries,
                progress_callback=progress_callback,
            )

            for name, _, _ in STAGES:
                st.session_state.stage_status[name] = "done"

            st.session_state.workflow_state = state
            show_workflow(st.session_state.stage_status)
            status_box.success("🎉 Study pack generated successfully!")

        except Exception as exc:
            st.error(f"Workflow failed: {exc}")
            state = st.session_state.workflow_state


state = st.session_state.workflow_state

if state:
    st.divider()

    tab1, tab2, tab3 = st.tabs(
        ["🎓 Final Study Pack", "🔍 AI Review", "🛠 Diagnostics"]
    )

    with tab1:
        if state.refinement:
            render_final_pack(state)
        else:
            st.warning("Final refinement output is unavailable.")

    with tab2:
        if state.review:
            review = state.review

            score = int(review.get("overall_score", 0))
            st.metric("AI Quality Score", f"{score}/100")

            st.markdown("### Strengths")
            for item in review.get("strengths", []):
                st.markdown(f"- {item}")

            st.markdown("### Issues Found")
            issues = review.get("issues", [])

            if issues:
                for issue in issues:
                    severity = issue.get("severity", "Issue")
                    st.warning(
                        f"**{severity} — {issue.get('area', '')}**\n\n"
                        f"{issue.get('issue', '')}\n\n"
                        f"Recommendation: {issue.get('recommendation', '')}"
                    )
            else:
                st.success("No significant issues were identified.")

            st.markdown("### Refinement Instructions")
            for item in review.get("refinement_instructions", []):
                st.markdown(f"- {item}")

    with tab3:
        st.markdown("### Retry / Error Log")

        if state.errors:
            for error in state.errors:
                st.error(
                    f"**{error['stage']}** — attempt {error['attempt']}: "
                    f"{error['error']}"
                )
        else:
            st.success("No errors occurred.")

        st.markdown("### Stage Attempts")
        for name, label, _ in STAGES:
            st.write(
                f"**{label}:** "
                f"{state.attempts.get(name, 0)} attempt(s)"
            )

        st.markdown("### Context Passing")
        st.code(
            """Learner Profile
      ↓
Planning → plan
      ↓
Content Generation → content
      ↓
Assessment → assessment
      ↓
Review → quality findings
      ↓
Refinement → final study pack""",
            language="text",
        )

        with st.expander("View raw workflow state"):
            st.json({
                "learner": state.learner,
                "plan": state.plan,
                "content": state.content,
                "assessment": state.assessment,
                "review": state.review,
                "refinement": state.refinement,
            })

st.divider()
st.caption(
    "AI-generated educational material should be reviewed before use in "
    "high-stakes academic or professional settings."
)
