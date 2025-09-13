import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
import re

def format_drug_info(drug_info: Dict) -> str:
    """Format drug information for display"""
    if not drug_info:
        return "No drug information available"
    
    formatted = f"""
    **Drug Name:** {drug_info.get('name', 'Unknown')}
    **Generic Name:** {drug_info.get('generic_name', 'N/A')}
    **Therapeutic Class:** {drug_info.get('therapeutic_class', 'N/A')}
    **Standard Dosage:** {drug_info.get('standard_dosage', 'N/A')}
    **Mechanism:** {drug_info.get('mechanism', 'N/A')}
    """
    
    return formatted.strip()

def create_safety_chart(recommendation: Dict) -> go.Figure:
    """Create safety score visualization"""
    safety_score = recommendation.get('safety_score', 85)
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = safety_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Safety Score"},
        delta = {'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 70], 'color': "orange"},
                {'range': [70, 85], 'color': "yellow"},
                {'range': [85, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def create_interaction_severity_chart(interactions: List[Dict]) -> go.Figure:
    """Create chart showing interaction severity distribution"""
    if not interactions:
        # Empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No interactions found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    # Count severities
    severity_counts = {}
    for interaction in interactions:
        severity = interaction.get('severity', 'Unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Create pie chart
    fig = px.pie(
        values=list(severity_counts.values()),
        names=list(severity_counts.keys()),
        title="Drug Interaction Severity Distribution",
        color_discrete_map={
            'High': '#FF4444',
            'Moderate': '#FFA500', 
            'Low': '#FFFF00',
            'Minimal': '#90EE90'
        }
    )
    
    fig.update_layout(height=400)
    return fig

def create_drug_timeline_chart(drugs: List[Dict]) -> go.Figure:
    """Create timeline chart for drug administration"""
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set3
    
    for i, drug in enumerate(drugs):
        drug_name = drug.get('name', f'Drug {i+1}')
        frequency = drug.get('frequency', 'Once daily')
        
        # Parse frequency to number
        freq_num = parse_frequency_to_number(frequency)
        
        # Create timeline bars
        y_pos = i
        for j in range(freq_num):
            x_start = j * (24 / freq_num)
            x_end = x_start + 1  # 1 hour duration
            
            fig.add_trace(go.Scatter(
                x=[x_start, x_end, x_end, x_start, x_start],
                y=[y_pos-0.3, y_pos-0.3, y_pos+0.3, y_pos+0.3, y_pos-0.3],
                fill='toself',
                fillcolor=colors[i % len(colors)],
                line=dict(color=colors[i % len(colors)]),
                name=drug_name,
                showlegend=(j == 0),  # Only show legend for first occurrence
                hovertemplate=f"<b>{drug_name}</b><br>Time: %{{x:.0f}}:00<br>Dosage: {drug.get('dosage', 'N/A')}<extra></extra>"
            ))
    
    fig.update_layout(
        title="Daily Drug Administration Schedule",
        xaxis_title="Time of Day (Hours)",
        yaxis_title="Medications",
        xaxis=dict(range=[0, 24], tickmode='linear', tick0=0, dtick=4),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(drugs))),
            ticktext=[drug.get('name', f'Drug {i+1}') for i, drug in enumerate(drugs)]
        ),
        height=max(300, len(drugs) * 80),
        hovermode='closest'
    )
    
    return fig

def parse_frequency_to_number(frequency_str: str) -> int:
    """Parse frequency string to number of times per day"""
    frequency_str = frequency_str.lower()
    
    frequency_map = {
        'once': 1, 'daily': 1, 'qd': 1, '1 time': 1,
        'twice': 2, 'bid': 2, '2 times': 2,
        'three times': 3, 'tid': 3, '3 times': 3,
        'four times': 4, 'qid': 4, '4 times': 4
    }
    
    for key, value in frequency_map.items():
        if key in frequency_str:
            return value
    
    # Try to extract number
    match = re.search(r'(\d+)', frequency_str)
    if match:
        return int(match.group(1))
    
    return 1  # Default to once daily

def validate_input(input_str: str, input_type: str = 'general') -> Dict[str, Any]:
    """Validate user input and return validation results"""
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'cleaned_input': input_str.strip()
    }
    
    if not input_str or not input_str.strip():
        validation_result['is_valid'] = False
        validation_result['errors'].append("Input cannot be empty")
        return validation_result
    
    if input_type == 'drug_name':
        # Validate drug name
        if len(input_str) < 2:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Drug name must be at least 2 characters long")
        
        # Check for potentially harmful characters
        if re.search(r'[<>"\']', input_str):
            validation_result['warnings'].append("Special characters detected in drug name")
        
        # Clean up drug name
        validation_result['cleaned_input'] = re.sub(r'[^\w\s-]', '', input_str).strip()
    
    elif input_type == 'prescription_text':
        # Validate prescription text
        if len(input_str) < 10:
            validation_result['warnings'].append("Prescription text seems very short")
        
        # Check for common prescription elements
        has_drug = bool(re.search(r'\b(mg|g|ml|mcg|tablet|capsule|dose)\b', input_str, re.IGNORECASE))
        has_frequency = bool(re.search(r'\b(daily|twice|once|bid|tid|qid)\b', input_str, re.IGNORECASE))
        
        if not has_drug:
            validation_result['warnings'].append("No clear drug dosage information detected")
        if not has_frequency:
            validation_result['warnings'].append("No clear frequency information detected")
    
    elif input_type == 'patient_age':
        try:
            age = int(input_str)
            if age < 0 or age > 150:
                validation_result['is_valid'] = False
                validation_result['errors'].append("Age must be between 0 and 150")
            elif age < 1:
                validation_result['warnings'].append("Infant - special pediatric considerations apply")
            elif age > 90:
                validation_result['warnings'].append("Very elderly patient - extra caution required")
        except ValueError:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Age must be a valid number")
    
    return validation_result

