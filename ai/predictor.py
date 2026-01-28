# ai/predictor.py
"""
AI-Based Exam Performance Predictor
Technique: Feature Engineering + Weighted Regression
"""

def predict_exam_performance(
    study_hours_per_day,
    attendance_percentage,
    assignment_completion_rate,
    previous_exam_score
):
    """
    Inputs:
    - study_hours_per_day: float (0–10)
    - attendance_percentage: float (0–100)
    - assignment_completion_rate: float (0–100)
    - previous_exam_score: float (0–100)

    Returns:
    - predicted_score: float
    - level: str
    - suggestions: list[str]
    """

    # ---------------- FEATURE ENGINEERING ----------------

    study_score = min(study_hours_per_day / 10, 1.0) * 100
    attendance_score = attendance_percentage
    assignment_score = assignment_completion_rate
    past_score = previous_exam_score

    # ---------------- WEIGHTED REGRESSION ----------------
    # Weights chosen based on academic importance

    predicted_score = (
        0.30 * study_score +
        0.25 * attendance_score +
        0.25 * assignment_score +
        0.20 * past_score
    )

    predicted_score = round(predicted_score, 2)

    # ---------------- CLASSIFICATION ----------------

    if predicted_score >= 85:
        level = "Excellent"
    elif predicted_score >= 70:
        level = "Good"
    elif predicted_score >= 55:
        level = "Average"
    else:
        level = "At Risk"

    # ---------------- AI RECOMMENDATIONS ----------------

    suggestions = []

    if study_hours_per_day < 3:
        suggestions.append("Increase daily study time to at least 3–4 hours.")

    if attendance_percentage < 75:
        suggestions.append("Improve class attendance to strengthen understanding.")

    if assignment_completion_rate < 70:
        suggestions.append("Complete assignments regularly to boost consistency.")

    if previous_exam_score < 60:
        suggestions.append("Revise weak topics from previous exams.")

    if not suggestions:
        suggestions.append("Maintain your current study strategy. You're on the right track!")

    return predicted_score, level, suggestions
