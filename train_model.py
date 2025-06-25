import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load data
df = pd.read_csv('loan_approval_dataset_large.csv')

# Drop applicant_id if present
if 'applicant_id' in df.columns:
    df = df.drop('applicant_id', axis=1)

# Encode categorical variables
le = LabelEncoder()
for col in ['gender', 'married', 'education', 'self_employed', 'property_area', 'loan_status']:
    df[col] = le.fit_transform(df[col])

# Features and target
X = df.drop('loan_status', axis=1)
y = df['loan_status']

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
joblib.dump(model, 'loan_model.pkl') 