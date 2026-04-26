import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from extractor import extract_text
from agents import (
    skill_extraction_agent,
    conduct_assessment,
    evaluate_answers,
    learning_plan_agent
)


def run_pipeline(resume_path, job_description):
    print("Step 1: Extracting Resume...")
    resume_text = extract_text(resume_path)

    print("Step 2: Extracting Skills...")
    skill_data = json.loads(
        skill_extraction_agent(resume_text, job_description)
    )

    required_skills = skill_data["required_skills"]
    candidate_skills = skill_data["candidate_skills"]

    print("Candidate Skills Found:")
    print(candidate_skills)

    print("Step 3: Conversational Assessment...")
    answers = conduct_assessment(
        required_skills,
        resume_text,
        job_description,
        candidate_skills
    )

    print("Step 4: Evaluating...")
    evaluations = []

    for skill, ans in answers.items():
        eval_result = evaluate_answers(skill, ans)
        evaluations.append(json.loads(eval_result))

    print("Step 5: Learning Plan Generation...")
    learning_plan = json.loads(
        learning_plan_agent(evaluations, skill_data)
    )

    final_output = {
        "skills": skill_data,
        "evaluations": evaluations,
        "learning_plan": learning_plan
    }

    print("\nFINAL OUTPUT:\n")
    print(json.dumps(final_output, indent=2))


if __name__ == "__main__":
    # 🔹 Open file picker (no manual typing)
    Tk().withdraw()
    resume_path = askopenfilename(
        title="Select Resume",
        filetypes=[("PDF files", "*.pdf"), ("DOCX files", "*.docx")]
    )

    if not resume_path:
        print("No file selected ❌")
        exit()

    print(f"Selected file: {resume_path}")

    job_description = input("Enter job description: ")

    run_pipeline(resume_path, job_description)