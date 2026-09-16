{{ config(
    materialized='table',
    tags=['silver', 'acled', 'conflict', 'geospatial', 'ai_enriched']
) }}

/*
  Silver model: ACLED Jordan Events (AI-Enriched)
  
  Transforms raw ACLED API data into cleaned, AI-enriched silver layer.
  
  Transformations:
  - Convert event_date string to DATE type
  - Cast geographic coordinates (lat/lon) to DOUBLE precision
  - Standardize fatalities: NULL -> 0 (using COALESCE)
  - Derive temporal fields (event_month, event_quarter)
  
  AI Enrichments:
  - Primary Cause: AI classification using ai_classify() v2.1 - 11 broad categories with descriptions
  - Primary Cause Confidence: Model confidence score (0-1) for primary classification
  - Specific Primary Cause: Granular AI classification - 62 detailed subcategories with descriptions
  - Specific Primary Cause Confidence: Model confidence score (0-1) for specific classification
  - Global Instructions: Context-specific guidance for Jordan-focused event classification
  - Crowd Size: Extract from tags and convert to integer estimates
  
  Label Descriptions: Each classification label includes a semantic description to improve
  accuracy and reduce ambiguity between similar categories (e.g., utility_privatization vs
  utility_bill protests). Descriptions help the AI understand contextual boundaries.
  
  Derived Analytics:
  - has_fatalities: Boolean flag for events with casualties
  - is_violent: Boolean for violent event types
  - is_peaceful_protest: Boolean for peaceful protests only
  - actor_category: Simplified actor classification
  
  Data Quality:
  - Ensures event_id_cnty is unique (tested in schema.yml)
  - Validates date and disorder_type presence
  - Deduplicates on event_id_cnty
  
  Runtime: ~3-5 minutes (AI classification on 1,300+ events)
  Source: Bronze table from ACLED API ingestion
  Target: Silver layer for conflict/protest analysis
*/

WITH base_data AS (
  SELECT 
    event_id_cnty,
    TO_DATE(event_date) AS event_date,
    year,
    time_precision,
    disorder_type,
    event_type,
    sub_event_type,
    actor1,
    assoc_actor_1,
    inter1,
    actor2,
    assoc_actor_2,
    inter2,
    interaction,
    civilian_targeting,
    iso,
    region,
    country,
    admin1 AS governorate_name,
    admin2 AS town_district_of_governorate,
    admin3,
    location,
    CAST(latitude AS DOUBLE) AS latitude,
    CAST(longitude AS DOUBLE) AS longitude,
    geo_precision,
    source,
    source_scale,
    notes,
    COALESCE(fatalities, 0) AS fatalities,
    tags,
    timestamp
  FROM {{ source('bronze', 'acled_jordan_events') }}
  WHERE event_id_cnty IS NOT NULL
    AND event_date IS NOT NULL
    AND disorder_type IS NOT NULL
),

