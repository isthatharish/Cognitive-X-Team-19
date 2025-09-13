import os
import json
import re
from typing import List, Dict, Optional
import requests
from dataclasses import dataclass

@dataclass
class DrugMention:
    """Structure for extracted drug mentions"""
    name: str
    dosage: str
    frequency: str
    duration: Optional[str] = None
    instructions: Optional[str] = None
    confidence: float = 0.0

class NLPProcessor:
    """NLP processor using IBM Granite models via Hugging Face for drug information extraction"""
    
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.hf_api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable is required but not set. Please set it before running the application.")
        self.model_name = "ibm-granite/granite-3.3-2b-base"
        self.hf_endpoint = f"https://api-inference.huggingface.co/models/{self.model_name}"
        
        # Common drug patterns for regex fallback
        self.drug_patterns = {
            'dosage': r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|iu|units?)',
            'frequency': r'(once|twice|three times?|four times?|\d+\s*times?)\s*(daily|a day|per day|bid|tid|qid|qd)',
            'duration': r'for\s+(\d+)\s*(days?|weeks?|months?)',
            'instructions': r'(with|without|before|after)\s+(meals?|food|eating)'
        }
    
    def extract_drug_information(self, text: str) -> List[Dict]:
        """Extract structured drug information from unstructured text"""
        try:
            # Primary method: IBM Granite model
            granite_results = self._extract_with_granite(text)
            if granite_results:
                return granite_results
            
            # Fallback method: Rule-based extraction
            return self._extract_with_rules(text)
            
        except Exception as e:
            print(f"Error in drug extraction: {str(e)}")
            # Return rule-based extraction as ultimate fallback
            return self._extract_with_rules(text)
    
    def _extract_with_granite(self, text: str) -> Optional[List[Dict]]:
        """Extract drug information using IBM Granite model via Hugging Face"""
        try:
            prompt = f"""Extract drug information from the following medical text. For each drug mentioned, provide:
            - Drug name
            - Dosage (amount and unit)
            - Frequency (how often per day)
            - Duration (if mentioned)
            - Special instructions (if any)
            - Confidence score (0-1)
            
            Text: {text}
            
            Respond with a JSON array of objects with fields: name, dosage, frequency, duration, instructions, confidence."""
            
            headers = {
                'Authorization': f'Bearer {self.hf_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'inputs': prompt,
                'parameters': {
                    'max_length': 1000,
                    'temperature': 0.1,
                    'return_full_text': False
                }
            }
            
            response = requests.post(self.hf_endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse Hugging Face response
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '').strip()
                    
                    # Try to parse JSON from the response
                    try:
                        extracted_data = json.loads(generated_text)
                        if isinstance(extracted_data, list):
                            return extracted_data
                        elif isinstance(extracted_data, dict):
                            return [extracted_data]
                    except json.JSONDecodeError:
                        # If JSON parsing fails, fallback to rule-based
                        pass
            
            return None
            
        except Exception as e:
            print(f"Error with Granite model via Hugging Face: {str(e)}")
            return None
    
    def _extract_with_rules(self, text: str) -> List[Dict]:
        """Rule-based drug information extraction as fallback"""
        try:
            extracted_drugs = []
            
            # Common drug name patterns (this would be expanded with a comprehensive drug list)
            common_drugs = [
                'metformin', 'lisinopril', 'atorvastatin', 'amlodipine', 'omeprazole',
                'metoprolol', 'losartan', 'simvastatin', 'levothyroxine', 'hydrochlorothiazide',
                'amoxicillin', 'azithromycin', 'doxycycline', 'ciprofloxacin', 'prednisone',
                'ibuprofen', 'acetaminophen', 'aspirin', 'warfarin', 'clopidogrel',
                'insulin', 'furosemide', 'carvedilol', 'gabapentin', 'sertraline'
            ]
            
            # Split text into sentences for better processing
            sentences = re.split(r'[.;]\s*', text.lower())
            
            for sentence in sentences:
                for drug in common_drugs:
                    if drug in sentence:
                        drug_info = self._extract_drug_details(sentence, drug)
                        if drug_info:
                            extracted_drugs.append(drug_info)
            
            # Remove duplicates based on drug name
            unique_drugs = []
            seen_drugs = set()
            
            for drug in extracted_drugs:
                if drug['name'] not in seen_drugs:
                    unique_drugs.append(drug)
                    seen_drugs.add(drug['name'])
            
            return unique_drugs
            
        except Exception as e:
            print(f"Error in rule-based extraction: {str(e)}")
            return []
    
    def _extract_drug_details(self, sentence: str, drug_name: str) -> Optional[Dict]:
        """Extract details for a specific drug from a sentence"""
        try:
            # Extract dosage
            dosage_match = re.search(self.drug_patterns['dosage'], sentence, re.IGNORECASE)
            dosage = f"{dosage_match.group(1)} {dosage_match.group(2)}" if dosage_match else "Not specified"
            
            # Extract frequency
            frequency_match = re.search(self.drug_patterns['frequency'], sentence, re.IGNORECASE)
            frequency = frequency_match.group(0) if frequency_match else "As directed"
            
            # Extract duration
            duration_match = re.search(self.drug_patterns['duration'], sentence, re.IGNORECASE)
            duration = duration_match.group(0) if duration_match else None
            
            # Extract instructions
            instructions_match = re.search(self.drug_patterns['instructions'], sentence, re.IGNORECASE)
            instructions = instructions_match.group(0) if instructions_match else None
            
            # Calculate confidence based on extracted information
            confidence = 0.6  # Base confidence for finding the drug
            if dosage != "Not specified":
                confidence += 0.2
            if frequency != "As directed":
                confidence += 0.15
            if duration:
                confidence += 0.05
                
            return {
                'name': drug_name.title(),
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration,
                'instructions': instructions,
                'confidence': min(confidence, 1.0)
            }
            
        except Exception as e:
            print(f"Error extracting drug details: {str(e)}")
            return None
    
    def standardize_drug_name(self, drug_name: str) -> str:
        """Standardize drug name format"""
        # Remove common suffixes and normalize
        drug_name = drug_name.strip().lower()
        
        # Remove dosage information from name
        drug_name = re.sub(r'\s+\d+\s*(mg|g|ml|mcg)', '', drug_name)
        
        # Remove brand name indicators
        drug_name = re.sub(r'\s*\([^)]+\)', '', drug_name)
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in drug_name.split())
    
    def extract_dosage_amount(self, dosage_string: str) -> Optional[float]:
        """Extract numeric dosage amount"""
        try:
            match = re.search(r'(\d+(?:\.\d+)?)', dosage_string)
            if match:
                return float(match.group(1))
            return None
        except:
            return None
    
    def extract_dosage_unit(self, dosage_string: str) -> Optional[str]:
        """Extract dosage unit"""
        try:
            match = re.search(r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|iu|units?)', dosage_string, re.IGNORECASE)
            if match:
                return match.group(2).lower()
            return None
        except:
            return None
    
    def parse_frequency(self, frequency_string: str) -> int:
        """Parse frequency string to times per day"""
        frequency_map = {
            'once': 1, 'daily': 1, 'qd': 1,
            'twice': 2, 'bid': 2,
            'three times': 3, 'tid': 3,
            'four times': 4, 'qid': 4
        }
        
        freq_lower = frequency_string.lower()
        
        for key, value in frequency_map.items():
            if key in freq_lower:
                return value
        
        # Try to extract number
        match = re.search(r'(\d+)', frequency_string)
        if match:
            return int(match.group(1))
        
        return 1  # Default to once daily
    
    def validate_extraction(self, extracted_data: List[Dict]) -> List[Dict]:
        """Validate and clean extracted drug data"""
        validated_data = []
        
        for drug in extracted_data:
            # Ensure required fields exist
            if not drug.get('name'):
                continue
            
            # Standardize drug name
            drug['name'] = self.standardize_drug_name(drug['name'])
            
            # Validate dosage format
            if not drug.get('dosage') or drug['dosage'] == "Not specified":
                drug['dosage'] = "Dosage not specified"
            
            # Validate frequency
            if not drug.get('frequency') or drug['frequency'] == "As directed":
                drug['frequency'] = "As directed by physician"
            
            # Ensure confidence is a float
            drug['confidence'] = float(drug.get('confidence', 0.5))
            
            validated_data.append(drug)
        
        return validated_data
