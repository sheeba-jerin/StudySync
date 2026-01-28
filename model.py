import pandas as pd
from sklearn.tree import DecisionTreeClassifier

def train_model():
    data = pd.DataFrame({
        "attendance": [85,60,90,70,50,95,65,80],
        "study_hours": [6,3,7,4,2,8,3,5],
        "internal_marks": [78,45,88,60,40,92,55,70],
        "assignment_score": [80,50,85,65,45,90,60,75],
        "result": [1,0,1,1,0,1,0,1]
    })

    X = data[["attendance","study_hours","internal_marks","assignment_score"]]
    y = data["result"]

    model = DecisionTreeClassifier()
    model.fit(X, y)

    return model
