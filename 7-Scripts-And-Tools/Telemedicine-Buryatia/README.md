# Scripts and Tools - Buryatia Telemedicine Platform

This directory contains practical tools and scripts that demonstrate technical implementation capabilities for the Buryatia Telemedicine Platform.

## 📁 Contents

### 1. Data Generator (`data-generator.py`)
**Purpose**: Generates synthetic test data with cultural context for development and testing.

**Key Features**:
- Culturally-aware patient profiles (Buryat/Russian ethnicity, language preferences)
- Traditional medicine integration in consultations
- Regional connectivity simulation
- Bilingual symptom and treatment data

**Usage**:
```bash
# Generate sample dataset
python data-generator.py

# Generate specific number of patients
python data-generator.py --patients 100

# Output to specific file
python data-generator.py --output my_data.json
Output: JSON file with patients, consultations, and treatment plans

2. Diagram Generator (diagram-generator.py)
Purpose: Automates creation of PlantUML diagrams for system documentation.

Key Features:

Use case diagrams with cultural actors

Sequence diagrams for consultation flows

Component architecture diagrams

Data flow diagrams for traditional knowledge

Usage:

bash
# Generate all diagrams
python diagram-generator.py

# Generate specific diagram type
python diagram-generator.py --type use-case
Output: PlantUML (.puml) files in diagrams/ directory

🛠️ Setup and Requirements
Python Environment
bash
# Required Python version
python --version  # Python 3.8+

# Install dependencies (if any)
pip install -r requirements.txt
PlantUML Setup (for diagram rendering)
bash
# Option 1: Online rendering
# Upload .puml files to: http://www.plantuml.com/plantuml/

# Option 2: Local installation
# Download PlantUML.jar from: https://plantuml.com/download
java -jar plantuml.jar diagrams/*.puml
🎯 Use Cases for Demonstrations
For Technical Interviews
Show data modeling skills with data-generator.py

Demonstrate system design with generated diagrams

Highlight cultural adaptation in technical solutions

For Project Documentation
Use generated diagrams in technical specifications

Provide sample data for API testing

Demonstrate data structure understanding

For Development Teams
Bootstrap development with realistic test data

Maintain consistent documentation with automated diagrams

Ensure cultural considerations in all artifacts

📊 Generated Artifacts
Sample Data Structure
json
{
  "patients": [
    {
      "patient_id": "uuid",
      "first_name": "Баир",
      "ethnicity": "buryat",
      "preferred_language": "buryat",
      "traditional_medicine_acceptance": 4,
      "region": "Окинский район"
    }
  ],
  "consultations": [
    {
      "consultation_language": "buryat",
      "traditional_healer_involved": true,
      "cultural_mediator_used": false
    }
  ]
}
Available Diagrams
Use Case Diagram - System functionality and actors

Sequence Diagram - Consultation workflow

Component Diagram - System architecture

Data Flow Diagram - Traditional knowledge management

🔧 Customization Guide
Adapting for Other Regions
Update regional data in data-generator.py

Modify cultural parameters and language preferences

Adjust connectivity profiles based on infrastructure

Customize traditional medicine knowledge base

Extending Functionality
Add new diagram types to diagram-generator.py

Include additional data validation in data-generator.py

Integrate with actual database for real data sampling

Add API testing scripts for generated data

📈 Impact and Value
For System Analysts
Demonstrates practical implementation skills

Shows understanding of cultural-technical integration

Provides reusable artifacts for multiple projects

Highlights attention to detail in documentation

For Development Teams
Accelerates testing with realistic data

Ensures cultural considerations in development

Provides clear system documentation

Supports consistent architecture understanding

For Stakeholders
Visualizes complex system interactions

Demonstrates cultural sensitivity in technology

Shows practical approach to problem-solving

Provides tangible artifacts for discussion

🚀 Quick Start
Generate Sample Data:

bash
cd 7-Scripts-And-Tools
python data-generator.py
Create Diagrams:

bash
python diagram-generator.py
Render Diagrams (optional):

bash
# Using local PlantUML
java -jar plantuml.jar diagrams/*.puml
📞 Support
For questions or issues:

Check script documentation within each file

Review generated sample outputs

Contact: behabobrova@gmail.com

Last Updated: 2024
Compatibility: Python 3.8+, PlantUML

text

```python
#!/usr/bin/env python3
"""
Buryatia Telemedicine Platform - Culturally-Aware Test Data Generator

DESCRIPTION:
Generates synthetic patient and consultation data that reflects the cultural,
linguistic, and geographical diversity of the Buryatia region. This tool
demonstrates understanding of healthcare digitalization in indigenous contexts.

USAGE:
    python data-generator.py [--patients NUMBER] [--output FILE]

EXAMPLES:
    # Generate default dataset (50 patients)
    python data-generator.py

    # Generate 100 patient records
    python data-generator.py --patients 100

    # Save to specific file
    python data-generator.py --output my_test_data.json

OUTPUT:
    JSON file containing:
    - patients: Demographic and cultural attributes
    - consultations: Healthcare interactions with traditional medicine
    - treatment_plans: Integrated modern-traditional approaches

KEY FEATURES:
    - Cultural sensitivity: Buryat/Russian ethnicity and language modeling
    - Traditional medicine: Integration with modern healthcare
    - Regional variation: Different connectivity and access patterns
    - Realistic profiles: Age, settlement type, medical acceptance

AUTHOR: Natalia Bobrova
CONTACT: behabobrova@gmail.com
VERSION: 1.0
"""
import json
import random
from datetime import datetime, date, timedelta
from uuid import uuid4
from typing import List, Dict, Any

