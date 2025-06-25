import streamlit as st
import requests
from PIL import Image

# --- Branding and Header ---
st.set_page_config(page_title='Loan Approval AI', page_icon=':money_with_wings:', layout='wide')

# Optional: Add a logo (replace with your logo path or URL)
# logo = Image.open('logo.png')
# st.image(logo, width=120)
st.markdown('💸 **Loan Approval AI System**', unsafe_allow_html=True)
st.markdown('AI-powered, explainable, and professional loan application analysis')
st.markdown('---')

# --- Helper for readable feature values ---
def readable_feature(feature, value):
    if feature == 'property_area':
        return f"Property Area: {['Rural', 'Semiurban', 'Urban'][int(value)]}"
    if feature == 'education':
        return f"Education: {'Graduate' if int(value) == 0 else 'Not Graduate'}"
    if feature == 'gender':
        return f"Gender: {'Male' if int(value) == 1 else 'Female'}"
    if feature == 'married':
        return f"Marital Status: {'Married' if int(value) == 1 else 'Single'}"
    if feature == 'credit_history':
        return f"Credit History: {'Good' if int(value) == 1 else 'Bad'}"
    if feature == 'self_employed':
        return f"Self Employed: {'Yes' if int(value) == 1 else 'No'}"
    return f"{feature.replace('_', ' ').title()}: {value}"

