from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import shap

app = Flask(__name__)
print("Loading model and encoders...")
model = joblib.load('professional_loan_model.pkl')
le_dict = joblib.load('professional_label_encoders.pkl')
print("Model and encoders loaded successfully!")
explainer = shap.TreeExplainer(model)

model_features = ['age', 'gender', 'married', 'dependents', 'education', 'employment_type', 'years_at_job', 'annual_income', 'coapplicant_income', 'credit_score', 'credit_history', 'loan_amount', 'loan_amount_term', 'loan_purpose', 'property_area', 'collateral_value']

# Helper to encode input using label encoders
def encode_input(data):
    print("Encoding input data...")
    encoded = {}
    for f in model_features:
        if f in le_dict:
            encoded[f] = le_dict[f].transform([data[f]])[0]
        else:
            encoded[f] = data[f]
    print("Encoded data:", encoded)
    return encoded

def explain_rejection(data):
    reasons = []
    if data.get('credit_score', 700) < 650:
        reasons.append('Low credit score')
    if data.get('credit_history', 'Good') in ['Bad', 0]:
        reasons.append('Bad credit history')
    if int(data.get('annual_income', 500)) < 200:
        reasons.append('Low annual income')
    if int(data.get('loan_amount', 150)) > int(data.get('annual_income', 500)) * 0.6:
        reasons.append('Loan amount is high compared to income')
    if int(data.get('years_at_job', 5)) < 2:
        reasons.append('Short job duration')
    if int(data.get('collateral_value', 0)) < int(data.get('loan_amount', 150)) * 0.5:
        reasons.append('Insufficient collateral value')
    return reasons or ['General risk factors based on application']

def calculate_loan_terms(loan_amount, loan_amount_term, credit_score):
    # Simple interest rate logic based on credit score
    if credit_score >= 800:
        interest_rate = 7.0
    elif credit_score >= 750:
        interest_rate = 8.0
    elif credit_score >= 700:
        interest_rate = 9.0
    elif credit_score >= 650:
        interest_rate = 10.5
    else:
        interest_rate = 13.0
    # EMI calculation
    P = loan_amount * 1000  # convert to actual amount
    N = loan_amount_term
    R = interest_rate / (12 * 100)
    EMI = (P * R * (1 + R) ** N) / ((1 + R) ** N - 1) if R > 0 else P / N
    total_payment = EMI * N
    return {
        'interest_rate': round(interest_rate, 2),
        'emi': round(EMI, 2),
        'total_payment': round(total_payment, 2)
    }

def get_shap_reasons(input_df):
    shap_values = explainer.shap_values(input_df)
    print('shap_values type:', type(shap_values))
    print('shap_values shape:', getattr(shap_values, 'shape', 'no shape'))
    if isinstance(shap_values, list):
        print('shap_values[1] type:', type(shap_values[1]))
        print('shap_values[1] shape:', getattr(shap_values[1], 'shape', 'no shape'))
        shap_values = shap_values[1]
    print('shap_values[0] type:', type(shap_values[0]))
    print('shap_values[0] shape:', getattr(shap_values[0], 'shape', 'no shape'))
    # Ensure we have a 1D array of floats for the first sample
    shap_vals = shap_values[0]
    # If shap_vals is not a 1D array, flatten it
    if hasattr(shap_vals, 'flatten'):
        shap_vals = shap_vals.flatten()
    # If any element is an array, extract the scalar
    shap_vals = [float(s[0]) if hasattr(s, '__len__') and not isinstance(s, str) and len(s) == 1 else float(s) for s in shap_vals]
    feature_importance = pd.DataFrame([
        {'feature': f, 'shap_value': s, 'value': v}
        for f, s, v in zip(model_features, shap_vals, input_df.iloc[0].tolist())
    ])
    feature_importance['abs_shap'] = feature_importance['shap_value'].abs()
    top_features = feature_importance.sort_values('abs_shap', ascending=False).head(3)
    explanations = []
    for _, row in top_features.iterrows():
        direction = 'increased' if row['shap_value'] > 0 else 'decreased'
        explanations.append(f"{row['feature']} ({row['value']}) {direction} the approval probability")
    return explanations

@app.route('/predict', methods=['POST'])
def predict():
    print("Received prediction request!")
    data = request.get_json()
    print("Input data:", data)
    
    try:
        # Encode input
        encoded = encode_input(data)
        input_df = pd.DataFrame([encoded], columns=model_features)
        print("Input DataFrame:", input_df)
        
        prediction = model.predict(input_df)[0]
        print("Raw prediction:", prediction)
        
        result = le_dict['loan_status'].inverse_transform([prediction])[0]
        print("Final result:", result)
        
        response = {'prediction': result}
        if result == 'Approved':
            # Calculate loan terms
            terms = calculate_loan_terms(
                float(data['loan_amount']),
                int(data['loan_amount_term']),
                int(data['credit_score'])
            )
            response['bank_summary'] = {
                'Interest Rate (%)': terms['interest_rate'],
                'EMI (per month)': terms['emi'],
                'Total Payment': terms['total_payment'],
                'Loan Amount': float(data['loan_amount']) * 1000,
                'Loan Term (months)': int(data['loan_amount_term'])
            }
            response['message'] = (
                f"Congratulations! Your loan is approved.\n"
                f"Interest Rate: {terms['interest_rate']}% per annum\n"
                f"EMI: {terms['emi']} per month\n"
                f"Total Payment: {terms['total_payment']}\n"
                f"Loan Amount: {float(data['loan_amount']) * 1000}\n"
                f"Loan Term: {int(data['loan_amount_term'])} months"
            )
        else:
            response['reasons'] = explain_rejection(data)
        
        # SHAP explanations
        response['shap_reasons'] = get_shap_reasons(input_df)
        
        print("Sending response:", response)
        return jsonify(response)
        
    except Exception as e:
        print("Error occurred:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 