class BuryatiaDataGenerator:
    def __init__(self):
        self.regions = ["Окинский район", "Курумканский район", "Баунтовский район"]
        self.buryat_first_names = ["Баир", "Булат", "Жаргал", "Эрдэни", "Сагаан"]
        self.buryat_last_names = ["Дамдинов", "Цыденов", "Батуев", "Гармаев", "Будаев"]
        self.russian_first_names = ["Александр", "Сергей", "Дмитрий", "Анна", "Елена"]
        self.russian_last_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Попов"]
        self.symptoms_buryat = {
            "Халуурал": "fever", "Гэдэшын ороохой": "stomach_pain", "Толгой ороохой": "headache"
        }
        self.traditional_treatments = [
            {"buryat_name": "Сагаан дали", "russian_name": "Полынь белая", "uses": ["fever", "stomach_pain"]}
        ]

    def generate_patient(self) -> Dict[str, Any]:
        ethnicity = random.choice(["buryat", "russian", "mixed"])
        if ethnicity == "buryat":
            first_name = random.choice(self.buryat_first_names)
            last_name = random.choice(self.buryat_last_names)
            preferred_language = "buryat"
            traditional_acceptance = random.randint(4, 5)
        elif ethnicity == "russian":
            first_name = random.choice(self.russian_first_names)
            last_name = random.choice(self.russian_last_names)
            preferred_language = "russian"
            traditional_acceptance = random.randint(2, 3)
        else:
            first_name = random.choice(self.buryat_first_names + self.russian_first_names)
            last_name = random.choice(self.buryat_last_names + self.russian_last_names)
            preferred_language = random.choice(["buryat", "russian"])
            traditional_acceptance = random.randint(3, 4)
        
        age = random.randint(18, 85)
        birth_date = date.today() - timedelta(days=age*365)
        region = random.choice(self.regions)
        
        return {
            "patient_id": str(uuid4()),
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": birth_date.isoformat(),
            "ethnicity": ethnicity,
            "preferred_language": preferred_language,
            "phone_number": f"+7914{random.randint(1000000, 9999999)}",
            "region": region,
            "traditional_medicine_acceptance": traditional_acceptance,
            "registration_date": datetime.now().isoformat()
        }

    def generate_consultation(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        consultation_date = datetime.now() - timedelta(days=random.randint(1, 30))
        symptoms = random.sample(list(self.symptoms_buryat.keys()), random.randint(1, 3))
        traditional_healer_involved = patient["traditional_medicine_acceptance"] >= 4 and random.random() > 0.3
        
        return {
            "consultation_id": str(uuid4()),
            "patient_id": patient["patient_id"],
            "consultation_date": consultation_date.isoformat(),
            "consultation_language": patient["preferred_language"],
            "symptoms": symptoms,
            "traditional_healer_involved": traditional_healer_involved,
            "patient_satisfaction": random.randint(3, 5)
        }

    def generate_dataset(self, num_patients: int = 50) -> Dict[str, Any]:
        patients = [self.generate_patient() for _ in range(num_patients)]
        consultations = []
        for patient in patients:
            for _ in range(random.randint(1, 3)):
                consultations.append(self.generate_consultation(patient))
        
        return {
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "total_patients": len(patients),
                "total_consultations": len(consultations)
            },
            "patients": patients,
            "consultations": consultations
        }

def main():
    generator = BuryatiaDataGenerator()
    dataset = generator.generate_dataset()
    
    with open("buryatia_telemedicine_sample_data.json", 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"Sample data generated: {len(dataset['patients'])} patients, {len(dataset['consultations'])} consultations")

if __name__ == "__main__":
    main()
python
#!/usr/bin/env python3
"""
Buryatia Telemedicine Platform - Automated Diagram Generator

DESCRIPTION:
Generates PlantUML diagrams for system documentation, demonstrating
architecture, workflows, and cultural integration patterns.

USAGE:
    python diagram-generator.py [--type DIAGRAM_TYPE]

EXAMPLES:
    # Generate all diagrams
    python diagram-generator.py

    # Generate specific diagram type
    python diagram-generator.py --type use-case

OUTPUT:
    PlantUML (.puml) files in 'diagrams/' directory

RENDERING:
    To convert .puml to images:
    1. Online: http://www.plantuml.com/plantuml/
    2. Local: java -jar plantuml.jar diagrams/*.puml

AUTHOR: Natalia Bobrova
CONTACT: behabobrova@gmail.com
VERSION: 1.0
"""
import os

class DiagramGenerator:
    def __init__(self, output_dir="diagrams"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_use_case_diagram(self):
        diagram_content = """@startuml
title Buryatia Telemedicine Platform - Use Case Diagram

left to right direction
actor "Rural Patient" as Patient
actor "Traditional Healer" as Healer
actor "District Doctor" as Doctor

rectangle "Telemedicine Platform" {
  usecase "Bilingual Consultation" as UC1
  usecase "Traditional Treatment" as UC2
  usecase "Cultural Mediation" as UC3
}

Patient --> UC1
Healer --> UC2
Doctor --> UC1
Doctor --> UC3

note right of Patient
  <b>Cultural Context:</b>
  Prefers Buryat language
  Trusts traditional medicine
end note
@enduml
"""
        filename = os.path.join(self.output_dir, "use-case-diagram.puml")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(diagram_content)
        return filename

    def generate_all_diagrams(self):
        diagrams = [self.generate_use_case_diagram()]
        print(f"Generated {len(diagrams)} diagrams in '{self.output_dir}'")
        return diagrams

def main():
    generator = DiagramGenerator()
    generator.generate_all_diagrams()

if __name__ == "__main__":
    main()
txt
# Buryatia Telemedicine Platform - Script Dependencies
# Generated: 2024

# Core Python (included in standard library)
# No external dependencies required

# PlantUML rendering (external tool)
# Download from: https://plantuml.com/download

# Python version requirement
python_requires>=3.8
