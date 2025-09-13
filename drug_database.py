import sqlite3
import json
import pandas as pd
from typing import List, Dict, Optional
import os

class DrugDatabase:
    """Handles drug database operations and queries"""
    
    def __init__(self, db_path: str = "drug_database.db"):
        self.db_path = db_path
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        except Exception as e:
            raise Exception(f"Failed to connect to database: {str(e)}")
    
    def get_drug_info(self, drug_name: str) -> Optional[Dict]:
        """Get comprehensive drug information"""
        try:
            if not self.connection:
                return None
            cursor = self.connection.cursor()
            
            query = """
                SELECT d.*, GROUP_CONCAT(i.indication) as indications,
                       GROUP_CONCAT(c.contraindication) as contraindications
                FROM drugs d
                LEFT JOIN drug_indications i ON d.id = i.drug_id
                LEFT JOIN drug_contraindications c ON d.id = c.drug_id
                WHERE LOWER(d.name) = LOWER(?) OR LOWER(d.generic_name) = LOWER(?)
                GROUP BY d.id
            """
            
            cursor.execute(query, (drug_name, drug_name))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result['id'],
                    'name': result['name'],
                    'generic_name': result['generic_name'],
                    'therapeutic_class': result['therapeutic_class'],
                    'mechanism': result['mechanism'],
                    'standard_dosage': result['standard_dosage'],
                    'max_daily_dose': result['max_daily_dose'],
                    'half_life': result['half_life'],
                    'bioavailability': result['bioavailability'],
                    'protein_binding': result['protein_binding'],
                    'metabolism': result['metabolism'],
                    'elimination': result['elimination'],
                    'pregnancy_category': result['pregnancy_category'],
                    'lactation_safety': result['lactation_safety'],
                    'pediatric_dosage': result['pediatric_dosage'],
                    'geriatric_considerations': result['geriatric_considerations'],
                    'renal_adjustment': result['renal_adjustment'],
                    'hepatic_adjustment': result['hepatic_adjustment'],
                    'common_side_effects': result['common_side_effects'],
                    'serious_adverse_effects': result['serious_adverse_effects'],
                    'monitoring_parameters': result['monitoring_parameters'],
                    'drug_interactions': result['drug_interactions'],
                    'food_interactions': result['food_interactions'],
                    'cost_tier': result['cost_tier'],
                    'indications': result['indications'].split(',') if result['indications'] else [],
                    'contraindications': result['contraindications'].split(',') if result['contraindications'] else []
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting drug info: {str(e)}")
            return None
    
    def search_drugs(self, search_term: str, limit: int = 10) -> List[Dict]:
        """Search for drugs by name or generic name"""
        try:
            cursor = self.connection.cursor()
            
            query = """
                SELECT name, generic_name, therapeutic_class
                FROM drugs 
                WHERE LOWER(name) LIKE LOWER(?) OR LOWER(generic_name) LIKE LOWER(?)
                ORDER BY 
                    CASE 
                        WHEN LOWER(name) = LOWER(?) THEN 1
                        WHEN LOWER(generic_name) = LOWER(?) THEN 2
                        WHEN LOWER(name) LIKE LOWER(?) THEN 3
                        ELSE 4
                    END
                LIMIT ?
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_term, 
                                 search_term, f"{search_term}%", limit))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error searching drugs: {str(e)}")
            return []
    
    def get_drug_interactions(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Get interaction information between two drugs"""
        try:
            cursor = self.connection.cursor()
            
            query = """
                SELECT di.*, d1.name as drug1_name, d2.name as drug2_name
                FROM drug_interactions di
                JOIN drugs d1 ON di.drug1_id = d1.id
                JOIN drugs d2 ON di.drug2_id = d2.id
                WHERE (LOWER(d1.name) = LOWER(?) AND LOWER(d2.name) = LOWER(?))
                   OR (LOWER(d1.name) = LOWER(?) AND LOWER(d2.name) = LOWER(?))
                   OR (LOWER(d1.generic_name) = LOWER(?) AND LOWER(d2.generic_name) = LOWER(?))
                   OR (LOWER(d1.generic_name) = LOWER(?) AND LOWER(d2.generic_name) = LOWER(?))
            """
            
            cursor.execute(query, (drug1, drug2, drug2, drug1, drug1, drug2, drug2, drug1))
            result = cursor.fetchone()
            
            if result:
                return {
                    'drug1': result['drug1_name'],
                    'drug2': result['drug2_name'],
                    'severity': result['severity'],
                    'risk_level': result['risk_level'],
                    'mechanism': result['mechanism'],
                    'description': result['description'],
                    'clinical_significance': result['clinical_significance'],
                    'recommendation': result['recommendation'],
                    'monitoring_required': bool(result['monitoring_required'])
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting drug interactions: {str(e)}")
            return None
    
    def get_therapeutic_alternatives(self, drug_name: str, therapeutic_class: str = None) -> List[Dict]:
        """Get therapeutic alternatives for a drug"""
        try:
            cursor = self.connection.cursor()
            
            # First get the drug's therapeutic class if not provided
            if not therapeutic_class:
                drug_info = self.get_drug_info(drug_name)
                if drug_info:
                    therapeutic_class = drug_info['therapeutic_class']
                else:
                    return []
            
            query = """
                SELECT name, generic_name, mechanism, standard_dosage, cost_tier
                FROM drugs 
                WHERE therapeutic_class = ? AND LOWER(name) != LOWER(?) AND LOWER(generic_name) != LOWER(?)
                ORDER BY cost_tier, name
                LIMIT 10
            """
            
            cursor.execute(query, (therapeutic_class, drug_name, drug_name))
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting therapeutic alternatives: {str(e)}")
            return []
    
    def get_age_specific_dosage(self, drug_name: str, age: int) -> Optional[Dict]:
        """Get age-specific dosage recommendations"""
        try:
            cursor = self.connection.cursor()
            
            query = """
                SELECT d.*, 
                       CASE 
                           WHEN ? < 18 THEN d.pediatric_dosage
                           WHEN ? >= 65 THEN d.geriatric_considerations
                           ELSE d.standard_dosage
                       END as recommended_dosage
                FROM drugs d
                WHERE LOWER(d.name) = LOWER(?) OR LOWER(d.generic_name) = LOWER(?)
            """
            
            cursor.execute(query, (age, age, drug_name, drug_name))
            result = cursor.fetchone()
            
            if result:
                return {
                    'drug_name': result['name'],
                    'recommended_dosage': result['recommended_dosage'] or result['standard_dosage'],
                    'standard_dosage': result['standard_dosage'],
                    'max_daily_dose': result['max_daily_dose'],
                    'age_specific': age < 18 or age >= 65,
                    'special_considerations': result['geriatric_considerations'] if age >= 65 else result['pediatric_dosage']
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting age-specific dosage: {str(e)}")
            return None
    
    def check_contraindications(self, drug_name: str, conditions: List[str], allergies: List[str] = None) -> List[Dict]:
        """Check for contraindications based on patient conditions and allergies"""
        try:
            contraindications = []
            
            # Check medical condition contraindications
            cursor = self.connection.cursor()
            
            placeholders = ','.join(['?' for _ in conditions])
            query = f"""
                SELECT dc.contraindication, dc.severity, dc.reason
                FROM drug_contraindications dc
                JOIN drugs d ON dc.drug_id = d.id
                WHERE (LOWER(d.name) = LOWER(?) OR LOWER(d.generic_name) = LOWER(?))
                  AND LOWER(dc.contraindication) IN ({','.join(['LOWER(?)' for _ in conditions])})
            """
            
            params = [drug_name, drug_name] + conditions
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            for result in results:
                contraindications.append({
                    'type': 'condition',
                    'contraindication': result['contraindication'],
                    'severity': result['severity'],
                    'reason': result['reason']
                })
            
            # Check allergy contraindications
            if allergies:
                for allergy in allergies:
                    if allergy.lower() in drug_name.lower():
                        contraindications.append({
                            'type': 'allergy',
                            'contraindication': f"Allergy to {allergy}",
                            'severity': 'High',
                            'reason': 'Patient has documented allergy to this medication'
                        })
            
            return contraindications
            
        except Exception as e:
            print(f"Error checking contraindications: {str(e)}")
            return []
    
    def get_monitoring_requirements(self, drug_names: List[str]) -> Dict:
        """Get monitoring requirements for a list of drugs"""
        try:
            cursor = self.connection.cursor()
            
            placeholders = ','.join(['?' for _ in drug_names])
            query = f"""
                SELECT d.name, d.monitoring_parameters, d.serious_adverse_effects
                FROM drugs d
                WHERE LOWER(d.name) IN ({','.join(['LOWER(?)' for _ in drug_names])})
                   OR LOWER(d.generic_name) IN ({','.join(['LOWER(?)' for _ in drug_names])})
            """
            
            params = drug_names + drug_names
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            monitoring_data = {}
            for result in results:
                monitoring_data[result['name']] = {
                    'parameters': result['monitoring_parameters'],
                    'adverse_effects': result['serious_adverse_effects']
                }
            
            return monitoring_data
            
        except Exception as e:
            print(f"Error getting monitoring requirements: {str(e)}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
