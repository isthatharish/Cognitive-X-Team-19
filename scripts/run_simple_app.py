import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    packages = [
        'streamlit',
        'pandas', 
        'plotly',
        'requests'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")

def create_simple_app():
    """Create a simplified version of the app that works without external APIs"""
    app_content = '''
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import re

# Page configuration
st.set_page_config(
    page_title="AI Medical Prescription Verification",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Header
    st.title("🏥 AI Medical Prescription Verification System")
    st.markdown("---")
    st.markdown("*Demo Version - Powered by Rule-Based Analysis*")
    
    # Sidebar - Patient Profile
    with st.sidebar:
        st.header("👤 Patient Profile")
        
        # Patient information form
        with st.form("patient_form"):
            patient_name = st.text_input("Patient Name")
            patient_age = st.number_input("Age", min_value=0, max_value=150, value=30)
            patient_weight = st.number_input("Weight (kg)", min_value=0.0, max_value=500.0, value=70.0)
            
            # Medical conditions
            st.subheader("Medical Conditions")
            conditions = st.multiselect(
                "Select existing conditions:",
                ["Diabetes", "Hypertension", "Heart Disease", "Kidney Disease", 
                 "Liver Disease", "Asthma", "Allergies", "None"]
            )
            
            # Known allergies
            allergies = st.text_area("Known Drug Allergies (comma-separated)")
            
            submit_profile = st.form_submit_button("Update Patient Profile")
            
            if submit_profile and patient_name:
                st.session_state.patient_profile = {
                    'name': patient_name,
                    'age': patient_age,
                    'weight': patient_weight,
                    'conditions': conditions,
                    'allergies': [a.strip() for a in allergies.split(",") if a.strip()]
                }
                st.success("Patient profile updated!")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs([
        "📝 Prescription Analysis", 
        "🔍 Drug Interactions", 
        "📊 Analysis Dashboard"
    ])
    
    with tab1:
        prescription_analysis_tab()
    
    with tab2:
        drug_interaction_tab()
    
    with tab3:
        dashboard_tab()

def prescription_analysis_tab():
    """Tab for analyzing prescription text"""
    st.header("📝 Prescription Text Analysis")
    st.markdown("Extract drug information from prescription text using pattern matching.")
    
    prescription_text = st.text_area(
        "Enter prescription text:",
        placeholder="Patient should take Metformin 500mg twice daily with meals, Lisinopril 10mg once daily in the morning...",
        height=150
    )
    
    if st.button("🔍 Analyze Prescription", type="primary") and prescription_text:
        with st.spinner("Analyzing prescription text..."):
            extracted_drugs = extract_drug_information(prescription_text)
            
            if extracted_drugs:
                st.success(f"Successfully extracted {len(extracted_drugs)} drug(s)")
                
                # Display extracted information
                for i, drug in enumerate(extracted_drugs):
                    with st.expander(f"Drug {i+1}: {drug['name']}", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Drug Name", drug['name'])
                            st.metric("Dosage", drug['dosage'])
                        
                        with col2:
                            st.metric("Frequency", drug['frequency'])
                            st.metric("Duration", drug.get('duration', 'Not specified'))
                        
                        with col3:
                            st.metric("Instructions", drug.get('instructions', 'Standard'))
                            st.metric("Confidence", f"{drug.get('confidence', 0.8):.2f}")
                
                # Store results for other tabs
                st.session_state.extracted_drugs = extracted_drugs
                
            else:
                st.warning("No drugs could be extracted from the text. Please check the format.")

def extract_drug_information(text):
    """Extract drug information using pattern matching"""
    common_drugs = [
        'metformin', 'lisinopril', 'atorvastatin', 'amlodipine', 'omeprazole',
        'metoprolol', 'losartan', 'simvastatin', 'levothyroxine', 'hydrochlorothiazide',
        'amoxicillin', 'azithromycin', 'doxycycline', 'ciprofloxacin', 'prednisone',
        'ibuprofen', 'acetaminophen', 'aspirin', 'warfarin', 'clopidogrel',
        'insulin', 'furosemide', 'carvedilol', 'gabapentin', 'sertraline'
    ]
    
    drug_patterns = {
        'dosage': r'(\\d+(?:\\.\\d+)?)\\s*(mg|g|ml|mcg|iu|units?)',
        'frequency': r'(once|twice|three times?|four times?|\\d+\\s*times?)\\s*(daily|a day|per day|bid|tid|qid|qd)',
        'duration': r'for\\s+(\\d+)\\s*(days?|weeks?|months?)',
        'instructions': r'(with|without|before|after)\\s+(meals?|food|eating)'
    }
    
    extracted_drugs = []
    sentences = re.split(r'[.;]\\s*', text.lower())
    
    for sentence in sentences:
        for drug in common_drugs:
            if drug in sentence:
                # Extract dosage
                dosage_match = re.search(drug_patterns['dosage'], sentence, re.IGNORECASE)
                dosage = f"{dosage_match.group(1)} {dosage_match.group(2)}" if dosage_match else "Not specified"
                
                # Extract frequency
                frequency_match = re.search(drug_patterns['frequency'], sentence, re.IGNORECASE)
                frequency = frequency_match.group(0) if frequency_match else "As directed"
                
                # Extract duration
                duration_match = re.search(drug_patterns['duration'], sentence, re.IGNORECASE)
                duration = duration_match.group(0) if duration_match else None
                
                # Extract instructions
                instructions_match = re.search(drug_patterns['instructions'], sentence, re.IGNORECASE)
                instructions = instructions_match.group(0) if instructions_match else None
                
                # Calculate confidence
                confidence = 0.6
                if dosage != "Not specified":
                    confidence += 0.2
                if frequency != "As directed":
                    confidence += 0.15
                if duration:
                    confidence += 0.05
                
                drug_info = {
                    'name': drug.title(),
                    'dosage': dosage,
                    'frequency': frequency,
                    'duration': duration,
                    'instructions': instructions,
                    'confidence': min(confidence, 1.0)
                }
                
                # Avoid duplicates
                if not any(d['name'] == drug_info['name'] for d in extracted_drugs):
                    extracted_drugs.append(drug_info)
    
    return extracted_drugs

def drug_interaction_tab():
    """Tab for drug interaction detection"""
    st.header("🔍 Drug Interaction Detection")
    st.markdown("Check for potentially harmful interactions between medications.")
    
    # Manual drug entry
    st.subheader("Enter Medications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'current_drugs' not in st.session_state:
            st.session_state.current_drugs = []
        
        new_drug = st.text_input("Add medication:")
        if st.button("➕ Add Drug") and new_drug:
            if new_drug not in st.session_state.current_drugs:
                st.session_state.current_drugs.append(new_drug)
                st.rerun()
    
    with col2:
        if st.session_state.current_drugs:
            st.write("**Current Medications:**")
            for i, drug in enumerate(st.session_state.current_drugs):
                col_drug, col_remove = st.columns([3, 1])
                with col_drug:
                    st.write(f"• {drug}")
                with col_remove:
                    if st.button("🗑️", key=f"remove_{i}"):
                        st.session_state.current_drugs.remove(drug)
                        st.rerun()
    
    # Use extracted drugs if available
    if hasattr(st.session_state, 'extracted_drugs'):
        st.info("Using drugs from prescription analysis")
        drug_names = [drug['name'] for drug in st.session_state.extracted_drugs]
    else:
        drug_names = st.session_state.current_drugs if st.session_state.current_drugs else []
    
    if st.button("🔍 Check Interactions", type="primary") and len(drug_names) >= 2:
        with st.spinner("Checking drug interactions..."):
            interactions = check_drug_interactions(drug_names)
            
            if interactions:
                st.error(f"⚠️ Found {len(interactions)} potential interaction(s)")
                
                for interaction in interactions:
                    with st.expander(f"⚠️ {interaction['drug1']} ↔ {interaction['drug2']}", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Severity", interaction['severity'])
                            st.metric("Risk Level", interaction['risk_level'])
                        
                        with col2:
                            st.write("**Description:**")
                            st.write(interaction['description'])
                            
                            st.write("**Recommendation:**")
                            st.write(interaction['recommendation'])
            else:
                st.success("✅ No significant interactions detected")
    
    elif len(drug_names) < 2:
        st.info("Please add at least 2 medications to check for interactions.")

def check_drug_interactions(drug_names):
    """Check for drug interactions using predefined patterns"""
    interaction_patterns = {
        'anticoagulants': ['warfarin', 'heparin', 'rivaroxaban', 'apixaban'],
        'antiplatelets': ['aspirin', 'clopidogrel', 'ticagrelor'],
        'ace_inhibitors': ['lisinopril', 'enalapril', 'captopril'],
        'nsaids': ['ibuprofen', 'naproxen', 'diclofenac'],
        'statins': ['atorvastatin', 'simvastatin', 'lovastatin'],
        'beta_blockers': ['metoprolol', 'propranolol', 'atenolol']
    }
    
    interactions = []
    
    # Check for known dangerous combinations
    drug_classes = {}
    for drug in drug_names:
        drug_lower = drug.lower()
        for class_name, drugs in interaction_patterns.items():
            if any(d in drug_lower for d in drugs):
                if class_name not in drug_classes:
                    drug_classes[class_name] = []
                drug_classes[class_name].append(drug)
    
    # Check for high-risk combinations
    if 'anticoagulants' in drug_classes and 'antiplatelets' in drug_classes:
        interactions.append({
            'drug1': drug_classes['anticoagulants'][0],
            'drug2': drug_classes['antiplatelets'][0],
            'severity': 'High',
            'risk_level': 'High',
            'description': 'Increased bleeding risk due to additive anticoagulant effects',
            'recommendation': 'Avoid combination if possible. Monitor for bleeding signs.'
        })
    
    if 'anticoagulants' in drug_classes and 'nsaids' in drug_classes:
        interactions.append({
            'drug1': drug_classes['anticoagulants'][0],
            'drug2': drug_classes['nsaids'][0],
            'severity': 'High',
            'risk_level': 'High',
            'description': 'NSAIDs may increase bleeding risk and reduce anticoagulant effectiveness',
            'recommendation': 'Use alternative pain management. If necessary, monitor INR closely.'
        })
    
    if 'ace_inhibitors' in drug_classes and 'nsaids' in drug_classes:
        interactions.append({
            'drug1': drug_classes['ace_inhibitors'][0],
            'drug2': drug_classes['nsaids'][0],
            'severity': 'Moderate',
            'risk_level': 'Moderate',
            'description': 'NSAIDs may reduce the effectiveness of ACE inhibitors',
            'recommendation': 'Monitor blood pressure and kidney function.'
        })
    
    return interactions

def dashboard_tab():
    """Dashboard tab showing analysis results"""
    st.header("📊 Analysis Dashboard")
    st.markdown("Comprehensive overview of prescription analysis results.")
    
    if not hasattr(st.session_state, 'extracted_drugs'):
        st.info("No analysis results available. Please run prescription analysis first.")
        return
    
    drugs = st.session_state.extracted_drugs
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Drugs", len(drugs))
    
    with col2:
        drug_names = [drug['name'] for drug in drugs]
        interactions = check_drug_interactions(drug_names) if len(drug_names) >= 2 else []
        st.metric("Interactions Found", len(interactions))
    
    with col3:
        high_risk = sum(1 for i in interactions if i.get('severity') == 'High')
        st.metric("High Risk Interactions", high_risk)
    
    with col4:
        avg_confidence = sum(drug.get('confidence', 0.8) for drug in drugs) / len(drugs) if drugs else 0
        st.metric("Avg Confidence", f"{avg_confidence:.2f}")
    
    # Drug list
    if drugs:
        st.subheader("💊 Extracted Medications")
        
        drug_data = []
        for drug in drugs:
            drug_data.append({
                'Drug': drug['name'],
                'Dosage': drug['dosage'],
                'Frequency': drug['frequency'],
                'Confidence': f"{drug.get('confidence', 0.8):.2f}"
            })
        
        df = pd.DataFrame(drug_data)
        st.dataframe(df, use_container_width=True)
        
        # Confidence chart
        fig = px.bar(df, x='Drug', y='Confidence', 
                     title="Drug Extraction Confidence Scores",
                     color='Confidence',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    # Interactions summary
    if interactions:
        st.subheader("⚠️ Drug Interactions Summary")
        interaction_df = pd.DataFrame(interactions)
        st.dataframe(interaction_df[['drug1', 'drug2', 'severity', 'description']], use_container_width=True)

if __name__ == "__main__":
    print("🚀 Starting Medication Safety Application...")
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'simple_app.py', '--server.port=8501'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run app: {e}")
    except KeyboardInterrupt:
        print("\\n👋 Application stopped by user")
