from typing import List, Dict, Optional
from drug_database import DrugDatabase
from patient_profile import PatientProfile

class AlternativeFinder:
    """Finds alternative medications when contraindications exist"""
    
    def __init__(self, drug_database: DrugDatabase):
        self.db = drug_database
        
        # Therapeutic equivalence groups
        self.therapeutic_groups = {
            'ace_inhibitors': {
                'drugs': ['lisinopril', 'enalapril', 'captopril', 'ramipril'],
                'mechanism': 'ACE inhibition',
                'indication': 'Hypertension, Heart Failure'
            },
            'arbs': {
                'drugs': ['losartan', 'valsartan', 'irbesartan', 'olmesartan'],
                'mechanism': 'Angiotensin receptor blockade',
                'indication': 'Hypertension, Heart Failure'
            },
            'statins': {
                'drugs': ['atorvastatin', 'simvastatin', 'rosuvastatin', 'pravastatin'],
                'mechanism': 'HMG-CoA reductase inhibition',
                'indication': 'Hyperlipidemia'
            },
            'beta_blockers': {
                'drugs': ['metoprolol', 'atenolol', 'propranolol', 'carvedilol'],
                'mechanism': 'Beta-adrenergic blockade',
                'indication': 'Hypertension, Heart Disease'
            },
            'diuretics_thiazide': {
                'drugs': ['hydrochlorothiazide', 'chlorthalidone', 'indapamide'],
                'mechanism': 'Sodium-chloride cotransporter inhibition',
                'indication': 'Hypertension, Edema'
            },
            'diuretics_loop': {
                'drugs': ['furosemide', 'bumetanide', 'torsemide'],
                'mechanism': 'Na-K-2Cl cotransporter inhibition',
                'indication': 'Heart Failure, Edema'
            },
            'calcium_channel_blockers': {
                'drugs': ['amlodipine', 'nifedipine', 'diltiazem', 'verapamil'],
                'mechanism': 'Calcium channel blockade',
                'indication': 'Hypertension, Angina'
            },
            'proton_pump_inhibitors': {
                'drugs': ['omeprazole', 'lansoprazole', 'pantoprazole', 'esomeprazole'],
                'mechanism': 'Proton pump inhibition',
                'indication': 'GERD, Peptic Ulcer'
            },
            'ssri_antidepressants': {
                'drugs': ['sertraline', 'fluoxetine', 'paroxetine', 'citalopram'],
                'mechanism': 'Selective serotonin reuptake inhibition',
                'indication': 'Depression, Anxiety'
            },
            'antibiotics_penicillin': {
                'drugs': ['amoxicillin', 'ampicillin', 'penicillin'],
                'mechanism': 'Beta-lactam antibiotic',
                'indication': 'Bacterial Infections'
            },
            'antibiotics_macrolide': {
                'drugs': ['azithromycin', 'clarithromycin', 'erythromycin'],
                'mechanism': 'Protein synthesis inhibition',
                'indication': 'Bacterial Infections'
            },
            'antibiotics_quinolone': {
                'drugs': ['ciprofloxacin', 'levofloxacin', 'moxifloxacin'],
                'mechanism': 'DNA gyrase inhibition',
                'indication': 'Bacterial Infections'
            }
        }
        
        # Cross-class alternatives (when switching drug classes)
        self.cross_class_alternatives = {
            'hypertension': ['ace_inhibitors', 'arbs', 'beta_blockers', 'calcium_channel_blockers', 'diuretics_thiazide'],
            'depression': ['ssri_antidepressants', 'snri_antidepressants', 'tricyclic_antidepressants'],
            'bacterial_infection': ['antibiotics_penicillin', 'antibiotics_macrolide', 'antibiotics_quinolone', 'antibiotics_cephalosporin']
        }
    
    def find_alternatives(self, problematic_drug: str, patient: PatientProfile,
                         reason: str, therapeutic_class: str = None) -> List[Dict]:
        """Find alternative medications for a problematic drug"""
        try:
            alternatives = []
            
            # Get drug information
            drug_info = self.db.get_drug_info(problematic_drug)
            if not drug_info:
                return self._find_alternatives_by_name(problematic_drug, patient, reason)
            
            # Find within-class alternatives first
            within_class = self._find_within_class_alternatives(
                problematic_drug, drug_info, patient, reason
            )
            alternatives.extend(within_class)
            
            # Find cross-class alternatives if needed
            if len(alternatives) < 5:
                cross_class = self._find_cross_class_alternatives(
                    drug_info, patient, reason
                )
                alternatives.extend(cross_class)
            
            # Get database alternatives
            db_alternatives = self.db.get_therapeutic_alternatives(
                problematic_drug, therapeutic_class
            )
            
            # Process database alternatives
            for alt in db_alternatives:
                if alt['name'].lower() != problematic_drug.lower():
                    processed_alt = self._process_alternative(
                        alt, patient, reason, problematic_drug
                    )
                    alternatives.append(processed_alt)
            
            # Remove duplicates and sort by suitability
            alternatives = self._deduplicate_and_rank(alternatives, patient, reason)
            
            return alternatives[:10]  # Return top 10 alternatives
            
        except Exception as e:
            print(f"Error finding alternatives: {str(e)}")
            return []
    
    def _find_within_class_alternatives(self, problematic_drug: str, drug_info: Dict,
                                      patient: PatientProfile, reason: str) -> List[Dict]:
        """Find alternatives within the same therapeutic class"""
        alternatives = []
        
        # Find the therapeutic group
        drug_group = None
        for group_name, group_info in self.therapeutic_groups.items():
            if any(drug.lower() in problematic_drug.lower() for drug in group_info['drugs']):
                drug_group = group_info
                break
        
        if not drug_group:
            return alternatives
        
        # Evaluate each drug in the group
        for alt_drug in drug_group['drugs']:
            if alt_drug.lower() != problematic_drug.lower():
                alt_info = self.db.get_drug_info(alt_drug)
                if alt_info:
                    alternative = self._evaluate_alternative(
                        alt_info, patient, reason, problematic_drug, drug_group
                    )
                    if alternative:
                        alternatives.append(alternative)
        
        return alternatives
    
    def _find_cross_class_alternatives(self, drug_info: Dict, patient: PatientProfile,
                                     reason: str) -> List[Dict]:
        """Find alternatives from different therapeutic classes"""
        alternatives = []
        
        # Determine likely indication based on drug class
        therapeutic_class = drug_info.get('therapeutic_class', '').lower()
        
        indication_mapping = {
            'antihypertensive': 'hypertension',
            'antidepressant': 'depression',
            'antibiotic': 'bacterial_infection',
            'analgesic': 'pain',
            'anticoagulant': 'anticoagulation'
        }
        
        indication = None
        for key, value in indication_mapping.items():
            if key in therapeutic_class:
                indication = value
                break
        
        if indication and indication in self.cross_class_alternatives:
            for alt_class in self.cross_class_alternatives[indication]:
                if alt_class in self.therapeutic_groups:
                    group_info = self.therapeutic_groups[alt_class]
                    # Get first drug from alternative class as representative
                    alt_drug_name = group_info['drugs'][0]
                    alt_info = self.db.get_drug_info(alt_drug_name)
                    
                    if alt_info:
                        alternative = self._evaluate_alternative(
                            alt_info, patient, reason, drug_info['name'], group_info
                        )
                        if alternative:
                            alternatives.append(alternative)
        
        return alternatives
    
    def _find_alternatives_by_name(self, drug_name: str, patient: PatientProfile,
                                 reason: str) -> List[Dict]:
        """Fallback method to find alternatives when drug not in database"""
        alternatives = []
        
        # Search for similar drugs
        similar_drugs = self.db.search_drugs(drug_name, limit=20)
        
        for drug in similar_drugs:
            if drug['name'].lower() != drug_name.lower():
                drug_info = self.db.get_drug_info(drug['name'])
                if drug_info:
                    alternative = {
                        'name': drug['name'],
                        'similarity_score': 0.7,  # Estimated
                        'safety_rating': 4,
                        'mechanism': drug_info.get('mechanism', 'Not specified'),
                        'advantages': ['Available in database', 'Well-documented profile'],
                        'considerations': ['Verify therapeutic equivalence'],
                        'cost_comparison': 'Similar',
                        'suitability_score': 70
                    }
                    alternatives.append(alternative)
        
        return alternatives[:5]
    
    def _evaluate_alternative(self, alt_info: Dict, patient: PatientProfile,
                            reason: str, original_drug: str, group_info: Dict = None) -> Optional[Dict]:
        """Evaluate suitability of an alternative drug"""
        try:
            # Check contraindications
            contraindications = self.db.check_contraindications(
                alt_info['name'], patient.conditions, patient.allergies
            )
            
            # Calculate suitability score
            suitability_score = 100
            
            # Reduce score for contraindications
            for contraindication in contraindications:
                if contraindication['severity'] == 'High':
                    suitability_score -= 30
                elif contraindication['severity'] == 'Moderate':
                    suitability_score -= 15
                else:
                    suitability_score -= 5
            
            # If suitability is too low, skip this alternative
            if suitability_score < 40:
                return None
            
            # Generate advantages and considerations
            advantages, considerations = self._generate_comparison_points(
                alt_info, patient, reason, original_drug
            )
            
            # Calculate similarity score
            similarity_score = self._calculate_similarity_score(alt_info, group_info)
            
            # Calculate safety rating
            safety_rating = self._calculate_safety_rating(alt_info, patient)
            
            return {
                'name': alt_info['name'],
                'similarity_score': similarity_score,
                'safety_rating': safety_rating,
                'mechanism': alt_info.get('mechanism', 'Not specified'),
                'advantages': advantages,
                'considerations': considerations,
                'cost_comparison': self._compare_cost(alt_info),
                'suitability_score': suitability_score,
                'contraindications': len(contraindications)
            }
            
        except Exception as e:
            print(f"Error evaluating alternative: {str(e)}")
            return None
    
    def _process_alternative(self, alt_dict: Dict, patient: PatientProfile,
                           reason: str, original_drug: str) -> Dict:
        """Process database alternative into standardized format"""
        
        # Get detailed info for the alternative
        alt_info = self.db.get_drug_info(alt_dict['name'])
        
        if alt_info:
            return self._evaluate_alternative(alt_info, patient, reason, original_drug)
        else:
            # Create basic alternative info
            return {
                'name': alt_dict['name'],
                'similarity_score': 0.8,
                'safety_rating': 4,
                'mechanism': alt_dict.get('mechanism', 'Not specified'),
                'advantages': ['Therapeutically equivalent'],
                'considerations': ['Verify dosing equivalence'],
                'cost_comparison': alt_dict.get('cost_tier', 'Similar'),
                'suitability_score': 75
            }
    
    def _generate_comparison_points(self, alt_info: Dict, patient: PatientProfile,
                                  reason: str, original_drug: str) -> tuple:
        """Generate advantages and considerations for alternative"""
        advantages = []
        considerations = []
        
        # Reason-specific advantages
        if reason == 'Drug Interaction':
            advantages.append('Potentially fewer drug interactions')
        elif reason == 'Allergy':
            advantages.append('Different chemical structure - unlikely to cross-react')
        elif reason == 'Side Effects':
            advantages.append('Different side effect profile')
        elif reason == 'Cost':
            advantages.append('More cost-effective option')
        
        # Patient-specific advantages
        if patient.age >= 65:
            if alt_info.get('geriatric_considerations'):
                advantages.append('Has specific geriatric dosing guidelines')
            else:
                considerations.append('Limited geriatric data available')
        
        if patient.age < 18:
            if alt_info.get('pediatric_dosage'):
                advantages.append('Has established pediatric dosing')
            else:
                considerations.append('Pediatric use requires careful consideration')
        
        # Condition-specific considerations
        for condition in patient.conditions:
            if 'kidney' in condition.lower() and alt_info.get('renal_adjustment'):
                considerations.append('Requires dose adjustment for renal impairment')
            elif 'liver' in condition.lower() and alt_info.get('hepatic_adjustment'):
                considerations.append('Requires dose adjustment for hepatic impairment')
        
        # General drug properties
        if alt_info.get('half_life'):
            advantages.append(f"Half-life: {alt_info['half_life']}")
        
        if alt_info.get('bioavailability'):
            advantages.append(f"Bioavailability: {alt_info['bioavailability']}")
        
        return advantages, considerations
    
    def _calculate_similarity_score(self, alt_info: Dict, group_info: Dict = None) -> float:
        """Calculate therapeutic similarity score"""
        base_score = 0.8  # Base similarity within therapeutic class
        
        if group_info:
            # Same mechanism of action
            if alt_info.get('mechanism') and group_info.get('mechanism'):
                if group_info['mechanism'].lower() in alt_info.get('mechanism', '').lower():
                    base_score += 0.1
        
        return min(1.0, base_score)
    
    def _calculate_safety_rating(self, alt_info: Dict, patient: PatientProfile) -> int:
        """Calculate safety rating (1-5 scale)"""
        rating = 4  # Base rating
        
        # Check for serious adverse effects
        if alt_info.get('serious_adverse_effects'):
            rating -= 1
        
        # Check pregnancy category if relevant
        if alt_info.get('pregnancy_category') in ['X', 'D']:
            rating -= 1
        
        # Adjust for patient age
        if patient.age >= 65 and not alt_info.get('geriatric_considerations'):
            rating -= 0.5
        elif patient.age < 18 and not alt_info.get('pediatric_dosage'):
            rating -= 0.5
        
        return max(1, min(5, int(rating)))
    
    def _compare_cost(self, alt_info: Dict) -> str:
        """Compare cost tier"""
        cost_tier = alt_info.get('cost_tier', 'Tier 2')
        
        cost_mapping = {
            'Tier 1': 'Lower cost',
            'Tier 2': 'Similar cost',
            'Tier 3': 'Higher cost',
            'Generic': 'Lower cost',
            'Brand': 'Higher cost'
        }
        
        return cost_mapping.get(cost_tier, 'Similar cost')
    
    def _deduplicate_and_rank(self, alternatives: List[Dict], patient: PatientProfile,
                            reason: str) -> List[Dict]:
        """Remove duplicates and rank alternatives by suitability"""
        
        # Remove duplicates based on drug name
        seen_names = set()
        unique_alternatives = []
        
        for alt in alternatives:
            if alt['name'] not in seen_names:
                unique_alternatives.append(alt)
                seen_names.add(alt['name'])
        
        # Sort by suitability score, then by safety rating
        unique_alternatives.sort(
            key=lambda x: (x.get('suitability_score', 0), x.get('safety_rating', 0)),
            reverse=True
        )
        
        return unique_alternatives
