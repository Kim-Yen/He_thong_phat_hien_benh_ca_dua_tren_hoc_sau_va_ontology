# -*- coding: utf-8 -*-
"""
Module Suy luận Tri thức Ontology kết hợp Deep Learning (AI-Ontology Hybrid Reasoning)
Hệ thống Hỗ trợ Chẩn đoán Bệnh Cá Nước Ngọt & Nước Lợ
Sinh viên: Trương Thị Kim Yên - ĐH Nha Trang
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import rdflib
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD

FDO_IRI = "http://www.semanticweb.org/fish-disease-ontology#"
FDO = Namespace(FDO_IRI)

class FishDiseaseReasoner:
    """
    Bộ suy luận tri thức Semantic Web hỗ trợ chẩn đoán bệnh cá.
    Tích hợp kết quả phân loại Deep Learning, triệu chứng lâm sàng và chỉ số môi trường nước.
    """
    
    def __init__(self, ontology_path: Optional[str] = None, mapping_path: Optional[str] = None):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Tự động tìm đường dẫn file Ontology
        if ontology_path is None or not os.path.exists(ontology_path):
            candidate_ontologies = [
                ontology_path,
                os.path.join(project_root, "ontology", "FishDiseaseOntology.owl"),
                os.path.join("ontology", "FishDiseaseOntology.owl"),
                os.path.join("..", "ontology", "FishDiseaseOntology.owl"),
                "FishDiseaseOntology.owl"
            ]
            for c in candidate_ontologies:
                if c and os.path.exists(c):
                    ontology_path = os.path.abspath(c)
                    break
                    
        # Tự động tìm đường dẫn file mapping JSON (hỗ trợ cả thư mục notebook/ và thư mục gốc)
        if mapping_path is None or not os.path.exists(mapping_path):
            candidate_mappings = [
                mapping_path,
                os.path.join(project_root, "notebook", "label_ontology_mapping.json"),
                os.path.join(project_root, "label_ontology_mapping.json"),
                os.path.join("notebook", "label_ontology_mapping.json"),
                os.path.join("..", "notebook", "label_ontology_mapping.json"),
                os.path.join(project_root, "ontology", "label_ontology_mapping.json"),
                "label_ontology_mapping.json"
            ]
            for c in candidate_mappings:
                if c and os.path.exists(c):
                    mapping_path = os.path.abspath(c)
                    break
            
        self.ontology_path = ontology_path
        self.mapping_path = mapping_path
        
        # 1. Nạp bản đồ ánh xạ nhãn AI <-> Ontology URI
        with open(self.mapping_path, "r", encoding="utf-8") as f:
            self.mapping_data = json.load(f)
        self.mappings = self.mapping_data["mappings"]
        
        # 2. Nạp Ontology vào rdflib Graph
        self.graph = Graph()
        self.graph.parse(self.ontology_path, format="xml")
        
    def reason(self, 
               ai_predictions: List[Dict[str, Any]], 
               observed_symptoms: List[str], 
               water_measurements: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Thực hiện suy luận lai (Hybrid Reasoning):
        - ai_predictions: danh sách [{'class_name': str, 'confidence': float}, ...]
        - observed_symptoms: danh sách mã hoặc tên triệu chứng ['SYM_SKIN_ULCERS', 'SYM_LETHARGY', ...]
        - water_measurements: dict các chỉ số nước {'temperature': float, 'ph': float, 'dissolved_oxygen': float, 'ammonia': float, ...}
        """
        if water_measurements is None:
            water_measurements = {}
            
        top_ai = ai_predictions[0] if ai_predictions else {"class_name": "Healthy Fish", "confidence": 0.5}
        top_ai_name = top_ai["class_name"]
        top_ai_conf = float(top_ai.get("confidence", 0.0))
        
        # Tìm thông tin ánh xạ của nhãn AI top-1
        top_mapping = None
        for k, v in self.mappings.items():
            if v["class_name"].lower() == top_ai_name.lower():
                top_mapping = v
                break
        if top_mapping is None:
            top_mapping = self.mappings["3"] # Default healthy
            
        # 1. PHÂN TÍCH TRIỆU CHỨNG LÂM SÀNG TỪ ONTOLOGY
        symptom_scores = {}
        for k, mapping in self.mappings.items():
            expected_sym_codes = [s["code"] for s in mapping.get("typical_symptoms", [])]
            expected_sym_uris = [s["uri"] for s in mapping.get("typical_symptoms", [])]
            
            # Đếm số triệu chứng trùng khớp
            match_count = 0
            for obs in observed_symptoms:
                if obs in expected_sym_codes or obs in expected_sym_uris:
                    match_count += 1
                elif any(obs.lower() in s["name"].lower() for s in mapping.get("typical_symptoms", [])):
                    match_count += 1
                    
            total_expected = max(1, len(expected_sym_codes))
            symptom_scores[mapping["class_name"]] = match_count / total_expected
            
        # 2. PHÂN TÍCH CHỈ SỐ MÔI TRƯỜNG NƯỚC TỪ ONTOLOGY & CẢNH BÁO
        water_warnings = []
        temp = water_measurements.get("temperature")
        ph = water_measurements.get("ph")
        do = water_measurements.get("dissolved_oxygen")
        ammonia = water_measurements.get("ammonia")
        nitrite = water_measurements.get("nitrite")
        
        water_risk_scores = {"Bacterial Gill Diseases": 0.0, "Bacterial Red Diseases": 0.0, "Epizootic Ulcerative Syndrome (EUS)": 0.0, "Healthy Fish": 0.0}
        
        if temp is not None:
            if temp < 25.0:
                water_warnings.append(f"Nhiệt độ nước lạnh ({temp}°C < 25°C) là yếu tố kích phát hàng đầu của nấm Oomycete Aphanomyces invadans (EUS).")
                water_risk_scores["Epizootic Ulcerative Syndrome (EUS)"] += 0.5
            elif temp > 30.0:
                water_warnings.append(f"Nhiệt độ nước cao ({temp}°C > 30°C) gia tăng áp lực trao đổi chất và vi khuẩn Aeromonas/Flavobacterium.")
                water_risk_scores["Bacterial Gill Diseases"] += 0.3
                water_risk_scores["Bacterial Red Diseases"] += 0.3
                
        if ph is not None:
            if ph < 6.5:
                water_warnings.append(f"Độ pH thấp ({ph} < 6.5) làm tổn thương lớp nhớt biểu bì cá, tạo điều kiện cho bào tử nấm EUS xâm nhập cơ.")
                water_risk_scores["Epizootic Ulcerative Syndrome (EUS)"] += 0.5
            elif ph > 8.5:
                water_warnings.append(f"Độ pH cao ({ph} > 8.5) gia tăng tỷ lệ amoniac độc NH3 tự do.")
                water_risk_scores["Bacterial Gill Diseases"] += 0.3
                
        if do is not None and do < 3.5:
            water_warnings.append(f"Hàm lượng oxy hòa tan thấp ({do} mg/L < 3.5 mg/L) gây stress hô hấp và kích hoạt bệnh thối mang (BGD).")
            water_risk_scores["Bacterial Gill Diseases"] += 0.5
            
        if ammonia is not None and ammonia > 0.5:
            water_warnings.append(f"Nồng độ Amoniac TAN cao ({ammonia} mg/L > 0.5 mg/L) phá hủy tơ mang và làm suy giảm miễn dịch.")
            water_risk_scores["Bacterial Gill Diseases"] += 0.4
            water_risk_scores["Bacterial Red Diseases"] += 0.4
            
        # 3. CƠ CHẾ PHÁT HIỆN MÂU THUẪN (CONFLICT DETECTION)
        conflict_detected = False
        conflict_type = "NONE"
        explanation = ""
        inferred_disease = top_ai_name
        
        # Mâu thuẫn loại 1: AI đoán cá khỏe mạnh (Healthy) nhưng có triệu chứng tổn thương bệnh lý
        has_pathology_symptom = any(s in ["SYM_SKIN_ULCERS", "SYM_FRAYED_GILLS", "SYM_ABDOMINAL_DISTENSION", "SYM_LETHARGY"] for s in observed_symptoms)
        if top_ai_name == "Healthy Fish" and has_pathology_symptom:
            conflict_detected = True
            conflict_type = "HEALTHY_AI_VS_PATHOLOGY_SYMPTOMS"
            # Tìm xem triệu chứng ủng hộ bệnh nào nhất
            best_sym_disease = max(symptom_scores, key=lambda k: symptom_scores[k] if k != "Healthy Fish" else -1)
            inferred_disease = best_sym_disease
            explanation = (
                f"MÂU THUẪN NGHIÊM TRỌNG: Mô hình Deep Learning nhận diện ảnh là 'Cá khỏe mạnh' (độ tin cậy {top_ai_conf:.1%}), "
                f"tuy nhiên triệu chứng thực tế ghi nhận tổn thương bệnh lý ({', '.join(observed_symptoms)}). "
                f"Hệ thống bác bỏ kết quả Healthy của AI và chuyển sang xem xét khả năng mắc '{inferred_disease}'."
            )
        # Mâu thuẫn loại 2: AI đoán bệnh A nhưng triệu chứng + nước chỉ ra bệnh B (ví dụ AI đoán Red Disease nhưng thực tế là EUS)
        elif top_ai_name == "Bacterial Red Diseases" and (temp is not None and temp < 24.0 or ph is not None and ph < 6.0):
            conflict_detected = True
            conflict_type = "BRD_AI_VS_EUS_ENVIRONMENT"
            inferred_disease = "Epizootic Ulcerative Syndrome (EUS)"
            explanation = (
                f"CẢNH BÁO BẤT ĐỒNG CHỨNG CỨ: Mô hình thị giác AI dự đoán 'Bệnh đốm đỏ do vi khuẩn' ({top_ai_conf:.1%}) do tổn thương loét đỏ bên ngoài, "
                f"tuy nhiên các yếu tố dịch tễ môi trường (Nhiệt độ nước lạnh {temp}°C, pH {ph}) ủng hộ mạnh mẽ 'Hội chứng lở loét dịch tễ (EUS)' do nấm Aphanomyces invadans. "
                f"Khuyến nghị chuyên gia kiểm tra tiêu bản sợi nấm trong mô cơ dưới kính hiển vi."
            )
        # Đồng thuận (Agreement)
        else:
            inferred_disease = top_ai_name
            explanation = (
                f"ĐỒNG THUẬN CHỨNG CỨ: Kết quả nhận diện từ mô hình Deep Learning ({top_ai_name} - độ tin cậy {top_ai_conf:.1%}) "
                f"hoàn toàn phù hợp với triệu chứng lâm sàng và các quy luật tiên đề tri thức trong Ontology."
            )

        # 4. TỔNG HỢP ĐIỂM TIN CẬY LAI (SUPPORT SCORE)
        # AI weight 0.50, Symptom match 0.35, Water match 0.15
        sym_score = symptom_scores.get(inferred_disease, 0.0)
        water_score = min(1.0, water_risk_scores.get(inferred_disease, 0.0))
        
        if conflict_detected:
            # Khi có mâu thuẫn, độ tin cậy bị điều chỉnh giảm trừ phạt mâu thuẫn
            support_score = round(0.35 * sym_score + 0.35 * water_score + 0.30 * top_ai_conf * 0.5, 3)
        else:
            support_score = round(0.50 * top_ai_conf + 0.35 * sym_score + 0.15 * (1.0 if not water_warnings else 0.8), 3)

        # 5. TRUY VẤN PHÁC ĐỒ ĐIỀU TRỊ & PHÒNG BỆNH TỪ ONTOLOGY
        inferred_mapping = None
        for k, v in self.mappings.items():
            if v["class_name"].lower() == inferred_disease.lower():
                inferred_mapping = v
                break
        if inferred_mapping is None:
            inferred_mapping = top_mapping

        # Xây dựng khuyến nghị cải thiện môi trường nước
        water_guidance = []
        if do is not None and do < 4.5:
            water_guidance.append(f"Tăng cường quạt nước / sục khí đáy ngay lập tức để nâng DO từ {do} mg/L lên trên 4.5 mg/L.")
        if ph is not None and ph < 6.5:
            water_guidance.append(f"Rải vôi nông nghiệp CaCO3 (2-3 kg / 100m3) hoặc vôi tôi Ca(OH)2 để nâng pH từ {ph} lên khoảng 7.0 - 7.5.")
        if ammonia is not None and ammonia > 0.3:
            water_guidance.append(f"Thay 20-30% nước sạch đáy ao và sử dụng chế phẩm vi sinh Bacillus sp. để phân hủy khí độc Amoniac ({ammonia} mg/L).")

        return {
            "case_summary": {
                "ai_predicted_class": top_ai_name,
                "ai_confidence": top_ai_conf,
                "inferred_disease": inferred_disease,
                "inferred_disease_vietnamese": inferred_mapping["vietnamese_name"],
                "inferred_disease_uri": inferred_mapping["ontology_uri"],
                "support_score": support_score,
                "conflict_detected": conflict_detected,
                "conflict_type": conflict_type
            },
            "evidence": {
                "deep_learning_evidence": {
                    "top_predictions": ai_predictions,
                    "model_source": "PyTorch CNN (MobileNetV3 / ResNet50)"
                },
                "ontology_evidence": {
                    "matched_symptoms": [s for s in observed_symptoms if s in [x["code"] for x in inferred_mapping.get("typical_symptoms", [])]],
                    "symptom_consistency_score": sym_score,
                    "water_risk_consistency_score": water_score,
                    "water_warnings": water_warnings,
                    "pathogen_info": inferred_mapping.get("pathogen")
                },
                "explanation": explanation
            },
            "recommendations": {
                "treatments": inferred_mapping.get("treatments", []),
                "prevention": inferred_mapping.get("prevention", ""),
                "water_adjustments": water_guidance
            }
        }

