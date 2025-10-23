#!/usr/bin/env python3
"""
Buryatia Telemedicine - Diagram Generator
Generates PlantUML diagrams for system documentation
"""

import os
from datetime import datetime

class DiagramGenerator:
    """Generates various PlantUML diagrams for the telemedicine platform"""
    
    def __init__(self, output_dir="diagrams"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_use_case_diagram(self):
        """Generate use case diagram showing system functionality"""
        
        diagram_content = """@startuml
!define BPMN
title Buryatia Telemedicine Platform - Use Case Diagram

left to right direction

actor "Rural Patient" as Patient
actor "Traditional Healer" as Healer
actor "District Doctor" as Doctor
actor "Cultural Mediator" as Mediator
actor "System Administrator" as Admin

rectangle "Telemedicine Platform" {
  usecase "Bilingual Consultation" as UC1
  usecase "Traditional Treatment Advice" as UC2
  usecase "Cultural Mediation" as UC3
  usecase "Low-bandwidth Video Call" as UC4
  usecase "Offline Data Synchronization" as UC5
  usecase "Ethnic Health Analytics" as UC6
  usecase "Traditional Knowledge Management" as UC7
  usecase "Multi-language Content Management" as UC8
  
  UC5 .> UC1 : <<extend>>
  UC5 .> UC4 : <<extend>>
  UC3 .> UC1 : <<include>>
  UC3 .> UC2 : <<include>>
}

Patient --> UC1
Patient --> UC4
Patient --> UC5

Healer --> UC2
Healer --> UC7

Doctor --> UC1
Doctor --> UC6

Mediator --> UC3
Mediator --> UC8

Admin --> UC7
Admin --> UC8

note right of Patient
  <b>Cultural Context:</b>
  Prefers Buryat language
  Limited digital literacy
  Trusts traditional medicine
end note

note left of Healer  
  <b>Role:</b>
  Traditional knowledge holder
  Cultural validation
  Community trust bridge
end note

@enduml
"""
        
        filename = os.path.join(self.output_dir, "use-case-diagram.puml")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(diagram_content)
        
        print(f"Use case diagram generated: {filename}")
        return filename
    
    def generate_sequence_diagram(self):
        """Generate sequence diagram for consultation flow"""
        
        diagram_content = """@startuml
title Buryatia Telemedicine - Consultation Sequence Diagram

actor Patient as P
participant "Mobile App" as App
participant "Cultural Mediator" as CM
participant "Medical Doctor" as MD
participant "Traditional Healer" as TH
database "Medical Records" as DB

group Bilingual Consultation Setup
  P -> App: Access app (Buryat language)
  App -> CM: Request cultural mediation\n(if needed)
  CM -> App: Provide language/cultural support
  App -> P: Display bilingual interface
end

group Symptom Assessment
  P -> App: Describe symptoms in Buryat
  App -> App: Translate to Russian\nfor medical system
  App -> DB: Store symptoms with\ncultural context
  App -> MD: Send consultation request\nwith translation
end

group Integrated Consultation
  MD -> App: Start video consultation
  App -> P: Connect with quality\nadaptation
  
  alt Traditional Medicine Requested
    P -> App: Request traditional healer
    App -> TH: Invite to consultation
    TH -> App: Join consultation
    MD -> TH: Discuss traditional options
    TH -> MD: Provide traditional\ntreatment advice
  end
  
  MD -> App: Create integrated\ntreatment plan
  App -> DB: Store plan with\ncompatibility data
end

group Post-Consultation
  App -> P: Provide bilingual\ntreatment instructions
  App -> P: Set medication reminders\nin Buryat
  App -> DB: Update patient records\nin both languages
  
  loop Weekly Follow-up
    App -> P: Send progress check-in\nin preferred language
    P -> App: Report symptoms/adherence
    App -> MD: Update treatment progress
  end
end

@enduml
"""
        
        filename = os.path.join(self.output_dir, "consultation-sequence-diagram.puml")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(diagram_content)
        
        print(f"Sequence diagram generated: {filename}")
        return filename
    
    def generate_component_diagram(self):
        """Generate component diagram showing system architecture"""
        
        diagram_content = """@startuml
title Buryatia Telemedicine Platform - Component Architecture

package "Frontend Applications" {
  [Mobile App] as Mobile
  [Web Portal] as Web
  [Admin Dashboard] as Admin
}

package "API Gateway" {
  [Bilingual API Gateway] as Gateway
}

package "Core Services" {
  [Patient Service] as PatientSvc
  [Consultation Service] as ConsultSvc
  [Medical Records Service] as RecordsSvc
}

package "Traditional Medicine" {
  [Traditional Knowledge Base] as KnowledgeBase
  [Treatment Compatibility Engine] as Compatibility
  [Cultural Validation Service] as CulturalSvc
}

package "Multilingual System" {
  [Translation Service] as TranslateSvc
  [Voice Interface Service] as VoiceSvc
  [Content Management] as ContentSvc
}

package "Data Storage" {
  [Patient Database] as PatientDB
  [Medical Records DB] as MedicalDB
  [Traditional Knowledge DB] as TraditionalDB
  [Multilingual Content DB] as ContentDB
}

' Connections
Mobile --> Gateway : HTTPS/JSON
Web --> Gateway : HTTPS/JSON
Admin --> Gateway : HTTPS/JSON

Gateway --> PatientSvc : Service Calls
Gateway --> ConsultSvc : Service Calls  
Gateway --> RecordsSvc : Service Calls

ConsultSvc --> KnowledgeBase : Traditional Advice
ConsultSvc --> Compatibility : Check Treatments
RecordsSvc --> CulturalSvc : Validate Content

PatientSvc --> TranslateSvc : Language Preference
ConsultSvc --> VoiceSvc : Buryat Voice
ContentSvc --> TranslateSvc : Content Translation

PatientSvc --> PatientDB : CRUD Operations
RecordsSvc --> MedicalDB : Medical Data
KnowledgeBase --> TraditionalDB : Traditional Knowledge
ContentSvc --> ContentDB : Multilingual Content

note right of Mobile
  <b>Cultural Features:</b>
  - Buryat/Russian language
  - Voice interface
  - Offline capability
  - Traditional medicine options
end note

note left of KnowledgeBase
  <b>Traditional Medicine:</b>
  - IP protection
  - Cultural validation
  - Benefit sharing
  - Community control
end note

@enduml
"""
        
        filename = os.path.join(self.output_dir, "component-architecture-diagram.puml")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(diagram_content)
        
        print(f"Component diagram generated: {filename}")
        return filename
    
    def generate_data_flow_diagram(self):
        """Generate data flow diagram for traditional knowledge"""
        
        diagram_content = """@startuml
title Traditional Knowledge Data Flow

actor "Traditional Healer" as Healer
participant "Cultural Mediator" as Mediator
participant "Knowledge Base" as KB
participant "Medical Doctor" as Doctor
participant "Patient" as Patient
database "Audit Log" as Audit

== Knowledge Contribution ==

group Cultural Validation
  Healer -> Mediator: Share traditional knowledge
  Mediator -> Mediator: Document cultural context
  Mediator -> KB: Submit for validation
  KB -> KB: Store with access controls
  KB -> Audit: Log contribution with metadata
end

group Benefit Sharing
  KB -> KB: Track knowledge usage
  KB -> Healer: Provide usage reports
  KB -> Healer: Distribute benefits\n(if applicable)
end

== Knowledge Usage ==

group Consultation Integration
  Doctor -> KB: Search traditional treatments
  KB -> KB: Check access permissions
  KB -> Doctor: Return compatible treatments
  
  Doctor -> Patient: Discuss integrated options
  Patient -> Doctor: Provide consent for\ntraditional treatment
  
  Doctor -> KB: Record treatment application
  KB -> Audit: Log usage with consent data
end

group Outcome Tracking
  Patient -> Doctor: Report treatment outcomes
  Doctor -> KB: Update effectiveness data
  KB -> KB: Aggregate outcome statistics
  KB -> Healer: Share outcome feedback
end

== Knowledge Preservation ==

group Cultural Continuity
  KB -> KB: Regular cultural review
  KB -> Mediator: Request content validation
  Mediator -> KB: Update cultural context
  KB -> KB: Version control for changes
  KB -> Audit: Maintain change history
end

note right of Healer
  <b>Rights Protected:</b>
  - Intellectual property
  - Cultural context
  - Benefit sharing
  - Usage control
end note

note left of KB
  <b>Security Features:</b>
  - Granular access control
  - Usage tracking
  - Cultural sensitivity levels
  - Audit logging
end note

@enduml
"""
        
        filename = os.path.join(self.output_dir, "data-flow-diagram.puml")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(diagram_content)
        
        print(f"Data flow diagram generated: {filename}")
        return filename
    
    def generate_all_diagrams(self):
        """Generate all diagrams"""
        print("Generating all PlantUML diagrams for Buryatia Telemedicine...")
        
        diagrams = [
            self.generate_use_case_diagram(),
            self.generate_sequence_diagram(), 
            self.generate_component_diagram(),
            self.generate_data_flow_diagram()
        ]
        
        print(f"\nGenerated {len(diagrams)} diagrams in '{self.output_dir}' directory")
        print("\nTo render these diagrams, use:")
        print("1. PlantUML online server: http://www.plantuml.com/plantuml/")
        print("2. Local PlantUML installation: java -jar plantuml.jar *.puml")
        print("3. VS Code PlantUML extension")
        
        return diagrams

def main():
    """Main function to generate all diagrams"""
    generator = DiagramGenerator()
    generator.generate_all_diagrams()

if __name__ == "__main__":
    main()
