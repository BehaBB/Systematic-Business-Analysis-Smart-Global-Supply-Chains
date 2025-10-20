-- Patient demographics analysis
SELECT 
    ethnicity,
    AVG(traditional_medicine_acceptance) as avg_acceptance
FROM patients 
GROUP BY ethnicity;