def format_recommendation_summary(recommendations: List[Dict]) -> str:
    """Format recommendations into a readable summary"""
    if not recommendations:
        return "No specific recommendations available."
    
    summary_parts = []
    
    warnings = [r['message'] for r in recommendations if r['type'] == 'warning']
    infos = [r['message'] for r in recommendations if r['type'] == 'info']
    successes = [r['message'] for r in recommendations if r['type'] == 'success']
    
    if warnings:
        summary_parts.append("**⚠️ Warnings:**")
        for warning in warnings:
            summary_parts.append(f"• {warning}")
    
    if infos:
        summary_parts.append("**ℹ️ Information:**")
        for info in infos:
            summary_parts.append(f"• {info}")
    
    if successes:
        summary_parts.append("**✅ Positive Findings:**")
        for success in successes:
            summary_parts.append(f"• {success}")
    
    return "\n".join(summary_parts)

def calculate_drug_load_score(drugs: List[Dict]) -> Dict[str, Any]:
    """Calculate overall drug load and complexity score"""
    if not drugs:
        return {'score': 0, 'risk_level': 'None', 'factors': []}
    
    base_score = len(drugs) * 10  # Base score per drug
    risk_factors = []
    
    # Count high-risk drugs
    high_risk_classes = ['anticoagulant', 'antipsychotic', 'opioid', 'benzodiazepine']
    high_risk_count = 0
    
    for drug in drugs:
        drug_name = drug.get('name', '').lower()
        for risk_class in high_risk_classes:
            if risk_class in drug_name:
                high_risk_count += 1
                base_score += 15
                break
    
    if high_risk_count > 0:
        risk_factors.append(f"{high_risk_count} high-risk medication(s)")
    
    # Multiple doses per day complexity
    complex_dosing = sum(1 for drug in drugs if 
                        parse_frequency_to_number(drug.get('frequency', '')) > 2)
    if complex_dosing > 0:
        base_score += complex_dosing * 5
        risk_factors.append(f"{complex_dosing} medication(s) with complex dosing")
    
    # Determine risk level
    if base_score < 30:
        risk_level = 'Low'
    elif base_score < 60:
        risk_level = 'Moderate'
    elif base_score < 90:
        risk_level = 'High'
    else:
        risk_level = 'Critical'
    
    return {
        'score': base_score,
        'risk_level': risk_level,
        'factors': risk_factors,
        'total_drugs': len(drugs),
        'high_risk_drugs': high_risk_count,
        'complex_dosing_drugs': complex_dosing
    }

def generate_medication_report(analysis_results: Dict) -> str:
    """Generate a comprehensive medication analysis report"""
    if not analysis_results:
        return "No analysis results available."
    
    report_sections = []
    
    # Header
    report_sections.append("# 📋 MEDICATION ANALYSIS REPORT")
    report_sections.append("=" * 50)
    
    # Summary
    total_drugs = analysis_results.get('total_drugs', 0)
    interactions = analysis_results.get('interactions', [])
    safety_score = analysis_results.get('overall_safety_score', 0)
    
    report_sections.append(f"**Total Medications:** {total_drugs}")
    report_sections.append(f"**Drug Interactions:** {len(interactions)}")
    report_sections.append(f"**Overall Safety Score:** {safety_score}/100")
    
    # Risk Assessment
    report_sections.append("\n## 🔍 RISK ASSESSMENT")
    if safety_score >= 80:
        report_sections.append("✅ **LOW RISK** - Prescription appears safe with minimal concerns")
    elif safety_score >= 60:
        report_sections.append("⚠️ **MODERATE RISK** - Some concerns identified, monitoring recommended")
    else:
        report_sections.append("🚨 **HIGH RISK** - Significant safety concerns require immediate attention")
    
    # Interactions
    if interactions:
        report_sections.append("\n## ⚠️ DRUG INTERACTIONS")
        for interaction in interactions[:5]:  # Show top 5
            report_sections.append(f"• **{interaction['drug1']} ↔ {interaction['drug2']}** ({interaction['severity']})")
            report_sections.append(f"  {interaction['description']}")
    
    # Recommendations
    recommendations = analysis_results.get('recommendations', [])
    if recommendations:
        report_sections.append("\n## 📋 RECOMMENDATIONS")
        for rec in recommendations:
            icon = {'warning': '⚠️', 'info': 'ℹ️', 'success': '✅'}.get(rec['type'], '•')
            report_sections.append(f"{icon} {rec['message']}")
    
    report_sections.append("\n" + "=" * 50)
    report_sections.append("*Report generated by AI Medical Prescription Verification System*")
    
    return "\n".join(report_sections)
