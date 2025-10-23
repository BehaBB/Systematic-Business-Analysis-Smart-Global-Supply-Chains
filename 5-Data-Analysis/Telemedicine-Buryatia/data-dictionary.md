-- Buryatia Telemedicine Platform - Analytical Queries
-- Cultural and Healthcare Impact Analysis

-- 1. PATIENT DEMOGRAPHICS AND ADOPTION ANALYSIS

-- Patient registration by ethnicity and language preference
SELECT 
    ethnicity,
    preferred_language,
    COUNT(*) as patient_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM patients 
GROUP BY ethnicity, preferred_language
ORDER BY patient_count DESC;

-- Traditional medicine acceptance by age group and region
SELECT 
    CASE 
        WHEN EXTRACT(YEAR FROM AGE(date_of_birth)) < 30 THEN 'Under 30'
        WHEN EXTRACT(YEAR FROM AGE(date_of_birth)) < 50 THEN '30-49'
        WHEN EXTRACT(YEAR FROM AGE(date_of_birth)) < 70 THEN '50-69'
        ELSE '70+'
    END as age_group,
    settlement_type,
    ROUND(AVG(traditional_medicine_acceptance), 2) as avg_acceptance,
    COUNT(*) as patient_count
FROM patients
GROUP BY age_group, settlement_type
ORDER BY age_group, avg_acceptance DESC;

-- 2. CONSULTATION EFFECTIVENESS ANALYSIS

-- Consultation success rates by connection quality and language
SELECT 
    consultation_language,
    CASE 
        WHEN connection_quality = 5 THEN 'Excellent'
        WHEN connection_quality >= 3 THEN 'Good'
        ELSE 'Poor'
    END as connection_quality,
    COUNT(*) as total_consultations,
    SUM(CASE WHEN consultation_duration > 300 THEN 1 ELSE 0 END) as successful_consultations,
    ROUND(SUM(CASE WHEN consultation_duration > 300 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM consultations 
WHERE consultation_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY consultation_language, connection_quality
ORDER BY consultation_language, success_rate DESC;

-- Traditional healer involvement impact on patient satisfaction
SELECT 
    CASE WHEN traditional_healer_involved THEN 'With Traditional Healer' ELSE 'Modern Only' END as consultation_type,
    COUNT(*) as consultation_count,
    ROUND(AVG(patient_satisfaction), 2) as avg_satisfaction,
    ROUND(AVG(consultation_duration), 2) as avg_duration_minutes
FROM consultations
GROUP BY traditional_healer_involved
ORDER BY avg_satisfaction DESC;

-- 3. TRADITIONAL MEDICINE INTEGRATION ANALYSIS

-- Most commonly used traditional treatments by region
SELECT 
    p.region,
    tt.treatment_buryat_name,
    tt.treatment_russian_name,
    COUNT(*) as usage_count,
    ROUND(AVG(tc.compatibility_level), 2) as avg_compatibility
FROM treatment_plans tp
JOIN traditional_treatments tt ON tp.traditional_treatment_id = tt.treatment_id
JOIN treatment_compatibility tc ON tt.treatment_id = tc.traditional_treatment_id
JOIN patients p ON tp.patient_id = p.patient_id
WHERE tp.plan_type = 'integrated'
GROUP BY p.region, tt.treatment_buryat_name, tt.treatment_russian_name
ORDER BY usage_count DESC
LIMIT 20;

-- Traditional medicine effectiveness for common conditions
SELECT 
    mc.condition_name_ru,
    mc.condition_name_buryat,
    tt.treatment_russian_name,
    COUNT(*) as application_count,
    ROUND(AVG(tp.outcome_score), 2) as avg_effectiveness,
    ROUND(AVG(tp.cultural_acceptance_score), 2) as avg_cultural_acceptance
FROM treatment_plans tp
JOIN medical_conditions mc ON tp.condition_id = mc.condition_id
JOIN traditional_treatments tt ON tp.traditional_treatment_id = tt.treatment_id
WHERE tp.outcome_score IS NOT NULL
GROUP BY mc.condition_name_ru, mc.condition_name_buryat, tt.treatment_russian_name
ORDER BY avg_effectiveness DESC
LIMIT 15;

-- 4. LANGUAGE AND CULTURAL IMPACT ANALYSIS

-- Consultation language preference trends over time
SELECT 
    DATE_TRUNC('month', consultation_date) as month,
    consultation_language,
    COUNT(*) as consultation_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY DATE_TRUNC('month', consultation_date)), 2) as monthly_percentage
FROM consultations
WHERE consultation_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY month, consultation_language
ORDER BY month, consultation_language;