enriched_data AS (
  SELECT 
    *,
    
    -- Temporal fields
    MONTH(event_date) AS event_month,
    QUARTER(event_date) AS event_quarter,
    
    -- Crowd size extraction from tags
    CASE 
      WHEN tags IS NULL OR tags = '' OR tags LIKE '%no report%' THEN 0
      WHEN tags LIKE '%tens%' OR tags = '10' THEN 10
      WHEN tags LIKE '%dozens%' THEN 30
      WHEN tags LIKE '%hundreds%' THEN 200
      WHEN tags LIKE '%thousands%' THEN 2000
      WHEN TRY_CAST(tags AS INT) IS NOT NULL THEN CAST(tags AS INT)
      ELSE 0
    END AS crowd_size_int,
    
    -- AI Classification: Primary Cause (11 broad categories) with confidence scores and descriptions
    ai_classify(
      notes, 
      '{
        "labor_workers_rights": "Worker strikes, wage disputes, labor protests, union organizing, or employment-related demonstrations",
        "palestinian_solidarity": "Protests supporting Palestine, opposing Israeli actions, Gaza bombardment opposition, or Jerusalem status",
        "government_policy": "Opposition to government decisions, parliament criticism, constitutional changes, judicial reforms, or political demands",
        "economic_grievances": "Protests against prices, inflation, taxes, cost of living, poverty, unemployment, or economic hardship",
        "tribal_violence": "Clan disputes, tribal feuds, honor violence, or inter-family conflicts",
        "education_issues": "School or university protests, student rights, education funding, curriculum disputes, or teacher hiring",
        "healthcare_issues": "Hospital complaints, medical shortages, healthcare access, or health insurance disputes",
        "service_delivery": "Water, electricity, waste, infrastructure, public transport issues, or utility service complaints",
        "violence_other": "Armed clashes, assaults, domestic violence, street violence, or criminal acts",
        "environmental": "Pollution protests, air or water quality complaints, or environmental regulation demands",
        "other": "Events that do not fit the above categories"
      }',
      MAP(
        'version', '2.1',
        'enableConfidenceScores', 'true',
        'instructions', 'Classify Jordanian civil events and protests by their primary cause. Focus on what protesters are demanding or opposing, not just who is involved. Choose the single best-fit category based on the main grievance.'
      )
    ) AS primary_cause_result,
    
    -- AI Classification: Specific Cause (62 granular subcategories) with confidence scores and descriptions
    ai_classify(
      notes,
      '{
        "teacher_strike": "Teachers walking out, striking, or refusing to work over wages, conditions, or policies",
        "healthcare_worker_protest": "Doctors, nurses, or medical staff protesting wages, conditions, or healthcare policies",
        "public_sector_wage_dispute": "Government employees demanding salary increases or protesting wage cuts",
        "private_sector_wage_dispute": "Private company workers demanding pay raises or protesting wage issues",
        "pension_reform_protest": "Opposition to changes in retirement benefits or pension systems",
        "working_conditions_protest": "Protests against unsafe work environments, long hours, or poor conditions",
        "union_organizing": "Labor union formation, collective bargaining efforts, or union rights advocacy",
        "layoff_protest": "Opposition to job cuts, dismissals, or workforce reductions",
        "gaza_bombardment_protest": "Protests specifically against Israeli military attacks on Gaza",
        "jerusalem_status_protest": "Protests concerning Jerusalem sovereignty, Al-Aqsa Mosque, or holy sites",
        "israeli_settlement_opposition": "Opposition to Israeli settlements in Palestinian territories",
        "palestinian_prisoner_support": "Advocacy for release or rights of Palestinians detained by Israel",
        "wadi_araba_agreement_opposition": "Opposition to Jordan-Israel peace treaty or normalization",
        "general_palestinian_solidarity": "Broad support for Palestinian people or opposition to Israeli policies not covered above",
        "amnesty_law_demand": "Calls for pardoning or releasing political prisoners or detainees",
        "parliament_criticism": "Opposition to parliamentary decisions, MPs, or legislative actions",
        "corruption_allegation": "Protests against government corruption, embezzlement, or official misconduct",
        "electoral_reform_demand": "Calls for changes to election laws, voting systems, or democratic processes",
        "free_speech_restriction_protest": "Opposition to censorship, press restrictions, or limits on expression",
        "judicial_reform_protest": "Opposition to changes in court systems, judicial independence, or legal reforms",
        "security_policy_protest": "Opposition to police actions, security laws, or law enforcement policies",
        "cabinet_reshuffle_protest": "Opposition to government appointments, ministerial changes, or cabinet composition",
        "fuel_price_protest": "Opposition to increases in gasoline, diesel, or fuel costs",
        "inflation_protest": "Protests against rising general prices or cost increases across goods",
        "unemployment_protest": "Demands for jobs, opposition to joblessness, or employment creation demands",
        "tax_increase_opposition": "Opposition to new taxes or tax rate increases",
        "subsidy_removal_protest": "Opposition to ending government subsidies on goods or services",
        "cost_of_living_protest": "General protests against high living expenses or economic hardship",
        "poverty_complaint": "Protests highlighting poverty, economic inequality, or wealth gaps",
        "utility_bill_protest": "Protests against high electricity, water, or utility billing costs",
        "utility_privatization_protest": "Opposition to transferring public water, electricity, or utility companies to private ownership",
        "public_service_reform_protest": "Opposition to restructuring or administrative changes in public service delivery",
        "tribal_feud": "Ongoing conflict between tribal families or clans",
        "clan_dispute": "Arguments or fights between family groups or extended kin networks",
        "honor_related_violence": "Violence motivated by family honor, reputation, or social standing",
        "land_dispute_tribal": "Conflicts over land ownership or boundaries between tribal groups",
        "revenge_attack_tribal": "Retaliatory violence following previous tribal incidents",
        "school_closure_protest": "Opposition to closing schools or educational facilities",
        "university_student_protest": "College or university students protesting campus issues, policies, or national concerns",
        "student_rights_protest": "Advocacy for student freedoms, expression, or treatment in educational settings",
        "education_funding_protest": "Demands for increased education budgets or opposition to funding cuts",
        "curriculum_dispute": "Opposition to educational content, textbooks, or teaching materials",
        "exam_policy_protest": "Opposition to testing requirements, exam administration, or grading policies",
        "teacher_hiring_protest": "Demands for teacher employment, contract renewals, or hiring practices",
        "hospital_service_complaint": "Protests against poor medical care quality, hospital conditions, or treatment issues",
        "medical_shortage_protest": "Opposition to lack of medicines, medical supplies, or healthcare equipment",
        "healthcare_access_protest": "Demands for improved access to medical services or healthcare facilities",
        "health_insurance_dispute": "Conflicts over health insurance coverage, costs, or benefits",
        "healthcare_privatization_protest": "Opposition to transferring public hospitals or healthcare to private companies",
        "water_shortage_protest": "Protests due to lack of water supply, water cuts, or inadequate water access",
        "electricity_outage_protest": "Opposition to power cuts, blackouts, or unreliable electricity supply",
        "waste_management_protest": "Protests against poor garbage collection, waste disposal, or sanitation issues",
        "road_infrastructure_complaint": "Demands for road repairs, infrastructure improvements, or maintenance",
        "public_transport_protest": "Protests concerning buses, taxis, fares, or public transportation services",
        "domestic_violence": "Violence within households or between family members",
        "street_violence": "Public fighting, brawls, or altercations in public spaces",
        "gang_related_violence": "Violence involving criminal gangs or organized groups",
        "mob_violence": "Crowd violence, rioting, or large-group attacks",
        "assault": "Physical attacks, beatings, or violent confrontations",
        "water_pollution_protest": "Opposition to contaminated water sources or water quality issues",
        "air_quality_protest": "Protests against air pollution, smog, or atmospheric contamination",
        "industrial_pollution_complaint": "Opposition to factory emissions, industrial waste, or manufacturing pollution",
        "environmental_regulation_demand": "Calls for stronger environmental laws, protections, or enforcement",
        "other_unspecified": "Events that do not fit any of the above specific categories"
      }',
      MAP(
        'version', '2.1',
        'enableConfidenceScores', 'true',
        'instructions', 'Classify Jordanian events into the most specific applicable category. Key distinctions: utility_privatization = transferring public companies to private ownership; utility_bill = protesting high costs; water_shortage = lack of supply. Tribal events involve family/clan conflicts. Palestinian solidarity includes Gaza support and anti-Israeli actions. Focus on the specific grievance mentioned in the event description.'
      )
    ) AS specific_primary_cause_result,
    
    -- Derived analytical flags
    (fatalities > 0) AS has_fatalities,
    
    event_type IN (
      'Riots', 
      'Violence against civilians',
      'Battles',
      'Explosions/Remote violence'
    ) AS is_violent,
    
    (event_type = 'Protests' AND fatalities = 0) AS is_peaceful_protest,
    
    -- Actor category simplification (inter1 can be string or numeric)
    CASE
      WHEN TRY_CAST(inter1 AS INT) IN (1, 2) THEN 'state_forces'
      WHEN TRY_CAST(inter1 AS INT) = 3 THEN 'political_militia'
      WHEN TRY_CAST(inter1 AS INT) = 4 THEN 'identity_militia'
      WHEN TRY_CAST(inter1 AS INT) = 5 THEN 'rioters'
      WHEN TRY_CAST(inter1 AS INT) = 6 THEN 'protesters'
      WHEN TRY_CAST(inter1 AS INT) = 7 THEN 'civilians'
      WHEN TRY_CAST(inter1 AS INT) = 8 THEN 'external_other_forces'
      ELSE 'other'
    END AS actor_category,
    
    CURRENT_TIMESTAMP() AS processed_at
    
  FROM base_data
)

-- Deduplication and extract AI classification results
SELECT 
  event_id_cnty,
  event_date,
  year,
  time_precision,
  disorder_type,
  event_type,
  sub_event_type,
  actor1,
  assoc_actor_1,
  inter1,
  actor2,
  assoc_actor_2,
  inter2,
  interaction,
  civilian_targeting,
  iso,
  region,
  country,
  governorate_name,
  town_district_of_governorate,
  admin3,
  location,
  latitude,
  longitude,
  geo_precision,
  source,
  source_scale,
  notes,
  fatalities,
  tags,
  timestamp,
  event_month,
  event_quarter,
  crowd_size_int,
  
  -- Extract AI classification labels and confidence scores
  primary_cause_result:response[0].value::STRING AS primary_cause,
  primary_cause_result:response[0].confidence_score::DOUBLE AS primary_cause_confidence,
  specific_primary_cause_result:response[0].value::STRING AS specific_primary_cause,
  specific_primary_cause_result:response[0].confidence_score::DOUBLE AS specific_primary_cause_confidence,
  
  has_fatalities,
  is_violent,
  is_peaceful_protest,
  actor_category,
  processed_at
  
FROM enriched_data
QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id_cnty ORDER BY timestamp DESC) = 1