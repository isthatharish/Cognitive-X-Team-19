import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image


# Load environment variables from .env
load_dotenv()

# Access Hugging Face API token
HF_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

import sys

# Import custom modules
from drug_database import DrugDatabase
from nlp_processor import NLPProcessor
from interaction_checker import InteractionChecker
from dosage_recommender import DosageRecommender
from alternative_finder import AlternativeFinder
from patient_profile import PatientProfile
from utils import format_drug_info, create_safety_chart, validate_input
from init_database import initialize_database

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.patient_profile = None
    st.session_state.analysis_results = None

# Page configuration
st.set_page_config(
    page_title="AI Medical Prescription Verification",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_system():
    """Initialize all system components"""
    if not st.session_state.initialized:
        with st.spinner("Initializing AI Medical Prescription Verification System..."):
            try:
                # Initialize database
                initialize_database()
                
                # Initialize components
                st.session_state.db = DrugDatabase()
                st.session_state.nlp = NLPProcessor()
                st.session_state.interaction_checker = InteractionChecker(st.session_state.db)
                st.session_state.dosage_recommender = DosageRecommender(st.session_state.db)
                st.session_state.alternative_finder = AlternativeFinder(st.session_state.db)
                
                st.session_state.initialized = True
                st.success("System initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize system: {str(e)}")
                return False
    return True

def main():
    # Initialize system
    if not initialize_system():
        return
    
    # Header
    st.title("🏥 AI Medical Prescription Verification System")
    st.markdown("---")
    st.markdown("*Powered by IBM Granite Models for Advanced Drug Analysis*")
    
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
                st.session_state.patient_profile = PatientProfile(
                    name=patient_name,
                    age=patient_age,
                    weight=patient_weight,
                    conditions=conditions,
                    allergies=[a.strip() for a in allergies.split(",") if a.strip()]
                )
                st.success("Patient profile updated!")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Prescription Analysis", 
        "🔍 Drug Interactions", 
        "💊 Dosage Recommendations",
        "🔄 Alternative Medications",
        "📊 Analysis Dashboard"
    ])
    
    with tab1:
        prescription_analysis_tab()
    
    with tab2:
        drug_interaction_tab()
    
    with tab3:
        dosage_recommendation_tab()
    
    with tab4:
        alternative_medication_tab()
    
    with tab5:
        dashboard_tab()

def prescription_analysis_tab():
    """Tab for analyzing prescription text using NLP"""
    st.header("📝 Prescription Text Analysis")
    st.markdown("Extract structured drug information from unstructured medical text using IBM Granite models.")
    
    # Input methods
    input_method = st.radio(
        "Choose input method:",
        ["Text Input", "File Upload"]
    )
    
    prescription_text = ""
    
    if input_method == "Text Input":
        prescription_text = st.text_area(
            "Enter prescription text:",
            placeholder="Patient should take Metformin 500mg twice daily with meals, Lisinopril 10mg once daily in the morning...",
            height=150
        )
    
    else:  # File Upload
        uploaded_file = st.file_uploader(
            "Upload prescription file:",
            type=['txt', 'pdf', 'docx']
        )
        if uploaded_file is not None:
            # Handle different file types
            if uploaded_file.type == "text/plain":
                prescription_text = str(uploaded_file.read(), "utf-8")
            else:
                st.warning("Currently only text files are supported.")
    
    if st.button("🔍 Analyze Prescription", type="primary") and prescription_text:
        with st.spinner("Analyzing prescription text with IBM Granite models..."):
            try:
                # Process text with NLP
                extracted_drugs = st.session_state.nlp.extract_drug_information(prescription_text)
                
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
                                st.metric("Confidence", f"{drug.get('confidence', 0.9):.2f}")
                    
                    # Store results for other tabs
                    st.session_state.extracted_drugs = extracted_drugs
                    
                    # Show comprehensive analysis button
                    if st.button("🔄 Run Comprehensive Analysis", type="secondary"):
                        run_comprehensive_analysis(extracted_drugs)
                
                else:
                    st.warning("No drugs could be extracted from the text. Please check the format.")
                    
            except Exception as e:
                st.error(f"Error analyzing prescription: {str(e)}")

