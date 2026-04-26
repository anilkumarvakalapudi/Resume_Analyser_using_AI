import {useState} from 'react'
import './App.css'

import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'


function App() {
  const [resume, setResume] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [result, setResult] = useState(null)
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [evaluations, setEvaluations] = useState([])
  const [learningPlan, setLearningPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [qLoading, setQLoading] = useState(false)
  const [evalLoading, setEvalLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  const onSubmitForm = async event => {
    event.preventDefault()

    if (resume === null || jobDescription === '') {
      setErrorMsg('Please upload resume and enter job description')
      return
    }

    setLoading(true)
    setErrorMsg('')
    setResult(null)
    setQuestions([])
    setAnswers({})
    setEvaluations([])
    setLearningPlan(null)

    const formData = new FormData()
    formData.append('resume', resume)
    formData.append('job_description', jobDescription)

    try {
      const response = await fetch('http://localhost:8000/analyze-resume', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        setResult(data)
      } else {
        setErrorMsg('Failed to analyze resume')
      }
    } catch (err) {
      setErrorMsg('Server error')
    }

    setLoading(false)
  }

const downloadPDF = () => {
  const pdf = new jsPDF('p', 'mm', 'a4')

  let y = 15

  pdf.setFontSize(18)
  pdf.text('Personalized Learning Plan', 15, y)
  y += 12

  learningPlan.learning_plan.forEach(item => {
    if (y > 260) {
      pdf.addPage()
      y = 15
    }

    pdf.setFontSize(14)
    pdf.text(item.skill, 15, y)
    y += 8

    pdf.setFontSize(11)

    const details = [
      `Current Level: ${item.current_level}`,
      `Target Level: ${item.target_level}`,
      `Why: ${item.why}`,
      `Estimated Time: ${item.estimated_time}`,
      `Difficulty: ${item.difficulty}`,
    ]

    details.forEach(line => {
      const wrapped = pdf.splitTextToSize(line, 180)
      pdf.text(wrapped, 15, y)
      y += wrapped.length * 6
    })

    y += 4
    pdf.setFontSize(12)
    pdf.text('Steps:', 15, y)
    y += 7

    pdf.setFontSize(11)

    item.steps.forEach(step => {
      const wrappedStep = pdf.splitTextToSize(`• ${step}`, 175)

      if (y > 270) {
        pdf.addPage()
        y = 15
      }

      pdf.text(wrappedStep, 20, y)
      y += wrappedStep.length * 6
    })

    y += 10
  })

  pdf.save('Personalized_Learning_Plan.pdf')
}

  const generateQuestions = async () => {
    setQLoading(true)
    setQuestions([])
    setAnswers({})

    const allQuestions = []

    for (let skill of result.skills.candidate_skills) {
      const response = await fetch('http://localhost:8000/generate-questions', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          skill: skill,
          resume_text: result.resume_text,
          job_description: jobDescription,
          candidate_skills: result.skills.candidate_skills,
        }),
      })

      const data = await response.json()

      allQuestions.push({
        skill: skill,
        questions: data.questions || [],
      })
    }

    setQuestions(allQuestions)
    setQLoading(false)
  }

  const onChangeAnswer = (skill, question, value) => {
    const key = skill + '---' + question

    setAnswers(prev => ({
      ...prev,
      [key]: value,
    }))
  }

  const evaluateAllAnswers = async () => {
    setEvalLoading(true)

    const formattedAnswers = questions.map(item => ({
      skill: item.skill,
      answers: item.questions.map(q => ({
        q: q,
        a: answers[item.skill + '---' + q] || '',
      })),
    }))

    const evalResponse = await fetch('http://localhost:8000/evaluate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        answers: formattedAnswers,
      }),
    })

    const evalData = await evalResponse.json()
    setEvaluations(evalData.evaluations)

    const planResponse = await fetch('http://localhost:8000/learning-plan', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        evaluations: evalData.evaluations,
        skill_data: result.skills,
      }),
    })

    const planData = await planResponse.json()
    setLearningPlan(planData)

    setEvalLoading(false)
  }

  return (
    <div className="app-container">
      <div className="card">
        <h1>AI Resume Skill Assessment</h1>

        <form onSubmit={onSubmitForm}>
          <label>Upload Resume</label>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={event => setResume(event.target.files[0])}
          />

          <label>Job Description</label>
          <textarea
            rows="5"
            value={jobDescription}
            onChange={event => setJobDescription(event.target.value)}
          />

          <button type="submit">
            {loading ? 'Analyzing...' : 'Analyze Resume'}
          </button>

          {errorMsg && <p className="error">{errorMsg}</p>}
        </form>
      </div>

      {result && (
        <div className="result-card">
          <h2>Extracted Skills</h2>

          <h3>Required Skills</h3>
          <div className="skills-list">
            {result.skills.required_skills.map(skill => (
              <span key={skill}>{skill}</span>
            ))}
          </div>

          <h3>Candidate Skills</h3>
          <div className="skills-list">
            {result.skills.candidate_skills.map(skill => (
              <span key={skill}>{skill}</span>
            ))}
          </div>

          <button onClick={generateQuestions}>
            {qLoading ? 'Generating...' : 'Generate Questions'}
          </button>
        </div>
      )}

      {questions.length > 0 && (
        <div className="result-card">
          <h2>Interview Questions</h2>

          {questions.map(item => (
            <div key={item.skill}>
              <h3>{item.skill}</h3>

              {item.questions.map((q, index) => (
                <div key={index} className="question-box">
                  <p>{q}</p>

                  <textarea
                    rows="3"
                    placeholder="Type your answer here..."
                    value={answers[item.skill + '---' + q] || ''}
                    onChange={event =>
                      onChangeAnswer(item.skill, q, event.target.value)
                    }
                  />
                </div>
              ))}
            </div>
          ))}

          <button onClick={evaluateAllAnswers}>
            {evalLoading ? 'Evaluating...' : 'Evaluate Answers'}
          </button>
        </div>
      )}

      {evaluations.length > 0 && (
        <div className="result-card">
          <h2>Evaluation Result</h2>

          {evaluations.map(item => (
            <div key={item.skill}>
              <h3>{item.skill}</h3>
              <p>Score: {item.score}/10</p>
              <p>Level: {item.level}</p>
              <p>Strengths: {item.strengths.join(', ')}</p>
              <p>Weaknesses: {item.weaknesses.join(', ')}</p>
            </div>
          ))}
        </div>
      )}

      {learningPlan && (
  <div className="result-card">
    <div id="learning-plan">
      <h2>Personalized Learning Plan</h2>

      {learningPlan.learning_plan.map(item => (
        <div key={item.skill} className="plan-box">
          <h3>{item.skill}</h3>
          <p>Current Level: {item.current_level}</p>
          <p>Target Level: {item.target_level}</p>
          <p>Why: {item.why}</p>
          <p>Estimated Time: {item.estimated_time}</p>
          <p>Difficulty: {item.difficulty}</p>

          <h4>Steps</h4>
          <ul>
            {item.steps.map(step => (
              <li key={step}>{step}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>

    <button onClick={downloadPDF}>
      Download Learning Plan PDF
    </button>
  </div>
)}
    </div>
  )
}

export default App