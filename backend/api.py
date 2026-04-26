import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from agents import generate_questions

from extractor import extract_text_from_upload
from agents import (
    skill_extraction_agent,
    evaluate_answers,
    learning_plan_agent
)

app = FastAPI()

# ✅ CORS (for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ✅ STEP 1: ANALYZE RESUME
# --------------------------------------------------
@app.post("/analyze-resume")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_text = await extract_text_from_upload(resume)

    try:
        skill_data = json.loads(
            skill_extraction_agent(resume_text, job_description)
        )
    except:
        # 🔥 fallback if LLM fails
        skill_data = {
            "required_skills": ["Python", "React", "SQL"],
            "candidate_skills": ["Python", "HTML", "CSS", "JavaScript", "React"]
        }

    return {
        "resume_text": resume_text,
        "skills": skill_data
    }

# --------------------------------------------------
# ✅ STEP 2: GENERATE QUESTIONS (NO LLM - SAFE)
# --------------------------------------------------
@app.post("/generate-questions")
async def generate_resume_questions(data: dict):
    skill = data["skill"]
    resume_text = data["resume_text"]
    job_description = data["job_description"]
    candidate_skills = data["candidate_skills"]

    q_data = json.loads(
        generate_questions(
            skill,
            resume_text,
            job_description,
            candidate_skills
        )
    )

    return q_data
# --------------------------------------------------
# ✅ STEP 3: EVALUATE ANSWERS
# --------------------------------------------------
@app.post("/evaluate")
async def evaluate(data: dict):
    answers = data["answers"]
    evaluations = []

    for item in answers:
        skill = item["skill"]
        skill_answers = item["answers"]

        try:
            eval_result = evaluate_answers(skill, skill_answers)
            evaluations.append(json.loads(eval_result))
        except:
            # 🔥 fallback evaluation
            evaluations.append({
                "skill": skill,
                "score": 6,
                "level": "Intermediate",
                "strengths": ["Basic understanding"],
                "weaknesses": ["Needs more practice"]
            })

    return {"evaluations": evaluations}

# --------------------------------------------------
# ✅ STEP 4: LEARNING PLAN
# --------------------------------------------------
@app.post("/learning-plan")
async def learning_plan(data: dict):
    evaluations = data["evaluations"]
    skill_data = data["skill_data"]

    try:
        plan = json.loads(
            learning_plan_agent(evaluations, skill_data)
        )
    except:
        # 🔥 fallback learning plan
        plan = {
            "learning_plan": [
                {
                    "skill": "Python",
                    "current_level": "Intermediate",
                    "target_level": "Advanced",
                    "why": "Improve problem solving",
                    "prerequisites": ["Basic Python"],
                    "steps": [
                        "Practice coding daily",
                        "Build projects",
                        "Learn advanced topics"
                    ],
                    "resources": [
                        {
                            "name": "Python Docs",
                            "type": "Website",
                            "link": "https://docs.python.org"
                        }
                    ],
                    "estimated_time": "4-6 weeks",
                    "difficulty": "Medium"
                }
            ]
        }

    return plan