def drug_interaction_tab():
    """Tab for drug interaction detection"""
    st.header("🔍 Drug Interaction Detection")
    st.markdown("Check for potentially harmful interactions between medications.")
    
    # Manual drug entry
    st.subheader("Enter Medications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Current medications
        if 'current_drugs' not in st.session_state:
            st.session_state.current_drugs = []
        
        new_drug = st.text_input("Add medication:")
        if st.button("➕ Add Drug") and new_drug:
            if new_drug not in st.session_state.current_drugs:
                st.session_state.current_drugs.append(new_drug)
                st.rerun()
    
    with col2:
        # Display current drug list
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
            try:
                interactions = st.session_state.interaction_checker.check_interactions(drug_names)
                
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
                    
            except Exception as e:
                st.error(f"Error checking interactions: {str(e)}")
    
    elif len(drug_names) < 2:
        st.info("Please add at least 2 medications to check for interactions.")

def dosage_recommendation_tab():
    """Tab for age-specific dosage recommendations"""
    st.header("💊 Age-Specific Dosage Recommendations")
    st.markdown("Get personalized dosage recommendations based on patient profile.")
    
    if not st.session_state.patient_profile:
        st.warning("Please create a patient profile in the sidebar first.")
        return
    
    # Drug selection for dosage check
    drug_name = st.text_input("Enter drug name for dosage recommendation:")
    indication = st.selectbox(
        "Medical indication:",
        ["Hypertension", "Diabetes", "Infection", "Pain Management", "Other"]
    )
    
    if st.button("💊 Get Dosage Recommendation", type="primary") and drug_name:
        with st.spinner("Calculating personalized dosage..."):
            try:
                recommendation = st.session_state.dosage_recommender.get_recommendation(
                    drug_name, 
                    st.session_state.patient_profile,
                    indication
                )
                
                if recommendation:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Recommended Dose", recommendation['dosage'])
                        st.metric("Frequency", recommendation['frequency'])
                    
                    with col2:
                        st.metric("Route", recommendation['route'])
                        st.metric("Duration", recommendation.get('duration', 'As needed'))
                    
                    with col3:
                        safety_score = recommendation.get('safety_score', 85)
                        st.metric("Safety Score", f"{safety_score}/100")
                    
                    # Safety considerations
                    st.subheader("🛡️ Safety Considerations")
                    
                    if recommendation.get('warnings'):
                        for warning in recommendation['warnings']:
                            st.warning(f"⚠️ {warning}")
                    
                    if recommendation.get('monitoring'):
                        st.info(f"📊 Monitoring: {recommendation['monitoring']}")
                    
                    # Age-specific adjustments
                    if recommendation.get('age_adjustments'):
                        st.subheader("👶👴 Age-Specific Adjustments")
                        st.write(recommendation['age_adjustments'])
                    
                    # Visualization
                    fig = create_safety_chart(recommendation)
                    st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.error("Unable to find dosage information for this drug.")
                    
            except Exception as e:
                st.error(f"Error getting dosage recommendation: {str(e)}")

def alternative_medication_tab():
    """Tab for finding alternative medications"""
    st.header("🔄 Alternative Medication Suggestions")
    st.markdown("Find safer or equivalent medications when contraindications exist.")
    
    if not st.session_state.patient_profile:
        st.warning("Please create a patient profile in the sidebar first.")
        return
    
    # Input for problematic drug
    problematic_drug = st.text_input("Enter problematic medication:")
    reason = st.selectbox(
        "Reason for finding alternative:",
        ["Drug Interaction", "Allergy", "Contraindication", "Side Effects", "Cost", "Availability"]
    )
    
    therapeutic_class = st.selectbox(
        "Therapeutic class (optional):",
        ["", "Antihypertensive", "Antidiabetic", "Antibiotic", "Analgesic", "Antidepressant", "Other"]
    )
    
    if st.button("🔍 Find Alternatives", type="primary") and problematic_drug:
        with st.spinner("Searching for alternative medications..."):
            try:
                alternatives = st.session_state.alternative_finder.find_alternatives(
                    problematic_drug,
                    st.session_state.patient_profile,
                    reason,
                    therapeutic_class
                )
                
                if alternatives:
                    st.success(f"Found {len(alternatives)} alternative(s)")
                    
                    for i, alt in enumerate(alternatives):
                        with st.expander(f"Alternative {i+1}: {alt['name']}", expanded=i < 3):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Drug Name", alt['name'])
                                st.metric("Similarity Score", f"{alt['similarity_score']:.2f}")
                            
                            with col2:
                                st.metric("Safety Rating", f"{alt['safety_rating']}/5")
                                st.metric("Cost Comparison", alt.get('cost_comparison', 'Similar'))
                            
                            with col3:
                                st.write("**Mechanism:**")
                                st.write(alt.get('mechanism', 'Not specified'))
                            
                            # Advantages and considerations
                            if alt.get('advantages'):
                                st.write("**✅ Advantages:**")
                                for adv in alt['advantages']:
                                    st.write(f"• {adv}")
                            
                            if alt.get('considerations'):
                                st.write("**⚠️ Considerations:**")
                                for cons in alt['considerations']:
                                    st.write(f"• {cons}")
                
                else:
                    st.warning("No suitable alternatives found for this medication.")
                    
            except Exception as e:
                st.error(f"Error finding alternatives: {str(e)}")

def dashboard_tab():
    """Dashboard tab showing comprehensive analysis results"""
    st.header("📊 Analysis Dashboard")
    st.markdown("Comprehensive overview of prescription analysis results.")
    
    if not hasattr(st.session_state, 'analysis_results') or not st.session_state.analysis_results:
        st.info("No analysis results available. Please run prescription analysis first.")
        return
    
    results = st.session_state.analysis_results
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Drugs", results.get('total_drugs', 0))
    
    with col2:
        interactions = results.get('interactions', [])
        st.metric("Interactions Found", len(interactions), delta=f"-{len(interactions)}" if interactions else "0")
    
    with col3:
        high_risk = sum(1 for i in interactions if i.get('severity') == 'High')
        st.metric("High Risk Interactions", high_risk, delta=f"-{high_risk}" if high_risk else "0")
    
    with col4:
        overall_safety = results.get('overall_safety_score', 85)
        st.metric("Overall Safety Score", f"{overall_safety}/100")
    
    # Detailed sections
    if interactions:
        st.subheader("⚠️ Drug Interactions Summary")
        interaction_df = pd.DataFrame(interactions)
        st.dataframe(interaction_df, use_container_width=True)
        
        # Interaction severity chart
        severity_counts = interaction_df['severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index, 
                     title="Interaction Severity Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Drug safety profiles
    if results.get('drug_profiles'):
        st.subheader("💊 Drug Safety Profiles")
        
        drug_data = []
        for drug in results['drug_profiles']:
            drug_data.append({
                'Drug': drug['name'],
                'Safety Score': drug.get('safety_score', 85),
                'Dosage Appropriate': 'Yes' if drug.get('dosage_appropriate', True) else 'No',
                'Age Suitable': 'Yes' if drug.get('age_suitable', True) else 'No'
            })
        
        df = pd.DataFrame(drug_data)
        st.dataframe(df, use_container_width=True)
        
        # Safety score visualization
        fig = px.bar(df, x='Drug', y='Safety Score', 
                     title="Drug Safety Scores",
                     color='Safety Score',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations summary
    if results.get('recommendations'):
        st.subheader("📋 Recommendations Summary")
        for rec in results['recommendations']:
            if rec['type'] == 'warning':
                st.warning(f"⚠️ {rec['message']}")
            elif rec['type'] == 'info':
                st.info(f"ℹ️ {rec['message']}")
            else:
                st.success(f"✅ {rec['message']}")

def run_comprehensive_analysis(extracted_drugs):
    """Run comprehensive analysis on extracted drugs"""
    if not st.session_state.patient_profile:
        st.warning("Patient profile required for comprehensive analysis.")
        return
    
    with st.spinner("Running comprehensive analysis..."):
        try:
            # Check interactions
            drug_names = [drug['name'] for drug in extracted_drugs]
            interactions = st.session_state.interaction_checker.check_interactions(drug_names)
            
            # Get dosage recommendations
            drug_profiles = []
            for drug in extracted_drugs:
                recommendation = st.session_state.dosage_recommender.get_recommendation(
                    drug['name'], 
                    st.session_state.patient_profile,
                    'General'
                )
                
                if recommendation:
                    drug_profiles.append({
                        'name': drug['name'],
                        'extracted_dosage': drug['dosage'],
                        'recommended_dosage': recommendation['dosage'],
                        'safety_score': recommendation.get('safety_score', 85),
                        'dosage_appropriate': drug['dosage'] == recommendation['dosage'],
                        'age_suitable': recommendation.get('age_suitable', True)
                    })
            
            # Calculate overall safety score
            if drug_profiles:
                overall_safety = sum(d['safety_score'] for d in drug_profiles) / len(drug_profiles)
                overall_safety -= len([i for i in interactions if i.get('severity') == 'High']) * 10
                overall_safety = max(0, min(100, overall_safety))
            else:
                overall_safety = 50
            
            # Generate recommendations
            recommendations = []
            if interactions:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Found {len(interactions)} drug interactions requiring attention"
                })
            
            inappropriate_dosages = [d for d in drug_profiles if not d['dosage_appropriate']]
            if inappropriate_dosages:
                recommendations.append({
                    'type': 'warning',
                    'message': f"{len(inappropriate_dosages)} drugs have potentially inappropriate dosages"
                })
            
            if overall_safety >= 80:
                recommendations.append({
                    'type': 'success',
                    'message': "Overall prescription safety profile is good"
                })
            elif overall_safety >= 60:
                recommendations.append({
                    'type': 'info',
                    'message': "Prescription requires monitoring but is generally acceptable"
                })
            else:
                recommendations.append({
                    'type': 'warning',
                    'message': "Prescription has significant safety concerns requiring review"
                })
            
            # Store results
            st.session_state.analysis_results = {
                'total_drugs': len(extracted_drugs),
                'interactions': interactions,
                'drug_profiles': drug_profiles,
                'overall_safety_score': overall_safety,
                'recommendations': recommendations
            }
            
            st.success("✅ Comprehensive analysis completed! Check the Dashboard tab for detailed results.")
            
        except Exception as e:
            st.error(f"Error running comprehensive analysis: {str(e)}")

if __name__ == "__main__":
    main()
