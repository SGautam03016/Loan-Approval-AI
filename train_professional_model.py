import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

df = pd.read_csv('professional_loan_dataset.csv')

# Encode categoricals
cat_cols = ['gender', 'married', 'education', 'employment_type', 'credit_history', 'loan_purpose', 'property_area', 'loan_status']
le_dict = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    le_dict[col] = le

X = df.drop('loan_status', axis=1)
y = df['loan_status']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print('Train accuracy:', model.score(X_train, y_train))
print('Test accuracy:', model.score(X_test, y_test))

joblib.dump(model, 'professional_loan_model.pkl')
joblib.dump(le_dict, 'professional_label_encoders.pkl')
print('Model and encoders saved.') 