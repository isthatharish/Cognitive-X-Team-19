from typing import List, Optional
from dataclasses import dataclass
from datetime import date

@dataclass
class PatientProfile:
    """Patient profile data structure"""
    name: str
    age: int
    weight: float  # in kg
    conditions: List[str]
    allergies: List[str]
    height: Optional[float] = None  # in cm
    sex: Optional[str] = None
    pregnancy_status: Optional[str] = None
    lactation_status: Optional[bool] = None
    smoking_status: Optional[str] = None
    alcohol_use: Optional[str] = None
    
    def __post_init__(self):
        """Validate patient data after initialization"""
        if self.age < 0 or self.age > 150:
            raise ValueError("Age must be between 0 and 150")
        
        if self.weight <= 0 or self.weight > 500:
            raise ValueError("Weight must be between 0 and 500 kg")
        
        # Clean up conditions and allergies
        self.conditions = [condition.strip() for condition in self.conditions if condition.strip()]
        self.allergies = [allergy.strip() for allergy in self.allergies if allergy.strip()]
    
    def get_bmi(self) -> Optional[float]:
        """Calculate BMI if height is available"""
        if self.height:
            height_m = self.height / 100  # Convert cm to meters
            return self.weight / (height_m ** 2)
        return None
    
    def get_age_category(self) -> str:
        """Get age category for dosing purposes"""
        if self.age < 18:
            return "pediatric"
        elif self.age < 65:
            return "adult"
        else:
            return "geriatric"
    
    def get_weight_category(self) -> str:
        """Get weight category"""
        bmi = self.get_bmi()
        if bmi:
            if bmi < 18.5:
                return "underweight"
            elif bmi < 25:
                return "normal"
            elif bmi < 30:
                return "overweight"
            else:
                return "obese"
        
        # Fallback based on weight alone (assuming average height)
        if self.weight < 50:
            return "low_weight"
        elif self.weight < 90:
            return "normal_weight"
        else:
            return "high_weight"
    
    def has_condition(self, condition: str) -> bool:
        """Check if patient has a specific condition"""
        return any(condition.lower() in c.lower() for c in self.conditions)
    
    def has_allergy(self, substance: str) -> bool:
        """Check if patient has allergy to a substance"""
        return any(substance.lower() in a.lower() for a in self.allergies)
    
    def get_renal_function_category(self) -> str:
        """Estimate renal function category based on age and conditions"""
        if self.has_condition("kidney disease") or self.has_condition("renal"):
            return "impaired"
        elif self.age >= 80:
            return "possibly_impaired"
        elif self.age >= 65:
            return "age_related_decline"
        else:
            return "normal"
    
    def get_hepatic_function_category(self) -> str:
        """Estimate hepatic function category based on conditions"""
        if self.has_condition("liver disease") or self.has_condition("hepatic") or self.has_condition("cirrhosis"):
            return "impaired"
        elif self.alcohol_use in ["heavy", "chronic"]:
            return "possibly_impaired"
        else:
            return "normal"
    
    def get_special_populations(self) -> List[str]:
        """Get list of special population categories"""
        populations = []
        
        if self.age < 18:
            populations.append("pediatric")
        elif self.age >= 65:
            populations.append("geriatric")
        
        if self.pregnancy_status in ["pregnant", "trying_to_conceive"]:
            populations.append("pregnancy")
        
        if self.lactation_status:
            populations.append("lactation")
        
        if self.get_renal_function_category() != "normal":
            populations.append("renal_impairment")
        
        if self.get_hepatic_function_category() != "normal":
            populations.append("hepatic_impairment")
        
        return populations
    
    def get_contraindication_keywords(self) -> List[str]:
        """Get keywords for contraindication checking"""
        keywords = []
        
        # Add conditions
        keywords.extend([c.lower() for c in self.conditions])
        
        # Add allergies
        keywords.extend([a.lower() for a in self.allergies])
        
        # Add age-related keywords
        if self.age < 18:
            keywords.extend(["pediatric", "children", "adolescent"])
        elif self.age >= 65:
            keywords.extend(["geriatric", "elderly", "aged"])
        
        # Add pregnancy/lactation
        if self.pregnancy_status == "pregnant":
            keywords.append("pregnancy")
        if self.lactation_status:
            keywords.append("lactation")
        
        return list(set(keywords))  # Remove duplicates
    
    def to_dict(self) -> dict:
        """Convert patient profile to dictionary"""
        return {
            'name': self.name,
            'age': self.age,
            'weight': self.weight,
            'height': self.height,
            'sex': self.sex,
            'conditions': self.conditions,
            'allergies': self.allergies,
            'bmi': self.get_bmi(),
            'age_category': self.get_age_category(),
            'weight_category': self.get_weight_category(),
            'renal_function': self.get_renal_function_category(),
            'hepatic_function': self.get_hepatic_function_category(),
            'special_populations': self.get_special_populations()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PatientProfile':
        """Create patient profile from dictionary"""
        return cls(
            name=data['name'],
            age=data['age'],
            weight=data['weight'],
            conditions=data.get('conditions', []),
            allergies=data.get('allergies', []),
            height=data.get('height'),
            sex=data.get('sex'),
            pregnancy_status=data.get('pregnancy_status'),
            lactation_status=data.get('lactation_status'),
            smoking_status=data.get('smoking_status'),
            alcohol_use=data.get('alcohol_use')
        )
    
    def __str__(self) -> str:
        """String representation of patient profile"""
        return f"Patient: {self.name}, Age: {self.age}, Weight: {self.weight}kg, Conditions: {', '.join(self.conditions) if self.conditions else 'None'}"
