-- Patients with cultural attributes
CREATE TABLE patients (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100),
    ethnicity VARCHAR(50),
    preferred_language VARCHAR(10) DEFAULT 'buryat',
    traditional_medicine_acceptance INTEGER
);
