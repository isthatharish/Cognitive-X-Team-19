from typing import List, Dict, Tuple, Optional
import itertools
from drug_database import DrugDatabase

class InteractionChecker:
    """Checks for drug-drug interactions and provides safety assessments"""
    
    def __init__(self, drug_database: DrugDatabase):
        self.db = drug_database
        
        # Common interaction patterns (expanded for comprehensive checking)
        self.interaction_patterns = {
            'cyp450_inhibitors': [
                'ciprofloxacin', 'fluconazole', 'clarithromycin', 'erythromycin',
                'ketoconazole', 'omeprazole', 'fluvoxamine'
            ],
            'cyp450_inducers': [
                'rifampin', 'carbamazepine', 'phenytoin', 'phenobarbital',
                'st johns wort', 'modafinil'
            ],
            'anticoagulants': [
                'warfarin', 'heparin', 'rivaroxaban', 'apixaban', 'dabigatran'
            ],
            'antiplatelets': [
                'aspirin', 'clopidogrel', 'ticagrelor', 'prasugrel'
            ],
            'ace_inhibitors': [
                'lisinopril', 'enalapril', 'captopril', 'ramipril'
            ],
            'arbs': [
                'losartan', 'valsartan', 'irbesartan', 'olmesartan'
            ],
            'diuretics': [
                'furosemide', 'hydrochlorothiazide', 'spironolactone', 'amiloride'
            ],
            'beta_blockers': [
                'metoprolol', 'propranolol', 'atenolol', 'carvedilol'
            ],
            'statins': [
                'atorvastatin', 'simvastatin', 'lovastatin', 'rosuvastatin'
            ],
            'nsaids': [
                'ibuprofen', 'naproxen', 'diclofenac', 'celecoxib'
            ],
            'antidepressants_ssri': [
                'sertraline', 'fluoxetine', 'paroxetine', 'citalopram'
            ],
            'antidepressants_snri': [
                'venlafaxine', 'duloxetine', 'desvenlafaxine'
            ],
            'benzodiazepines': [
                'lorazepam', 'alprazolam', 'clonazepam', 'diazepam'
            ],
            'opioids': [
                'morphine', 'oxycodone', 'hydrocodone', 'tramadol', 'codeine'
            ]
        }
    
    def check_interactions(self, drug_names: List[str]) -> List[Dict]:
        """Check for interactions between a list of drugs"""
        interactions = []
        
        try:
            # Get all possible drug pairs
            drug_pairs = list(itertools.combinations(drug_names, 2))
            
            for drug1, drug2 in drug_pairs:
                # Check database first
                db_interaction = self.db.get_drug_interactions(drug1, drug2)
                if db_interaction:
                    interactions.append(db_interaction)
                else:
                    # Check pattern-based interactions
                    pattern_interaction = self._check_pattern_interactions(drug1, drug2)
                    if pattern_interaction:
                        interactions.append(pattern_interaction)
            
            # Sort by severity
            interactions.sort(key=lambda x: self._get_severity_weight(x['severity']), reverse=True)
            
            return interactions
            
        except Exception as e:
            print(f"Error checking interactions: {str(e)}")
            return []
    
    def _check_pattern_interactions(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Check for interactions based on drug class patterns"""
        try:
            drug1_lower = drug1.lower()
            drug2_lower = drug2.lower()
            
            # Get drug classes for both drugs
            drug1_classes = self._get_drug_classes(drug1_lower)
            drug2_classes = self._get_drug_classes(drug2_lower)
            
            # Check for known dangerous combinations
            interaction = self._evaluate_class_interactions(
                drug1, drug2, drug1_classes, drug2_classes
            )
            
            return interaction
            
        except Exception as e:
            print(f"Error checking pattern interactions: {str(e)}")
            return None
    
    def _get_drug_classes(self, drug_name: str) -> List[str]:
        """Identify drug classes for a given drug"""
        classes = []
        
        for class_name, drugs in self.interaction_patterns.items():
            if any(drug in drug_name for drug in drugs):
                classes.append(class_name)
        
        return classes
    
    def _evaluate_class_interactions(self, drug1: str, drug2: str, 
                                   classes1: List[str], classes2: List[str]) -> Optional[Dict]:
        """Evaluate interactions between drug classes"""
        
        # High-risk interactions
        high_risk_combinations = [
            (['anticoagulants'], ['antiplatelets']),
            (['anticoagulants'], ['nsaids']),
            (['ace_inhibitors', 'arbs'], ['diuretics']),
            (['cyp450_inhibitors'], ['statins']),
            (['antidepressants_ssri', 'antidepressants_snri'], ['opioids']),
            (['benzodiazepines'], ['opioids']),
            (['beta_blockers'], ['diuretics'])
        ]
        
        # Medium-risk interactions
        medium_risk_combinations = [
            (['cyp450_inhibitors'], ['beta_blockers']),
            (['nsaids'], ['diuretics']),
            (['ace_inhibitors'], ['nsaids']),
            (['statins'], ['antidepressants_ssri'])
        ]
        
        # Check high-risk combinations
        for combo in high_risk_combinations:
            if (any(cls in classes1 for cls in combo[0]) and 
                any(cls in classes2 for cls in combo[1])) or \
               (any(cls in classes1 for cls in combo[1]) and 
                any(cls in classes2 for cls in combo[0])):
                
                return self._create_interaction_dict(drug1, drug2, 'High', combo)
        
        # Check medium-risk combinations
        for combo in medium_risk_combinations:
            if (any(cls in classes1 for cls in combo[0]) and 
                any(cls in classes2 for cls in combo[1])) or \
               (any(cls in classes1 for cls in combo[1]) and 
                any(cls in classes2 for cls in combo[0])):
                
                return self._create_interaction_dict(drug1, drug2, 'Moderate', combo)
        
        return None
    
    def _create_interaction_dict(self, drug1: str, drug2: str, severity: str, 
                               combo: Tuple) -> Dict:
        """Create standardized interaction dictionary"""
        
        # Generate description based on drug classes involved
        descriptions = {
            ('anticoagulants', 'antiplatelets'): 'Increased bleeding risk due to additive anticoagulant effects',
            ('anticoagulants', 'nsaids'): 'NSAIDs may increase bleeding risk and reduce anticoagulant effectiveness',
            ('ace_inhibitors', 'diuretics'): 'Risk of hypotension and hyperkalemia',
            ('cyp450_inhibitors', 'statins'): 'Increased statin levels may lead to muscle toxicity',
            ('antidepressants_ssri', 'opioids'): 'Risk of serotonin syndrome and CNS depression',
            ('benzodiazepines', 'opioids'): 'Dangerous CNS depression and respiratory depression',
            ('beta_blockers', 'diuretics'): 'Risk of hypotension and electrolyte imbalances'
        }
        
        # Generate recommendation based on severity
        recommendations = {
            'High': 'Avoid combination if possible. If necessary, use with extreme caution and close monitoring.',
            'Moderate': 'Use caution. Monitor patient closely for adverse effects.',
            'Low': 'Monitor patient. Interaction is generally manageable with appropriate precautions.'
        }
        
        # Find matching description
        description = "Potential interaction between drug classes"
        for key, desc in descriptions.items():
            if (key[0] in str(combo[0]) and key[1] in str(combo[1])) or \
               (key[1] in str(combo[0]) and key[0] in str(combo[1])):
                description = desc
                break
        
        return {
            'drug1': drug1,
            'drug2': drug2,
            'severity': severity,
            'risk_level': severity,
            'mechanism': f'Interaction between {combo[0]} and {combo[1]}',
            'description': description,
            'clinical_significance': f'{severity} clinical significance',
            'recommendation': recommendations.get(severity, recommendations['Moderate']),
            'monitoring_required': severity in ['High', 'Moderate']
        }
    
    def _get_severity_weight(self, severity: str) -> int:
        """Get numeric weight for severity ordering"""
        severity_weights = {
            'High': 3,
            'Moderate': 2,
            'Low': 1,
            'Minimal': 0
        }
        return severity_weights.get(severity, 1)
    
    def assess_overall_interaction_risk(self, interactions: List[Dict]) -> Dict:
        """Assess overall interaction risk for a drug combination"""
        if not interactions:
            return {
                'risk_level': 'Low',
                'risk_score': 10,
                'summary': 'No significant interactions detected',
                'recommendations': ['Continue monitoring patient as standard practice']
            }
        
        # Calculate risk score
        risk_score = 100
        high_risk_count = 0
        moderate_risk_count = 0
        
        for interaction in interactions:
            if interaction['severity'] == 'High':
                risk_score -= 30
                high_risk_count += 1
            elif interaction['severity'] == 'Moderate':
                risk_score -= 15
                moderate_risk_count += 1
            elif interaction['severity'] == 'Low':
                risk_score -= 5
        
        risk_score = max(0, risk_score)
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = 'Low'
        elif risk_score >= 60:
            risk_level = 'Moderate'
        elif risk_score >= 40:
            risk_level = 'High'
        else:
            risk_level = 'Critical'
        
        # Generate summary
        summary_parts = []
        if high_risk_count > 0:
            summary_parts.append(f"{high_risk_count} high-risk interaction(s)")
        if moderate_risk_count > 0:
            summary_parts.append(f"{moderate_risk_count} moderate-risk interaction(s)")
        
        summary = f"Found {', '.join(summary_parts)}" if summary_parts else "Minimal interactions"
        
        # Generate recommendations
        recommendations = []
        if high_risk_count > 0:
            recommendations.append("Consider alternative medications for high-risk interactions")
            recommendations.append("Implement intensive monitoring protocols")
        if moderate_risk_count > 0:
            recommendations.append("Monitor patient for interaction-related adverse effects")
        if risk_level in ['High', 'Critical']:
            recommendations.append("Consult with pharmacist or specialist")
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'summary': summary,
            'recommendations': recommendations,
            'high_risk_interactions': high_risk_count,
            'moderate_risk_interactions': moderate_risk_count,
            'total_interactions': len(interactions)
        }
    
    def get_interaction_monitoring_plan(self, interactions: List[Dict]) -> Dict:
        """Generate monitoring plan for drug interactions"""
        monitoring_plan = {
            'laboratory_monitoring': [],
            'clinical_monitoring': [],
            'frequency': 'Standard',
            'duration': 'Throughout treatment'
        }
        
        for interaction in interactions:
            if 'anticoagulant' in interaction.get('mechanism', '').lower():
                if 'PT/INR monitoring' not in monitoring_plan['laboratory_monitoring']:
                    monitoring_plan['laboratory_monitoring'].append('PT/INR monitoring')
                if 'Bleeding assessment' not in monitoring_plan['clinical_monitoring']:
                    monitoring_plan['clinical_monitoring'].append('Bleeding assessment')
            
            if 'statin' in interaction.get('mechanism', '').lower():
                if 'Liver function tests' not in monitoring_plan['laboratory_monitoring']:
                    monitoring_plan['laboratory_monitoring'].append('Liver function tests')
                if 'Muscle pain assessment' not in monitoring_plan['clinical_monitoring']:
                    monitoring_plan['clinical_monitoring'].append('Muscle pain assessment')
            
            if interaction['severity'] == 'High':
                monitoring_plan['frequency'] = 'Intensive'
        
        return monitoring_plan
