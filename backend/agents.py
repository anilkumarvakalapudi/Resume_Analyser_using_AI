import json
from llm import call_llm
from skillsgraph import ADJACENT_SKILLS


def skill_extraction_agent(resume_text, jd_text):
    system = "You extract structured technical skills."

    user = f"""
Extract skills from JD and Resume.

Return ONLY JSON in this format:
{{
  "required_skills": [],
  "candidate_skills": []
}}

Rules:
- required_skills should come from job description
- candidate_skills should come from resume
- Do not include explanation

JD:
{jd_text}

RESUME:
{resume_text}
"""

    return call_llm(system, user)


def generate_questions(skill, resume_text, jd_text, candidate_skills):
    system = "You are a senior technical interviewer."

    user = f"""
Generate exactly 3 interview questions for this skill: {skill}.

Rules:
- Questions must be based on the candidate's resume.
- Use the candidate's projects, internships, tools, and technologies.
- Also connect questions to the job description.
- Do NOT ask same generic questions like "Explain your experience".
- Do NOT ask unrelated theory.
- Each question should be different and practical.
- Return ONLY JSON.

Return format:
{{
  "questions": [
    "question 1",
    "question 2",
    "question 3"
  ]
}}

Job Description:
{jd_text}

Candidate Skills:
{candidate_skills}

Resume:
{resume_text}
"""

    response = call_llm(system, user)

    try:
        data = json.loads(response)
        questions = data.get("questions", [])

        clean_questions = []

        for q in questions:
            if isinstance(q, str):
                clean_questions.append(q)
            elif isinstance(q, dict):
                clean_questions.append(q.get("question", ""))

        return json.dumps({"questions": clean_questions})

    except Exception:
        return json.dumps({
            "questions": [
                f"Based on your resume, where did you use {skill} in your project?",
                f"How did {skill} help in your project implementation?",
                f"What challenge did you face while working with {skill}?"
            ]
        })


def conduct_assessment(skills, resume_text, jd_text, candidate_skills):
    answers = {}

    for skill in skills:
        print(f"\n--- Assessing {skill} ---")

        q_data = json.loads(
            generate_questions(skill, resume_text, jd_text, candidate_skills)
        )

        skill_answers = []

        for q in q_data["questions"]:
            print(f"\nQ: {q}")
            ans = input("Your Answer: ")
            skill_answers.append({"q": q, "a": ans})

        answers[skill] = skill_answers

    return answers


def evaluate_answers(skill, answers):
    system = "You are a strict technical evaluator."

    user = f"""
Evaluate the candidate answers for this skill: {skill}.

Return ONLY JSON:
{{
  "skill": "{skill}",
  "score": 1,
  "level": "Beginner",
  "strengths": [],
  "weaknesses": []
}}

Rules:
- score must be between 1 and 10
- level must be Beginner, Intermediate, or Advanced
- strengths should be based on answer quality
- weaknesses should mention improvement areas

Answers:
{answers}
"""

    try:
        response = call_llm(system, user)
        data = json.loads(response)
        return json.dumps(data)

    except Exception:
        return json.dumps({
            "skill": skill,
            "score": 6,
            "level": "Intermediate",
            "strengths": ["Basic understanding of the skill"],
            "weaknesses": ["Needs more practical explanation and project examples"]
        })


def learning_plan_agent(evaluations, skill_data):
    system = """
You are an expert career coach.

Create realistic personalized learning plans.

Rules:
- Suggest only logical next-step skills
- Use candidate strengths
- Fix weaknesses
- Avoid unrealistic jumps
- Return ONLY JSON
"""

    user = f"""
Candidate Skills:
{skill_data}

Evaluation:
{evaluations}

Skill Adjacency Map:
{ADJACENT_SKILLS}

Return JSON:
{{
  "learning_plan": [
    {{
      "skill": "",
      "current_level": "",
      "target_level": "",
      "why": "",
      "prerequisites": [],
      "steps": [],
      "resources": [
        {{
          "name": "",
          "type": "",
          "link": ""
        }}
      ],
      "estimated_time": "",
      "difficulty": ""
    }}
  ]
}}
"""

    try:
        response = call_llm(system, user)
        data = json.loads(response)
        return json.dumps(data)

    except Exception:
        plans = []

        for item in evaluations:
            skill = item.get("skill", "Skill")
            level = item.get("level", "Beginner")

            next_skills = ADJACENT_SKILLS.get(skill, [])

            plans.append({
                "skill": skill,
                "current_level": level,
                "target_level": "Advanced",
                "why": f"To improve your career readiness in {skill}.",
                "prerequisites": [skill],
                "steps": [
                    f"Revise the fundamentals of {skill}",
                    f"Practice hands-on examples using {skill}",
                    f"Build one small project using {skill}",
                    f"Learn related skills: {', '.join(next_skills) if next_skills else 'advanced concepts'}"
                ],
                "resources": [
                    {
                        "name": f"{skill} official documentation or beginner tutorial",
                        "type": "Website",
                        "link": ""
                    }
                ],
                "estimated_time": "4-6 weeks",
                "difficulty": "Medium"
            })

        return json.dumps({"learning_plan": plans})