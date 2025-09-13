# Overview

This is an AI-powered medical prescription verification system built with Python and Streamlit. The application provides comprehensive drug interaction checking, dosage recommendations, and alternative medication suggestions for healthcare professionals. The system leverages machine learning models (IBM Granite) for natural language processing of prescription text and maintains a comprehensive drug database for safety analysis.

The system analyzes patient profiles, medical conditions, and prescribed medications to identify potential contraindications, drug interactions, and provide age-specific dosage recommendations with safety scoring.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application framework
- **UI Components**: Interactive forms for patient data input, prescription text analysis, and results visualization
- **Visualization**: Plotly charts for safety scores and drug interaction analysis
- **State Management**: Streamlit session state for maintaining user data across interactions

## Backend Architecture
- **Modular Design**: Component-based architecture with separate modules for each major functionality
- **Core Components**:
  - `DrugDatabase`: SQLite database operations and drug information retrieval
  - `NLPProcessor`: Natural language processing for prescription text extraction
  - `InteractionChecker`: Drug-drug interaction analysis and safety assessment
  - `DosageRecommender`: Age and condition-specific dosage calculations
  - `AlternativeFinder`: Therapeutic alternative medication suggestions
  - `PatientProfile`: Patient data modeling and validation

## Data Storage
- **Database**: SQLite database for drug information, interactions, contraindications, and indications
- **Schema Design**: Normalized tables for drugs, drug interactions, contraindications, and therapeutic classifications
- **Initialization**: Automated database setup with essential drug data population

## Natural Language Processing
- **Primary Model**: IBM Granite 3.3-2B model via Hugging Face API for prescription text analysis
- **Fallback Strategy**: Rule-based regex patterns for drug name, dosage, and frequency extraction
- **Processing Pipeline**: Text preprocessing, entity extraction, and structured data conversion

## Safety and Validation
- **Drug Interaction Matrix**: Comprehensive interaction checking across therapeutic classes
- **Dosage Validation**: Age-based, weight-based, and condition-specific dosage adjustments
- **Safety Scoring**: Algorithmic safety assessment with visual indicators
- **Input Validation**: Patient profile validation and data sanitization

# External Dependencies

## Machine Learning Services
- **Hugging Face API**: IBM Granite model access for natural language processing
- **API Integration**: RESTful API calls with fallback mechanisms

## Python Libraries
- **Streamlit**: Web application framework for user interface
- **Plotly**: Data visualization for charts and graphs
- **Pandas**: Data manipulation and analysis
- **SQLite3**: Built-in database connectivity
- **Requests**: HTTP client for external API calls

## Database
- **SQLite**: Embedded database for drug information storage
- **Local Storage**: File-based database requiring no external database server

## Data Sources
- **Drug Information**: Pre-populated essential drug database with therapeutic classifications
- **Interaction Data**: Comprehensive drug interaction matrices
- **Clinical Guidelines**: Age-specific and condition-specific dosing recommendations
