from typing import Dict, List, Optional
import math
from drug_database import DrugDatabase
from patient_profile import PatientProfile

class DosageRecommender:
    """Provides age-specific and condition-specific dosage recommendations"""
    
    def __init__(self, drug_database: DrugDatabase):
        self.db = drug_database
        
        # Age-based dosage adjustment factors
        self.age_factors = {
            'pediatric': {
                'age_range': (0, 18),
                'weight_based': True,
                'renal_factor': 1.0,
                'hepatic_factor': 0.8
            },
            'adult': {
                'age_range': (18, 65),
                'weight_based': False,
                'renal_factor': 1.0,
                'hepatic_factor': 1.0
            },
            'geriatric': {
                'age_range': (65, 150),
                'weight_based': False,
                'renal_factor': 0.7,
                'hepatic_factor': 0.8
            }
        }
        
        # Condition-based adjustments
        self.condition_adjustments = {
            'kidney disease': {'renal_factor': 0.5, 'monitoring': 'Frequent renal function monitoring'},
            'liver disease': {'hepatic_factor': 0.6, 'monitoring': 'Liver function monitoring'},
            'heart disease': {'cardiac_factor': 0.9, 'monitoring': 'Cardiac function monitoring'},
            'diabetes': {'interaction_risk': True, 'monitoring': 'Blood glucose monitoring'}
        }
    
    def get_recommendation(self, drug_name: str, patient: PatientProfile, 
                          indication: str = 'General') -> Optional[Dict]:
        """Get comprehensive dosage recommendation for a patient"""
        try:
            # Get drug information from database
            drug_info = self.db.get_drug_info(drug_name)
            if not drug_info:
                return None
            
            # Determine age category
            age_category = self._get_age_category(patient.age)
            
            # Calculate base dosage
            base_dosage = self._parse_dosage(drug_info['standard_dosage'])
            if not base_dosage:
                return None
            
            # Apply age-specific adjustments
            adjusted_dosage = self._apply_age_adjustments(
                base_dosage, age_category, patient
            )
            
            # Apply condition-specific adjustments
            final_dosage = self._apply_condition_adjustments(
                adjusted_dosage, patient.conditions, drug_info
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                drug_info, final_dosage, patient, age_category, indication
            )
            
            return recommendation
            
        except Exception as e:
            print(f"Error getting dosage recommendation: {str(e)}")
            return None
    
    def _get_age_category(self, age: int) -> str:
        """Determine age category for dosing"""
        if age < 18:
            return 'pediatric'
        elif age < 65:
            return 'adult'
        else:
            return 'geriatric'
    
    def _parse_dosage(self, dosage_string: str) -> Optional[Dict]:
        """Parse dosage string into structured format"""
        try:
            import re
            
            # Extract numeric dose and unit
            dose_match = re.search(r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|iu|units?)', 
                                 dosage_string, re.IGNORECASE)
            if not dose_match:
                return None
            
            amount = float(dose_match.group(1))
            unit = dose_match.group(2).lower()
            
            # Extract frequency
            frequency_patterns = {
                r'once\s+daily|qd|daily': 1,
                r'twice\s+daily|bid|b\.i\.d': 2,
                r'three\s+times\s+daily|tid|t\.i\.d': 3,
                r'four\s+times\s+daily|qid|q\.i\.d': 4
            }
            
            frequency = 1  # Default
            for pattern, freq in frequency_patterns.items():
                if re.search(pattern, dosage_string, re.IGNORECASE):
                    frequency = freq
                    break
            
            return {
                'amount': amount,
                'unit': unit,
                'frequency': frequency,
                'total_daily': amount * frequency
            }
            
        except Exception as e:
            print(f"Error parsing dosage: {str(e)}")
            return None
    
    def _apply_age_adjustments(self, base_dosage: Dict, age_category: str, 
                             patient: PatientProfile) -> Dict:
        """Apply age-specific dosage adjustments"""
        adjusted = base_dosage.copy()
        age_settings = self.age_factors[age_category]
        
        # Pediatric weight-based dosing
        if age_category == 'pediatric' and age_settings['weight_based']:
            # Common pediatric dosing: mg/kg
            weight_factor = patient.weight / 70  # Assume 70kg adult reference
            adjusted['amount'] *= weight_factor
            adjusted['total_daily'] = adjusted['amount'] * adjusted['frequency']
        
        # Geriatric dose reduction
        elif age_category == 'geriatric':
            # Reduce dose by 20-30% for elderly
            reduction_factor = 0.75
            adjusted['amount'] *= reduction_factor
            adjusted['total_daily'] = adjusted['amount'] * adjusted['frequency']
        
        return adjusted
    
    def _apply_condition_adjustments(self, dosage: Dict, conditions: List[str], 
                                   drug_info: Dict) -> Dict:
        """Apply condition-specific dosage adjustments"""
        adjusted = dosage.copy()
        
        for condition in conditions:
            condition_lower = condition.lower()
            
            # Renal impairment adjustments
            if 'kidney' in condition_lower or 'renal' in condition_lower:
                if drug_info.get('renal_adjustment'):
                    # Reduce dose for renally eliminated drugs
                    adjusted['amount'] *= 0.7
                    adjusted['total_daily'] = adjusted['amount'] * adjusted['frequency']
            
            # Hepatic impairment adjustments
            elif 'liver' in condition_lower or 'hepatic' in condition_lower:
                if drug_info.get('hepatic_adjustment'):
                    # Reduce dose for hepatically metabolized drugs
                    adjusted['amount'] *= 0.6
                    adjusted['total_daily'] = adjusted['amount'] * adjusted['frequency']
        
        return adjusted
    
    def _generate_recommendation(self, drug_info: Dict, dosage: Dict, 
                               patient: PatientProfile, age_category: str,
                               indication: str) -> Dict:
        """Generate comprehensive dosage recommendation"""
        
        # Format dosage string
        dosage_str = f"{dosage['amount']:.1f} {dosage['unit']}"
        
        # Determine frequency string
        frequency_map = {
            1: 'once daily',
            2: 'twice daily',
            3: 'three times daily',
            4: 'four times daily'
        }
        frequency_str = frequency_map.get(dosage['frequency'], f"{dosage['frequency']} times daily")
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(drug_info, patient, dosage)
        
        # Generate warnings
        warnings = self._generate_warnings(drug_info, patient, age_category)
        
        # Generate monitoring requirements
        monitoring = self._generate_monitoring_requirements(drug_info, patient)
        
        # Age-specific considerations
        age_considerations = self._get_age_considerations(age_category, patient.age)
        
        recommendation = {
            'drug_name': drug_info['name'],
            'dosage': dosage_str,
            'frequency': frequency_str,
            'total_daily_dose': f"{dosage['total_daily']:.1f} {dosage['unit']}",
            'route': 'Oral',  # Default, would be from drug_info in real implementation
            'duration': 'As prescribed',
            'indication': indication,
            'safety_score': safety_score,
            'warnings': warnings,
            'monitoring': monitoring,
            'age_adjustments': age_considerations,
            'age_suitable': self._is_age_suitable(drug_info, patient.age),
            'dosage_appropriate': self._is_dosage_appropriate(drug_info, dosage)
        }
        
        return recommendation
    
    def _calculate_safety_score(self, drug_info: Dict, patient: PatientProfile, 
                              dosage: Dict) -> int:
        """Calculate safety score (0-100)"""
        score = 85  # Base score
        
        # Adjust for patient conditions
        for condition in patient.conditions:
            contraindications = self.db.check_contraindications(
                drug_info['name'], [condition], patient.allergies
            )
            if contraindications:
                for contraindication in contraindications:
                    if contraindication['severity'] == 'High':
                        score -= 25
                    elif contraindication['severity'] == 'Moderate':
                        score -= 15
                    else:
                        score -= 5
        
        # Adjust for dosage appropriateness
        max_dose = self._parse_max_dose(drug_info.get('max_daily_dose', ''))
        if max_dose and dosage['total_daily'] > max_dose:
            score -= 20
        
        # Adjust for age appropriateness
        if patient.age < 18 and not drug_info.get('pediatric_dosage'):
            score -= 15
        elif patient.age >= 65 and not drug_info.get('geriatric_considerations'):
            score -= 10
        
        return max(0, min(100, score))
    
    def _parse_max_dose(self, max_dose_string: str) -> Optional[float]:
        """Parse maximum dose string"""
        try:
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', max_dose_string)
            if match:
                return float(match.group(1))
            return None
        except:
            return None
    
    def _generate_warnings(self, drug_info: Dict, patient: PatientProfile, 
                         age_category: str) -> List[str]:
        """Generate patient-specific warnings"""
        warnings = []
        
        # Age-specific warnings
        if age_category == 'pediatric':
            warnings.append("Pediatric dosing requires careful weight-based calculation")
        elif age_category == 'geriatric':
            warnings.append("Elderly patients may require dose reduction and closer monitoring")
        
        # Condition-specific warnings
        for condition in patient.conditions:
            if 'kidney' in condition.lower():
                warnings.append("Renal function monitoring required")
            elif 'liver' in condition.lower():
                warnings.append("Hepatic function monitoring required")
            elif 'heart' in condition.lower():
                warnings.append("Cardiac monitoring may be required")
        
        # Drug-specific warnings from database
        if drug_info.get('serious_adverse_effects'):
            warnings.append(f"Monitor for: {drug_info['serious_adverse_effects']}")
        
        return warnings
    
    def _generate_monitoring_requirements(self, drug_info: Dict, 
                                        patient: PatientProfile) -> str:
        """Generate monitoring requirements"""
        monitoring_items = []
        
        # Add drug-specific monitoring
        if drug_info.get('monitoring_parameters'):
            monitoring_items.append(drug_info['monitoring_parameters'])
        
        # Add condition-specific monitoring
        for condition in patient.conditions:
            if condition.lower() in self.condition_adjustments:
                monitoring_items.append(
                    self.condition_adjustments[condition.lower()]['monitoring']
                )
        
        return "; ".join(monitoring_items) if monitoring_items else "Standard clinical monitoring"
    
    def _get_age_considerations(self, age_category: str, age: int) -> str:
        """Get age-specific dosing considerations"""
        if age_category == 'pediatric':
            return f"Pediatric patient (age {age}): Weight-based dosing applied with safety margin"
        elif age_category == 'geriatric':
            return f"Geriatric patient (age {age}): Dose reduced for age-related physiological changes"
        else:
            return "Standard adult dosing applied"
    
    def _is_age_suitable(self, drug_info: Dict, age: int) -> bool:
        """Check if drug is suitable for patient age"""
        if age < 18:
            return bool(drug_info.get('pediatric_dosage'))
        elif age >= 65:
            return True  # Most drugs can be used in elderly with adjustments
        else:
            return True
    
    def _is_dosage_appropriate(self, drug_info: Dict, dosage: Dict) -> bool:
        """Check if calculated dosage is appropriate"""
        max_dose = self._parse_max_dose(drug_info.get('max_daily_dose', ''))
        if max_dose and dosage['total_daily'] > max_dose:
            return False
        
        # Check if dose is too low (less than 10% of standard)
        standard_dose = self._parse_dosage(drug_info.get('standard_dosage', ''))
        if standard_dose and dosage['total_daily'] < (standard_dose['total_daily'] * 0.1):
            return False
        
        return True
