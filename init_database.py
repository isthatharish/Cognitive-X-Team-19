import sqlite3
import os
from typing import List, Dict, Tuple

def initialize_database(db_path: str = "drug_database.db") -> bool:
    """Initialize the drug database with tables and essential data"""
    try:
        # Remove existing database if it exists (for fresh initialization)
        if os.path.exists(db_path):
            print(f"Existing database found at {db_path}, reinitializing...")
        
        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        create_tables(cursor)
        
        # Populate with essential drug data
        populate_essential_drugs(cursor)
        populate_drug_interactions(cursor)
        populate_drug_indications(cursor)
        populate_drug_contraindications(cursor)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"Database initialized successfully at {db_path}")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

def create_tables(cursor: sqlite3.Cursor):
    """Create all required database tables"""
    
    # Main drugs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            generic_name TEXT,
            therapeutic_class TEXT,
            mechanism TEXT,
            standard_dosage TEXT,
            max_daily_dose TEXT,
            half_life TEXT,
            bioavailability TEXT,
            protein_binding TEXT,
            metabolism TEXT,
            elimination TEXT,
            pregnancy_category TEXT,
            lactation_safety TEXT,
            pediatric_dosage TEXT,
            geriatric_considerations TEXT,
            renal_adjustment TEXT,
            hepatic_adjustment TEXT,
            common_side_effects TEXT,
            serious_adverse_effects TEXT,
            monitoring_parameters TEXT,
            drug_interactions TEXT,
            food_interactions TEXT,
            cost_tier TEXT DEFAULT 'Tier 2',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Drug interactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug1_id INTEGER,
            drug2_id INTEGER,
            severity TEXT CHECK(severity IN ('High', 'Moderate', 'Low', 'Minimal')),
            risk_level TEXT,
            mechanism TEXT,
            description TEXT,
            clinical_significance TEXT,
            recommendation TEXT,
            monitoring_required BOOLEAN DEFAULT 0,
            FOREIGN KEY (drug1_id) REFERENCES drugs (id),
            FOREIGN KEY (drug2_id) REFERENCES drugs (id),
            UNIQUE(drug1_id, drug2_id)
        )
    ''')
    
    # Drug indications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_indications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_id INTEGER,
            indication TEXT NOT NULL,
            primary_indication BOOLEAN DEFAULT 0,
            FOREIGN KEY (drug_id) REFERENCES drugs (id)
        )
    ''')
    
    # Drug contraindications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drug_contraindications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_id INTEGER,
            contraindication TEXT NOT NULL,
            severity TEXT CHECK(severity IN ('High', 'Moderate', 'Low')),
            reason TEXT,
            FOREIGN KEY (drug_id) REFERENCES drugs (id)
        )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_drugs_name ON drugs(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_drugs_generic ON drugs(generic_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_drugs_class ON drugs(therapeutic_class)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_drugs ON drug_interactions(drug1_id, drug2_id)')

def populate_essential_drugs(cursor: sqlite3.Cursor):
    """Populate database with essential commonly used drugs"""
    
    essential_drugs = [
        # Cardiovascular medications
        {
            'name': 'Lisinopril',
            'generic_name': 'lisinopril',
            'therapeutic_class': 'ACE Inhibitor',
            'mechanism': 'Inhibits angiotensin-converting enzyme',
            'standard_dosage': '10 mg once daily',
            'max_daily_dose': '80 mg',
            'half_life': '12 hours',
            'bioavailability': '25%',
            'pregnancy_category': 'D',
            'pediatric_dosage': '0.1 mg/kg once daily',
            'geriatric_considerations': 'Start with 2.5-5 mg daily',
            'renal_adjustment': 'Reduce dose in CrCl <30',
            'hepatic_adjustment': 'No adjustment needed',
            'common_side_effects': 'Dry cough, hyperkalemia, hypotension',
            'serious_adverse_effects': 'Angioedema, renal failure',
            'monitoring_parameters': 'Blood pressure, serum creatinine, potassium',
            'cost_tier': 'Tier 1'
        },
        {
            'name': 'Metoprolol',
            'generic_name': 'metoprolol',
            'therapeutic_class': 'Beta Blocker',
            'mechanism': 'Selective beta-1 adrenergic receptor antagonist',
            'standard_dosage': '50 mg twice daily',
            'max_daily_dose': '400 mg',
            'half_life': '3-7 hours',
            'bioavailability': '50%',
            'pregnancy_category': 'C',
            'pediatric_dosage': '1-2 mg/kg/day divided',
            'geriatric_considerations': 'Start with 25 mg twice daily',
            'renal_adjustment': 'No adjustment needed',
            'hepatic_adjustment': 'Reduce dose in severe impairment',
            'common_side_effects': 'Fatigue, bradycardia, hypotension',
            'serious_adverse_effects': 'Heart block, bronchospasm',
            'monitoring_parameters': 'Heart rate, blood pressure, ECG',
            'cost_tier': 'Tier 1'
        },
        {
            'name': 'Amlodipine',
            'generic_name': 'amlodipine',
            'therapeutic_class': 'Calcium Channel Blocker',
            'mechanism': 'Dihydropyridine calcium channel antagonist',
            'standard_dosage': '5 mg once daily',
            'max_daily_dose': '10 mg',
            'half_life': '30-50 hours',
            'bioavailability': '90%',
            'pregnancy_category': 'C',
            'pediatric_dosage': '0.1-0.2 mg/kg once daily',
            'geriatric_considerations': 'Start with 2.5 mg daily',
            'renal_adjustment': 'No adjustment needed',
            'hepatic_adjustment': 'Start with 2.5 mg daily',
            'common_side_effects': 'Peripheral edema, flushing, dizziness',
            'serious_adverse_effects': 'Severe hypotension, heart failure',
            'monitoring_parameters': 'Blood pressure, heart rate, edema',
            'cost_tier': 'Tier 1'
        },
        
        # Diabetes medications
        {
            'name': 'Metformin',
            'generic_name': 'metformin',
            'therapeutic_class': 'Antidiabetic - Biguanide',
            'mechanism': 'Decreases hepatic glucose production, increases insulin sensitivity',
            'standard_dosage': '500 mg twice daily with meals',
            'max_daily_dose': '2550 mg',
            'half_life': '6.2 hours',
            'bioavailability': '50-60%',
            'pregnancy_category': 'B',
            'pediatric_dosage': '10-25 mg/kg/day divided',
            'geriatric_considerations': 'Monitor renal function closely',
            'renal_adjustment': 'Contraindicated if CrCl <30',
            'hepatic_adjustment': 'Contraindicated in hepatic impairment',
            'common_side_effects': 'GI upset, metallic taste, diarrhea',
            'serious_adverse_effects': 'Lactic acidosis (rare)',
            'monitoring_parameters': 'HbA1c, renal function, vitamin B12',
            'cost_tier': 'Tier 1'
        },
        
        # Lipid-lowering medications
        {
            'name': 'Atorvastatin',
            'generic_name': 'atorvastatin',
            'therapeutic_class': 'HMG-CoA Reductase Inhibitor',
            'mechanism': 'Inhibits cholesterol synthesis',
            'standard_dosage': '20 mg once daily',
            'max_daily_dose': '80 mg',
            'half_life': '14 hours',
            'bioavailability': '14%',
            'pregnancy_category': 'X',
            'pediatric_dosage': '10 mg once daily (≥10 years)',
            'geriatric_considerations': 'No dose adjustment needed',
            'renal_adjustment': 'No adjustment needed',
            'hepatic_adjustment': 'Contraindicated in active liver disease',
            'common_side_effects': 'Muscle pain, headache, GI upset',
            'serious_adverse_effects': 'Rhabdomyolysis, hepatotoxicity',
            'monitoring_parameters': 'Lipid panel, liver enzymes, CK if muscle symptoms',
            'cost_tier': 'Tier 1'
        },
        
        # Antibiotics
        {
            'name': 'Amoxicillin',
            'generic_name': 'amoxicillin',
            'therapeutic_class': 'Penicillin Antibiotic',
            'mechanism': 'Beta-lactam antibiotic - inhibits cell wall synthesis',
            'standard_dosage': '500 mg three times daily',
            'max_daily_dose': '3000 mg',
            'half_life': '1-1.3 hours',
            'bioavailability': '90%',
            'pregnancy_category': 'B',
            'pediatric_dosage': '20-40 mg/kg/day divided',
            'geriatric_considerations': 'Adjust for renal function',
            'renal_adjustment': 'Reduce dose if CrCl <30',
            'hepatic_adjustment': 'No adjustment needed',
            'common_side_effects': 'Diarrhea, nausea, rash',
            'serious_adverse_effects': 'Anaphylaxis, C. diff colitis',
            'monitoring_parameters': 'Signs of allergic reaction, GI symptoms',
            'cost_tier': 'Tier 1'
        },
        {
            'name': 'Azithromycin',
            'generic_name': 'azithromycin',
            'therapeutic_class': 'Macrolide Antibiotic',
            'mechanism': 'Protein synthesis inhibitor',
            'standard_dosage': '500 mg on day 1, then 250 mg daily for 4 days',
            'max_daily_dose': '500 mg',
            'half_life': '68 hours',
            'bioavailability': '37%',
            'pregnancy_category': 'B',
            'pediatric_dosage': '10 mg/kg on day 1, then 5 mg/kg daily',
            'geriatric_considerations': 'No dose adjustment needed',
            'renal_adjustment': 'No adjustment for mild-moderate impairment',
            'hepatic_adjustment': 'Use with caution',
            'common_side_effects': 'GI upset, diarrhea, abdominal pain',
            'serious_adverse_effects': 'QT prolongation, hepatotoxicity',
            'monitoring_parameters': 'ECG if cardiac risk factors, liver function',
            'cost_tier': 'Tier 2'
        },
        
        # Pain medications
        {
            'name': 'Ibuprofen',
            'generic_name': 'ibuprofen',
            'therapeutic_class': 'NSAID',
            'mechanism': 'COX-1 and COX-2 inhibitor',
            'standard_dosage': '400 mg three times daily',
            'max_daily_dose': '3200 mg',
            'half_life': '2-4 hours',
            'bioavailability': '80-100%',
            'pregnancy_category': 'C (D in 3rd trimester)',
            'pediatric_dosage': '10 mg/kg every 6-8 hours',
            'geriatric_considerations': 'Use lowest effective dose, monitor renal function',
            'renal_adjustment': 'Avoid in severe impairment',
            'hepatic_adjustment': 'Use with caution',
            'common_side_effects': 'GI upset, headache, dizziness',
            'serious_adverse_effects': 'GI bleeding, renal toxicity, CV events',
            'monitoring_parameters': 'Renal function, blood pressure, GI symptoms',
            'cost_tier': 'Tier 1'
        },
        {
            'name': 'Acetaminophen',
            'generic_name': 'acetaminophen',
            'therapeutic_class': 'Analgesic/Antipyretic',
            'mechanism': 'Inhibits COX enzymes in CNS',
            'standard_dosage': '650 mg every 4-6 hours',
            'max_daily_dose': '3000 mg',
            'half_life': '2-3 hours',
            'bioavailability': '85-98%',
            'pregnancy_category': 'B',
            'pediatric_dosage': '10-15 mg/kg every 4-6 hours',
            'geriatric_considerations': 'Consider dose reduction',
            'renal_adjustment': 'Increase dosing interval if CrCl <50',
            'hepatic_adjustment': 'Reduce dose, avoid in severe disease',
            'common_side_effects': 'Generally well tolerated',
            'serious_adverse_effects': 'Hepatotoxicity with overdose',
            'monitoring_parameters': 'Liver function with chronic use',
            'cost_tier': 'Tier 1'
        },
        
        # Gastric medications
        {
            'name': 'Omeprazole',
            'generic_name': 'omeprazole',
            'therapeutic_class': 'Proton Pump Inhibitor',
            'mechanism': 'Irreversibly blocks gastric H+/K+-ATPase',
            'standard_dosage': '20 mg once daily',
            'max_daily_dose': '80 mg',
            'half_life': '0.5-1 hour',
            'bioavailability': '65%',
            'pregnancy_category': 'C',
            'pediatric_dosage': '0.7-3.3 mg/kg once daily',
            'geriatric_considerations': 'No dose adjustment needed',
            'renal_adjustment': 'No adjustment needed',
            'hepatic_adjustment': 'Consider dose reduction',
            'common_side_effects': 'Headache, diarrhea, abdominal pain',
            'serious_adverse_effects': 'C. diff infection, bone fractures',
            'monitoring_parameters': 'Magnesium levels with long-term use',
            'cost_tier': 'Tier 1'
        },
        
        # Anticoagulants
        {
            'name': 'Warfarin',
            'generic_name': 'warfarin',
            'therapeutic_class': 'Anticoagulant',
            'mechanism': 'Vitamin K antagonist',
            'standard_dosage': '5 mg daily initially, then adjust based on INR',
            'max_daily_dose': '15 mg',
            'half_life': '36-42 hours',
            'bioavailability': '100%',
            'pregnancy_category': 'X',
            'pediatric_dosage': '0.1 mg/kg daily initially',
            'geriatric_considerations': 'Start with 2.5 mg daily',
            'renal_adjustment': 'No dose adjustment needed',
            'hepatic_adjustment': 'Use with extreme caution',
            'common_side_effects': 'Bleeding, bruising',
            'serious_adverse_effects': 'Major bleeding, skin necrosis',
            'monitoring_parameters': 'INR, signs of bleeding',
            'cost_tier': 'Tier 1'
        }
    ]
    
    # Insert drugs into database
    for drug in essential_drugs:
        cursor.execute('''
            INSERT OR REPLACE INTO drugs (
                name, generic_name, therapeutic_class, mechanism, standard_dosage,
                max_daily_dose, half_life, bioavailability, pregnancy_category,
                pediatric_dosage, geriatric_considerations, renal_adjustment,
                hepatic_adjustment, common_side_effects, serious_adverse_effects,
                monitoring_parameters, cost_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            drug['name'], drug['generic_name'], drug['therapeutic_class'],
            drug['mechanism'], drug['standard_dosage'], drug['max_daily_dose'],
            drug['half_life'], drug['bioavailability'], drug['pregnancy_category'],
            drug['pediatric_dosage'], drug['geriatric_considerations'],
            drug['renal_adjustment'], drug['hepatic_adjustment'],
            drug['common_side_effects'], drug['serious_adverse_effects'],
            drug['monitoring_parameters'], drug['cost_tier']
        ))

def populate_drug_interactions(cursor: sqlite3.Cursor):
    """Populate database with common drug interactions"""
    
    # First, let's get drug IDs
    cursor.execute("SELECT id, name FROM drugs")
    drug_ids = {name.lower(): id for id, name in cursor.fetchall()}
    
    interactions = [
        {
            'drug1': 'warfarin',
            'drug2': 'ibuprofen',
            'severity': 'High',
            'risk_level': 'High',
            'mechanism': 'Additive bleeding risk',
            'description': 'NSAIDs increase bleeding risk when combined with anticoagulants',
            'clinical_significance': 'High - increased risk of bleeding',
            'recommendation': 'Avoid combination. Use acetaminophen for pain relief instead.',
            'monitoring_required': 1
        },
        {
            'drug1': 'lisinopril',
            'drug2': 'ibuprofen',
            'severity': 'Moderate',
            'risk_level': 'Moderate',
            'mechanism': 'NSAIDs may reduce ACE inhibitor effectiveness',
            'description': 'NSAIDs can reduce antihypertensive effect and increase hyperkalemia risk',
            'clinical_significance': 'Moderate - monitor blood pressure and potassium',
            'recommendation': 'Monitor blood pressure and serum potassium closely',
            'monitoring_required': 1
        },
        {
            'drug1': 'atorvastatin',
            'drug2': 'azithromycin',
            'severity': 'Moderate',
            'risk_level': 'Moderate',
            'mechanism': 'CYP3A4 inhibition',
            'description': 'Azithromycin may increase statin levels, increasing risk of myopathy',
            'clinical_significance': 'Moderate - increased risk of muscle toxicity',
            'recommendation': 'Monitor for muscle pain and consider temporary statin discontinuation',
            'monitoring_required': 1
        },
        {
            'drug1': 'metoprolol',
            'drug2': 'amlodipine',
            'severity': 'Low',
            'risk_level': 'Low',
            'mechanism': 'Additive hypotensive effects',
            'description': 'Both drugs lower blood pressure - additive effect possible',
            'clinical_significance': 'Low - manageable with monitoring',
            'recommendation': 'Monitor blood pressure and adjust doses as needed',
            'monitoring_required': 1
        },
        {
            'drug1': 'omeprazole',
            'drug2': 'metformin',
            'severity': 'Low',
            'risk_level': 'Low',
            'mechanism': 'Potential absorption changes',
            'description': 'PPIs may affect vitamin B12 absorption, which could interact with metformin',
            'clinical_significance': 'Low - monitor B12 levels',
            'recommendation': 'Monitor vitamin B12 levels with long-term use',
            'monitoring_required': 0
        }
    ]
    
    for interaction in interactions:
        drug1_id = drug_ids.get(interaction['drug1'])
        drug2_id = drug_ids.get(interaction['drug2'])
        
        if drug1_id and drug2_id:
            cursor.execute('''
                INSERT OR REPLACE INTO drug_interactions (
                    drug1_id, drug2_id, severity, risk_level, mechanism,
                    description, clinical_significance, recommendation, monitoring_required
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                drug1_id, drug2_id, interaction['severity'], interaction['risk_level'],
                interaction['mechanism'], interaction['description'],
                interaction['clinical_significance'], interaction['recommendation'],
                interaction['monitoring_required']
            ))

def populate_drug_indications(cursor: sqlite3.Cursor):
    """Populate database with drug indications"""
    
    cursor.execute("SELECT id, name FROM drugs")
    drug_ids = {name.lower(): id for id, name in cursor.fetchall()}
    
    indications = [
        ('lisinopril', 'Hypertension', 1),
        ('lisinopril', 'Heart Failure', 1),
        ('lisinopril', 'Post-MI Cardioprotection', 0),
        ('metoprolol', 'Hypertension', 1),
        ('metoprolol', 'Angina', 1),
        ('metoprolol', 'Heart Failure', 0),
        ('amlodipine', 'Hypertension', 1),
        ('amlodipine', 'Angina', 1),
        ('metformin', 'Type 2 Diabetes', 1),
        ('metformin', 'Prediabetes', 0),
        ('atorvastatin', 'Hyperlipidemia', 1),
        ('atorvastatin', 'Cardiovascular Risk Reduction', 0),
        ('amoxicillin', 'Bacterial Infections', 1),
        ('amoxicillin', 'Strep Throat', 0),
        ('azithromycin', 'Respiratory Tract Infections', 1),
        ('azithromycin', 'Skin Infections', 0),
        ('ibuprofen', 'Pain', 1),
        ('ibuprofen', 'Inflammation', 1),
        ('acetaminophen', 'Pain', 1),
        ('acetaminophen', 'Fever', 1),
        ('omeprazole', 'GERD', 1),
        ('omeprazole', 'Peptic Ulcer Disease', 1),
        ('warfarin', 'Atrial Fibrillation', 1),
        ('warfarin', 'Deep Vein Thrombosis', 1),
        ('warfarin', 'Pulmonary Embolism', 1)
    ]
    
    for drug_name, indication, is_primary in indications:
        drug_id = drug_ids.get(drug_name)
        if drug_id:
            cursor.execute('''
                INSERT OR REPLACE INTO drug_indications (drug_id, indication, primary_indication)
                VALUES (?, ?, ?)
            ''', (drug_id, indication, is_primary))

def populate_drug_contraindications(cursor: sqlite3.Cursor):
    """Populate database with drug contraindications"""
    
    cursor.execute("SELECT id, name FROM drugs")
    drug_ids = {name.lower(): id for id, name in cursor.fetchall()}
    
    contraindications = [
        ('lisinopril', 'Pregnancy', 'High', 'Teratogenic - can cause fetal harm'),
        ('lisinopril', 'Angioedema History', 'High', 'Risk of recurrent angioedema'),
        ('lisinopril', 'Severe Renal Impairment', 'Moderate', 'Risk of hyperkalemia and worsening renal function'),
        ('metoprolol', 'Asthma', 'High', 'Risk of bronchospasm'),
        ('metoprolol', 'Heart Block', 'High', 'Can worsen conduction abnormalities'),
        ('metoprolol', 'Severe Heart Failure', 'Moderate', 'May worsen acute decompensated heart failure'),
        ('atorvastatin', 'Pregnancy', 'High', 'Teratogenic effects'),
        ('atorvastatin', 'Active Liver Disease', 'High', 'Risk of hepatotoxicity'),
        ('atorvastatin', 'Myopathy History', 'Moderate', 'Increased risk of recurrent muscle toxicity'),
        ('metformin', 'Severe Renal Impairment', 'High', 'Risk of lactic acidosis'),
        ('metformin', 'Liver Disease', 'High', 'Risk of lactic acidosis'),
        ('metformin', 'Heart Failure', 'Moderate', 'Increased risk of lactic acidosis'),
        ('warfarin', 'Pregnancy', 'High', 'Teratogenic and bleeding risk'),
        ('warfarin', 'Active Bleeding', 'High', 'Will worsen bleeding'),
        ('warfarin', 'Severe Liver Disease', 'High', 'Impaired metabolism and increased bleeding risk'),
        ('amoxicillin', 'Penicillin Allergy', 'High', 'Risk of anaphylaxis'),
        ('amoxicillin', 'Mononucleosis', 'Moderate', 'Increased risk of rash'),
        ('ibuprofen', 'Aspirin Allergy', 'High', 'Cross-reactivity risk'),
        ('ibuprofen', 'Active GI Bleeding', 'High', 'Will worsen bleeding'),
        ('ibuprofen', 'Severe Heart Failure', 'Moderate', 'May worsen fluid retention'),
        ('amlodipine', 'Severe Aortic Stenosis', 'Moderate', 'May cause dangerous hypotension')
    ]
    
    for drug_name, contraindication, severity, reason in contraindications:
        drug_id = drug_ids.get(drug_name)
        if drug_id:
            cursor.execute('''
                INSERT OR REPLACE INTO drug_contraindications (drug_id, contraindication, severity, reason)
                VALUES (?, ?, ?, ?)
            ''', (drug_id, contraindication, severity, reason))

if __name__ == "__main__":
    success = initialize_database()
    if success:
        print("Database initialization completed successfully!")
    else:
        print("Database initialization failed!")
