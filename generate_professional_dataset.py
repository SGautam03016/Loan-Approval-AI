import pandas as pd
import numpy as np
np.random.seed(42)

n = 20000

data = {
    'age': np.random.randint(21, 65, n),
    'gender': np.random.choice(['Male', 'Female'], n),
    'married': np.random.choice(['Yes', 'No'], n),
    'dependents': np.random.randint(0, 4, n),
    'education': np.random.choice(['Graduate', 'Not Graduate'], n),
    'employment_type': np.random.choice(['Salaried', 'Self-Employed', 'Business', 'Unemployed'], n),
    'years_at_job': np.random.randint(0, 30, n),
    'annual_income': np.random.randint(100, 2000, n),
    'coapplicant_income': np.random.randint(0, 1000, n),
    'credit_score': np.random.randint(300, 900, n),
    'credit_history': np.random.choice(['Good', 'Bad'], n, p=[0.8, 0.2]),
    'loan_amount': np.random.randint(50, 800, n),
    'loan_amount_term': np.random.choice([180, 240, 300, 360, 480], n),
    'loan_purpose': np.random.choice(['Home', 'Car', 'Education', 'Personal', 'Business', 'Other'], n),
    'property_area': np.random.choice(['Rural', 'Semiurban', 'Urban'], n),
    'collateral_value': np.random.randint(0, 1000, n),
}

df = pd.DataFrame(data)

# Simulate loan_status with a simple rule-based logic for demo
conditions = (
    (df['credit_score'] >= 650) &
    (df['credit_history'] == 'Good') &
    (df['annual_income'] > 200) &
    (df['loan_amount'] < df['annual_income'] * 0.6) &
    (df['years_at_job'] >= 2) &
    (df['collateral_value'] >= df['loan_amount'] * 0.5)
)
df['loan_status'] = np.where(conditions, 'Approved', 'Rejected')

df.to_csv('professional_loan_dataset.csv', index=False)
print('Synthetic professional dataset saved as professional_loan_dataset.csv') 