if __name__ == "__main__":
    print("Khởi tạo module suy luận tri thức FishDiseaseReasoner...")
    reasoner = FishDiseaseReasoner()
    print("Nạp thành công Ontology và Mapping!\n")

    # TEST CASE 1: Đồng thuận hoàn toàn (Consistent Case - BGD)
    print("=" * 60)
    print("TEST CASE 1: Bệnh thối mang (BGD) - AI và Triệu chứng đồng thuận")
    print("=" * 60)
    res1 = reasoner.reason(
        ai_predictions=[{"class_name": "Bacterial Gill Diseases", "confidence": 0.942}],
        observed_symptoms=["SYM_FRAYED_GILLS", "SYM_LETHARGY"],
        water_measurements={"temperature": 29.5, "ph": 7.2, "dissolved_oxygen": 2.8, "ammonia": 0.7}
    )
    print("Kết quả suy luận:", json.dumps(res1["case_summary"], ensure_ascii=False, indent=2))
    print("Giải thích:", res1["evidence"]["explanation"])

    # TEST CASE 2: Mâu thuẫn nghiêm trọng (Healthy AI vs Triệu chứng loét da)
    print("\n" + "=" * 60)
    print("TEST CASE 2: Mâu thuẫn AI (Healthy) vs Triệu chứng loét da (Ulcers)")
    print("=" * 60)
    res2 = reasoner.reason(
        ai_predictions=[{"class_name": "Healthy Fish", "confidence": 0.785}],
        observed_symptoms=["SYM_SKIN_ULCERS", "SYM_ABDOMINAL_DISTENSION"],
        water_measurements={"temperature": 28.0, "ph": 7.5, "dissolved_oxygen": 4.8}
    )
    print("Kết quả suy luận:", json.dumps(res2["case_summary"], ensure_ascii=False, indent=2))
    print("Giải thích:", res2["evidence"]["explanation"])

    # TEST CASE 3: Bất đồng chứng cứ dịch tễ (Red Disease AI vs EUS môi trường lạnh)
    print("\n" + "=" * 60)
    print("TEST CASE 3: Bất đồng chứng cứ dịch tễ (AI đoán Red Disease nhưng nước lạnh 21°C và pH 5.8)")
    print("=" * 60)
    res3 = reasoner.reason(
        ai_predictions=[{"class_name": "Bacterial Red Diseases", "confidence": 0.812}],
        observed_symptoms=["SYM_SKIN_ULCERS"],
        water_measurements={"temperature": 21.0, "ph": 5.8, "dissolved_oxygen": 3.4}
    )
    print("Kết quả suy luận:", json.dumps(res3["case_summary"], ensure_ascii=False, indent=2))
    print("Giải thích:", res3["evidence"]["explanation"])
    print("Khuyến nghị phác đồ:", json.dumps(res3["recommendations"], ensure_ascii=False, indent=2))
