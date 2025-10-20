CREATE TABLE patients (
    patient_id UUID PRIMARY KEY,
    -- Стандартные поля
    first_name VARCHAR,
    last_name VARCHAR,
    
    -- Уникальные для методологии EDHF
    ethnicity VARCHAR, -- бурят, русский, etc
    traditional_medicine_preferences JSONB, -- предпочтения к народной медицине
    language_preference VARCHAR DEFAULT 'buryat', -- бурятский язык интерфейса
    remote_area_connectivity_level INTEGER -- уровень доступа к интернету
);