# --- Form Layout ---
with st.form('loan_form'):
    st.markdown('#### 👤 Personal Information')
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input('Age', min_value=18, max_value=100, value=30, help='Applicant age in years')
        gender = st.selectbox('Gender', [1, 0], format_func=lambda x: 'Male' if x == 1 else 'Female', help='Select gender')
    with col2:
        married = st.selectbox('Marital Status', [1, 0], format_func=lambda x: 'Married' if x == 1 else 'Single', help='Marital status')
        dependents = st.number_input('Dependents', min_value=0, max_value=10, value=0, help='Number of dependents')
    with col3:
        education = st.selectbox('Education', [0, 1], format_func=lambda x: 'Graduate' if x == 0 else 'Not Graduate', help='Highest education level')

    st.markdown('#### 💼 Employment & Financial Information')
    col4, col5, col6 = st.columns(3)
    with col4:
        employment_type = st.selectbox('Employment Type', ['Salaried', 'Self-Employed', 'Business', 'Unemployed'], help='Type of employment')
        years_at_job = st.number_input('Years at Current Job', min_value=0, max_value=50, value=5, help='Years at current job')
    with col5:
        annual_income = st.number_input('Annual Income (in thousands)', min_value=0, value=500, help='Annual income in thousands')
        coapplicant_income = st.number_input('Coapplicant Income (in thousands)', min_value=0, value=0, help='Annual income of coapplicant in thousands')
    with col6:
        credit_score = st.number_input('Credit Score', min_value=300, max_value=900, value=700, help='Credit score (300-900)')
        credit_history = st.selectbox('Credit History', [1, 0], format_func=lambda x: 'Good' if x == 1 else 'Bad', help='Credit history status')

    st.markdown('#### 🏠 Loan Details')
    col7, col8, col9 = st.columns(3)
    with col7:
        loan_amount = st.number_input('Loan Amount (in thousands)', min_value=1, value=150, help='Requested loan amount in thousands')
        loan_amount_term = st.number_input('Loan Amount Term (months)', min_value=1, value=360, help='Loan repayment term in months')
    with col8:
        loan_purpose = st.selectbox('Loan Purpose', ['Home', 'Car', 'Education', 'Personal', 'Business', 'Other'], help='Purpose of the loan')
        property_area = st.selectbox('Property Area', [0, 1, 2], format_func=lambda x: ['Rural', 'Semiurban', 'Urban'][x], help='Property area type')
    with col9:
        collateral_value = st.number_input('Collateral Value (in thousands)', min_value=0, value=0, help='Value of collateral (if any) in thousands')

    # --- Application Summary Card (always visible) ---
    st.markdown(
        f"""
        <div style='background-color:#e3f2fd; padding:1.2em; border-radius:12px; border: 1px solid #90caf9; font-family:Segoe UI,Arial,sans-serif; color:#0d47a1; font-size:1.1em;'>
        <b>Application Summary</b><br><br>
        <b>Age:</b> {age} &nbsp; <b>Gender:</b> {'Male' if gender == 1 else 'Female'} &nbsp; <b>Marital Status:</b> {'Married' if married == 1 else 'Single'}<br>
        <b>Dependents:</b> {dependents} &nbsp; <b>Education:</b> {'Graduate' if education == 0 else 'Not Graduate'}<br>
        <b>Employment Type:</b> {employment_type} &nbsp; <b>Years at Job:</b> {years_at_job}<br>
        <b>Annual Income:</b> {annual_income}k &nbsp; <b>Coapplicant Income:</b> {coapplicant_income}k<br>
        <b>Credit Score:</b> {credit_score} &nbsp; <b>Credit History:</b> {'Good' if credit_history == 1 else 'Bad'}<br>
        <b>Loan Amount:</b> {loan_amount}k &nbsp; <b>Term:</b> {loan_amount_term} months<br>
        <b>Purpose:</b> {loan_purpose} &nbsp; <b>Property Area:</b> {['Rural', 'Semiurban', 'Urban'][property_area]}<br>
        <b>Collateral Value:</b> {collateral_value}k
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Validation Feedback ---
    warnings = []
    if credit_score < 650:
        warnings.append('⚠️ Credit score is below 650.')
    if annual_income < 200:
        warnings.append('⚠️ Annual income is quite low.')
    if loan_amount > annual_income * 0.6:
        warnings.append('⚠️ Loan amount is high compared to income.')
    if years_at_job < 2:
        warnings.append('⚠️ Less than 2 years at current job.')
    if credit_history == 0:
        warnings.append('⚠️ Bad credit history.')
    if collateral_value < loan_amount * 0.5:
        warnings.append('⚠️ Collateral value is low compared to loan amount.')
    if warnings:
        st.markdown('<div style="color:#d9534f; font-weight:bold;">' + '<br>'.join(warnings) + '</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button('🔍 Predict', use_container_width=True)

# --- Prediction and Results ---
if submitted:
    data = {
        'age': age,
        'gender': 'Male' if gender == 1 else 'Female',
        'married': 'Yes' if married == 1 else 'No',
        'dependents': dependents,
        'education': 'Graduate' if education == 0 else 'Not Graduate',
        'employment_type': employment_type,
        'years_at_job': years_at_job,
        'annual_income': annual_income,
        'coapplicant_income': coapplicant_income,
        'credit_score': credit_score,
        'credit_history': 'Good' if credit_history == 1 else 'Bad',
        'loan_amount': loan_amount,
        'loan_amount_term': loan_amount_term,
        'loan_purpose': loan_purpose,
        'property_area': ['Rural', 'Semiurban', 'Urban'][property_area],
        'collateral_value': collateral_value
    }
    with st.spinner('Analyzing your application with AI...'):
        try:
            response = requests.post('http://localhost:5000/predict', json=data)
            result_data = response.json()
            
            if 'error' in result_data:
                st.error(f'Backend Error: {result_data["error"]}')
            else:
                result = result_data.get('prediction', 'Unknown')
                
                if result == 'Approved':
                    st.success('✅ Loan Approved!')
                    
                    # Display bank summary
                    if 'bank_summary' in result_data:
                        bank_summary = result_data['bank_summary']
                        st.markdown(
                            f"""
                            <div style='background-color:#e8f5e9; padding:1.5em; border-radius:12px; border: 2px solid #4caf50; font-family:Segoe UI,Arial,sans-serif; color:#2e7d32; font-size:1.1em;'>
                            <h3 style='color:#2e7d32; margin-top:0;'>🏦 Bank Approval Summary</h3>
                            <div style='display:grid; grid-template-columns: 1fr 1fr; gap:1em; margin-top:1em;'>
                                <div><b>Interest Rate:</b> {bank_summary['Interest Rate (%)']}% per annum</div>
                                <div><b>EMI:</b> ₹{bank_summary['EMI (per month)']:,.2f} per month</div>
                                <div><b>Loan Amount:</b> ₹{bank_summary['Loan Amount']:,.2f}</div>
                                <div><b>Loan Term:</b> {bank_summary['Loan Term (months)']} months</div>
                                <div><b>Total Payment:</b> ₹{bank_summary['Total Payment']:,.2f}</div>
                            </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # Display message if available
                    if 'message' in result_data:
                        st.info(result_data['message'])
                        
                else:
                    st.error('❌ Loan Rejected')
                    
                    # Display rejection reasons
                    if 'reasons' in result_data:
                        st.markdown('**Reasons for rejection:**')
                        for reason in result_data['reasons']:
                            st.warning(reason)
                
                # Display SHAP explanations if available
                if 'shap_reasons' in result_data:
                    st.markdown('**Top AI-based reasons:**')
                    for reason in result_data['shap_reasons']:
                        # Parse the feature and value for user-friendly display
                        import re
                        m = re.match(r"(\w+) \((.*?)\) (increased|decreased) the approval probability", reason)
                        if m:
                            feature, value, direction = m.groups()
                            st.markdown(f"<div style='background-color:{'#e8f5e9' if direction=='increased' else '#ffebee'}; color:{'#388e3c' if direction=='increased' else '#c62828'}; padding:0.7em; border-radius:8px; margin-bottom:0.5em; font-size:1em;'><b>{readable_feature(feature, value)}</b><br>{'Increased' if direction=='increased' else 'Decreased'} the approval probability</div>", unsafe_allow_html=True)
                        else:
                            st.info(reason)
                            
        except Exception as e:
            st.error(f'Error: {e}')

st.markdown('---')
st.markdown('<center><small>Powered by AI | Built with Streamlit</small></center>', unsafe_allow_html=True) 