-- Cultural mediator usage and impact
SELECT 
    p.region,
    COUNT(*) as total_consultations,
    SUM(CASE WHEN c.cultural_mediator_used THEN 1 ELSE 0 END) as mediator_used,
    ROUND(SUM(CASE WHEN c.cultural_mediator_used THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as mediator_usage_rate,
    ROUND(AVG(CASE WHEN c.cultural_mediator_used THEN c.patient_satisfaction ELSE NULL END), 2) as satisfaction_with_mediator,
    ROUND(AVG(CASE WHEN NOT c.cultural_mediator_used THEN c.patient_satisfaction ELSE NULL END), 2) as satisfaction_without_mediator
FROM consultations c
JOIN patients p ON c.patient_id = p.patient_id
GROUP BY p.region
ORDER BY mediator_usage_rate DESC;

-- 5. ACCESSIBILITY AND HEALTHCARE IMPACT

-- Reduction in patient travel time by region
SELECT 
    p.region,
    p.settlement_type,
    COUNT(*) as patient_count,
    ROUND(AVG(CASE 
        WHEN p.settlement_type = 'remote_settlement' THEN 6.0
        WHEN p.settlement_type = 'rural' THEN 3.0
        ELSE 0.5
    END), 2) as estimated_travel_time_hours_before,
    0.5 as travel_time_hours_after, -- 30 minutes for teleconsultation
    ROUND(AVG(CASE 
        WHEN p.settlement_type = 'remote_settlement' THEN 6.0
        WHEN p.settlement_type = 'rural' THEN 3.0
        ELSE 0.5
    END) - 0.5, 2) as time_saved_hours
FROM patients p
WHERE p.registration_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY p.region, p.settlement_type
ORDER BY time_saved_hours DESC;

-- Healthcare accessibility improvement metrics
SELECT 
    p.region,
    COUNT(DISTINCT p.patient_id) as registered_patients,
    COUNT(DISTINCT c.patient_id) as patients_with_consultations,
    ROUND(COUNT(DISTINCT c.patient_id) * 100.0 / COUNT(DISTINCT p.patient_id), 2) as consultation_rate,
    -- Estimated accessibility before telemedicine (based on regional data)
    CASE 
        WHEN p.region IN ('Окинский', 'Баунтовский') THEN 40.0
        ELSE 60.0
    END as estimated_accessibility_before,
    ROUND(COUNT(DISTINCT c.patient_id) * 100.0 / COUNT(DISTINCT p.patient_id), 2) as accessibility_after
FROM patients p
LEFT JOIN consultations c ON p.patient_id = c.patient_id
    AND c.consultation_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.region
ORDER BY consultation_rate DESC;

-- 6. TRADITIONAL KNOWLEDGE PRESERVATION METRICS

-- Traditional healer engagement and knowledge contribution
SELECT 
    th.healer_type,
    th.region,
    COUNT(DISTINCT th.healer_id) as total_healers,
    COUNT(DISTINCT tk.healer_id) as contributing_healers,
    ROUND(COUNT(DISTINCT tk.healer_id) * 100.0 / COUNT(DISTINCT th.healer_id), 2) as contribution_rate,
    SUM(th.knowledge_contributions) as total_contributions,
    ROUND(AVG(th.community_standing), 2) as avg_community_standing
FROM traditional_healers th
LEFT JOIN traditional_knowledge tk ON th.healer_id = tk.healer_id
GROUP BY th.healer_type, th.region
ORDER BY contribution_rate DESC;

-- Traditional treatment documentation completeness
SELECT 
    tt.treatment_type,
    COUNT(*) as total_treatments,
    SUM(CASE WHEN tt.preparation_method IS NOT NULL THEN 1 ELSE 0 END) as with_preparation_method,
    SUM(CASE WHEN tt.seasonal_availability IS NOT NULL THEN 1 ELSE 0 END) as with_seasonal_info,
    SUM(CASE WHEN tt.regional_variations IS NOT NULL THEN 1 ELSE 0 END) as with_regional_variations,
    SUM(CASE WHEN tt.cultural_significance IS NOT NULL THEN 1 ELSE 0 END) as with_cultural_context,
    ROUND(( 
        (CASE WHEN tt.preparation_method IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN tt.seasonal_availability IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN tt.regional_variations IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN tt.cultural_significance IS NOT NULL THEN 1 ELSE 0 END)
    ) * 100.0 / 4, 2) as documentation_completeness
FROM traditional_treatments tt
GROUP BY tt.treatment_type
ORDER BY documentation_completeness DESC;

-- 7. PERFORMANCE AND TECHNICAL METRICS

-- Platform performance by region and connectivity
SELECT 
    p.region,
    p.settlement_type,
    COUNT(*) as consultation_count,
    ROUND(AVG(c.connection_quality), 2) as avg_connection_quality,
    ROUND(AVG(c.consultation_duration), 2) as avg_duration_minutes,
    SUM(CASE WHEN c.consultation_duration < 60 THEN 1 ELSE 0 END) as short_consultations,
    SUM(CASE WHEN c.consultation_duration >= 60 THEN 1 ELSE 0 END) as normal_consultations,
    ROUND(SUM(CASE WHEN c.consultation_duration >= 60 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as completion_rate
FROM consultations c
JOIN patients p ON c.patient_id = p.patient_id
WHERE c.consultation_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY p.region, p.settlement_type
ORDER BY completion_rate DESC;

-- Monthly growth and adoption metrics
SELECT 
    DATE_TRUNC('month', registration_date) as month,
    COUNT(*) as new_patients,
    SUM(COUNT(*)) OVER(ORDER BY DATE_TRUNC('month', registration_date)) as cumulative_patients,
    COUNT(DISTINCT CASE WHEN preferred_language = 'buryat' THEN patient_id END) as buryat_speakers,
    ROUND(AVG(traditional_medicine_acceptance), 2) as avg_traditional_acceptance
FROM patients
WHERE registration_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY month
ORDER BY month;
