# -*- coding: utf-8 -*-
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('d:/Project/ontology/FishDiseaseOntology.owl', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    'suspectedDisease',
    'inferredDisease',
    'observedSymptom',
    'hasWaterCondition',
    'hasAIPrediction',
    'temperatureValue',
    'pHValue',
    'dissolvedOxygenValue',
    'ammoniaValue',
    'nitriteValue',
    'alkalinityValue',
    'turbidityValue',
    'FishCondition',
    'DiagnosticCase',
    'HealthyState',
    'BacterialDisease',
    'FungalDisease',
    'ParasiticDisease',
    'Symptom',
    'Pathogen',
    'Treatment',
    'Prevention',
    'dc:source',
    'rdfs:comment',
    'rdfs:label',
    'disjointWith'
]

print("=== KIỂM TRA TỪNG MỤC YÊU CẦU CỦA GVHD TRONG FishDiseaseOntology.owl ===")
for c in checks:
    count = content.count(c)
    status = f"ĐÃ CÓ (xuất hiện {count} lần)" if count > 0 else "--> THIẾU (CHƯA CÓ) <--"
    print(f"{c:28}: {status}")
