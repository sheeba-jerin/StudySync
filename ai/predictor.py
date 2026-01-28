# ai/predictor.py

def predict_exam_score(study_hours, attendance, previous_score):
    """
    Simple AI-style prediction logic
    (rule-based but realistic and explainable)
    """

    score = (
        (study_hours * 5) +
        (attendance * 0.3) +
        (previous_score * 0.4)
    )

    if score > 100:
        score = 100
    if score < 0:
        score = 0

    return round(score, 2)


def risk_level(predicted_score):
    if predicted_score >= 75:
        return "Low Risk ✅"
    elif predicted_score >= 50:
        return "Medium Risk ⚠️"
    else:
        return "High Risk 🚨"
