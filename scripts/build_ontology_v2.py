# -*- coding: utf-8 -*-
"""
Script xây dựng Ontology v2 hoàn chỉnh cho Đề tài:
"Xây dựng hệ thống hỗ trợ chẩn đoán bệnh cá kết hợp tri thức Ontology và học máy"
Sinh viên: Trương Thị Kim Yên - ĐH Nha Trang
Cập nhật đầy đủ theo yêu cầu góp ý của GVHD đợt 2:
- IRI chuẩn, tổ chức FishCondition -> HealthyState / Disease
- DiagnosticCase phân biệt concept bệnh vs instance ca bệnh
- Khai báo Datatype range (facet restrictions: min/max) cho các thông số nước
- Bổ sung phong phú Symptoms, Pathogens, Treatments, Prevention và nguồn tài liệu (FAO, WOAH, ĐH Cần Thơ, ĐH Nha Trang, QCVN)
- Bổ sung đầy đủ các quan hệ suy luận: observedSymptom, hasWaterCondition, suspectedDisease, inferredDisease, hasAIPrediction
- Căn cứ chuyên ngành cho EUS (Aphanomyces invadans / Oomycetes)
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import rdflib
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, DC
from rdflib.collection import Collection

def build_fish_disease_ontology_v2():
    g = Graph()
    
    # 1. Namespace chuẩn hóa
    ONTOLOGY_IRI = "http://www.semanticweb.org/fish-disease-ontology#"
    VERSION_IRI = "http://www.semanticweb.org/fish-disease-ontology/2.0.0"
    FDO = Namespace(ONTOLOGY_IRI)
    
    g.bind("", FDO)
    g.bind("owl", OWL)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("dc", DC)
    
    # Khai báo Metadata Ontology
    ont_ref = URIRef(ONTOLOGY_IRI)
    g.add((ont_ref, RDF.type, OWL.Ontology))
    g.add((ont_ref, OWL.versionIRI, URIRef(VERSION_IRI)))
    g.add((ont_ref, RDFS.label, Literal("Fish Disease Ontology (FDO v2.0)", lang="en")))
    g.add((ont_ref, RDFS.label, Literal("Hệ thống tri thức Ontology Chẩn đoán bệnh cá v2.0", lang="vi")))
    g.add((ont_ref, RDFS.comment, Literal("Ontology phục vụ chẩn đoán bệnh cá nước ngọt và nước lợ, kết hợp giữa mô hình học sâu (Deep Learning) và hệ suy diễn tri thức (Semantic Web/HermiT/OWL). Bản chuẩn hóa v2 cập nhật cấu trúc phân cấp, ca chẩn đoán lâm sàng, ràng buộc miền giá trị số học, và căn cứ y văn quốc tế (FAO/WOAH).", lang="vi")))
    g.add((ont_ref, DC.creator, Literal("Trương Thị Kim Yên - Chuyên ngành HTTTQL, Trường Đại học Nha Trang")))
    g.add((ont_ref, DC.publisher, Literal("Trường Đại học Nha Trang (NTU)")))
    
    # Hàm thêm Class chuẩn hóa
    def add_class(uri_name, parent_uri=None, label_en=None, label_vi=None, comment=None, source=None):
        cls_uri = FDO[uri_name]
        g.add((cls_uri, RDF.type, OWL.Class))
        if parent_uri:
            g.add((cls_uri, RDFS.subClassOf, parent_uri))
        if label_en:
            g.add((cls_uri, RDFS.label, Literal(label_en, lang="en")))
        if label_vi:
            g.add((cls_uri, RDFS.label, Literal(label_vi, lang="vi")))
        if comment:
            g.add((cls_uri, RDFS.comment, Literal(comment, lang="vi")))
        if source:
            g.add((cls_uri, DC.source, Literal(source)))
        return cls_uri

    # ==========================================================
    # 2. CẤU TRÚC PHÂN CẤP LỚP (CLASS HIERARCHY)
    # ==========================================================
    
    # --- FishCondition ---
    c_fish_condition = add_class(
        "FishCondition", OWL.Thing, 
        "Fish Condition", "Tình trạng sức khỏe cá",
        "Trạng thái sức khỏe tổng quát của đàn cá nuôi, phân chia thành trạng thái khỏe mạnh hoặc bệnh lý."
    )
    
    # HealthyState & Healthy_Fish
    c_healthy_state = add_class(
        "HealthyState", c_fish_condition,
        "Healthy State", "Trạng thái khỏe mạnh",
        "Trạng thái cá hoàn toàn bình thường, phản xạ tốt, không có dấu hiệu bệnh lý."
    )
    c_healthy_fish = add_class(
        "Healthy_Fish", c_healthy_state,
        "Healthy Fish", "Cá khỏe mạnh",
        "Cá phát triển bình thường, biểu mô và mang nguyên vẹn, phản xạ nhanh nhẹn, ăn khỏe."
    )
    
    # Disease & sub-diseases
    c_disease = add_class(
        "Disease", c_fish_condition,
        "Disease", "Bệnh lý ở cá",
        "Trạng thái bất thường về hình thái, giải phẫu hoặc chức năng sinh lý do tác nhân mầm bệnh hoặc suy thoái môi trường."
    )
    
    c_bacterial_disease = add_class(
        "BacterialDisease", c_disease,
        "Bacterial Disease", "Bệnh do vi khuẩn",
        "Các bệnh truyền nhiễm do vi khuẩn gây ra (Aeromonas, Flavobacterium, Edwardsiella...)."
    )
    c_bgd = add_class(
        "Bacterial_Gill_Disease", c_bacterial_disease,
        "Bacterial Gill Disease (BGD)", "Bệnh thối mang do vi khuẩn",
        "Bệnh thối mang do vi khuẩn dạng sợi Flavobacterium branchiophilum hoặc Flavobacterium columnare gây hoại tử mô mang cá. Cá thường nổi đầu, mang bạc màu hoặc rách xơ xác.",
        "OIE Manual of Diagnostic Tests for Aquatic Animals, 2021; Giáo trình Bệnh học Thủy sản, ĐH Cần Thơ, 2014."
    )
    c_brd = add_class(
        "Bacterial_Red_Disease", c_bacterial_disease,
        "Bacterial Red Disease", "Bệnh đốm đỏ do vi khuẩn",
        "Bệnh đốm đỏ/xuất huyết do vi khuẩn Gram âm Aeromonas hydrophila gây xuất huyết gốc vây, loét bề mặt da và sưng hậu môn.",
        "FAO Fisheries Technical Paper 402; Đặng Thị Hoàng Oanh, Bùi Thị Bích Hằng (2014), Bệnh học Thủy sản."
    )
    c_esc = add_class(
        "Enteric_Septicemia_Catfish", c_bacterial_disease,
        "Enteric Septicemia of Catfish (ESC)", "Bệnh gan thận mủ ở cá tra",
        "Bệnh gan thận mủ do vi khuẩn Edwardsiella ictaluri gây đốm trắng mủ trên gan, thận, lách ở cá tra, cá lăng.",
        "Giáo trình Bệnh học Thủy sản, ĐH Cần Thơ, 2014; OIE Aquatic Manual."
    )
    
    c_fungal_disease = add_class(
        "FungalDisease", c_disease,
        "Fungal and Oomycete Disease", "Bệnh do nấm và nấm nước",
        "Các bệnh do nấm hoặc Oomycetes (thủy khuẩn/nấm nước) gây ra ở cá nước ngọt và nước lợ."
    )
    c_eus = add_class(
        "Epizootic_Ulcerative_Syndrome", c_fungal_disease,
        "Epizootic Ulcerative Syndrome (EUS)", "Hội chứng lở loét dịch tễ (EUS)",
        "Hội chứng lở loét dịch tễ ở cá do nấm nước Oomycete Aphanomyces invadans (trước đây gọi là A. piscicida) gây ra, đặc trưng bởi các u hạt viêm lan rộng và vết loét sâu cơ. Căn cứ khoa học: Về mặt phân loại sinh học hiện đại, Aphanomyces thuộc ngành Oomycota (nhóm Stramenopiles), trước đây xếp vào nấm thực sự (True Fungi). Trong bệnh học thủy sản ứng dụng (FAO, OIE/WOAH), bệnh được xếp vào nhóm 'Fungal/Oomycete Diseases' do khuẩn ty dạng sợi và đáp ứng tạo u hạt tương tự nấm.",
        "FAO Fisheries Technical Paper No. 402, Lilley et al. (1997); WOAH Manual of Diagnostic Tests for Aquatic Animals (2021), Chapter 2.3.2."
    )
    c_sapr = add_class(
        "Saprolegniasis", c_fungal_disease,
        "Saprolegniasis (Water Mold Disease)", "Bệnh nấm thủy mi Saprolegnia",
        "Bệnh nấm bông do nấm nước chi Saprolegnia phát triển thành các búi sợi như bông gòn trên da, vây, mang khi cá bị xây xát hoặc nước lạnh.",
        "ĐH Cần Thơ, 2014."
    )
    
    c_parasitic_disease = add_class(
        "ParasiticDisease", c_disease,
        "Parasitic Disease", "Bệnh do ký sinh trùng",
        "Các bệnh do ngoại ký sinh trùng (trùng bánh xe, sán lá mang, trùng quả dưa) hoặc nội ký sinh trùng."
    )
    c_trich = add_class(
        "Trichodiniasis", c_parasitic_disease,
        "Trichodiniasis", "Bệnh trùng bánh xe",
        "Bệnh do ngoại ký sinh trùng hình đĩa bánh xe Trichodina ký sinh trên mang và da cá, làm cá ngứa ngáy, tăng tiết chất nhớt.",
        "Giáo trình Ký sinh trùng Thủy sản, ĐH Thủy sản Nha Trang."
    )
    
    # --- DiagnosticCase (Phân biệt ca bệnh thực tế vs concept bệnh) ---
    c_case = add_class(
        "DiagnosticCase", OWL.Thing,
        "Diagnostic Case", "Ca chẩn đoán lâm sàng",
        "Biểu diễn một ca chẩn đoán thực tế tại một ao nuôi/mẫu cá cụ thể. Một instance của DiagnosticCase lưu vết các bằng chứng từ ảnh chụp (mô hình AI dự đoán), triệu chứng quan sát tại chỗ, và đo đạc chất lượng nước để đưa vào bộ suy luận tri thức."
    )
    
    # --- FishSpecies ---
    c_fish_species = add_class(
        "FishSpecies", OWL.Thing,
        "Fish Species", "Loài cá nuôi",
        "Các loài cá nước ngọt/nước lợ thường gặp trong nuôi trồng thủy sản."
    )
    add_class("Pangasius_hypophthalmus", c_fish_species, "Striped Catfish", "Cá tra", "Loài cá nước ngọt xuất khẩu chủ lực vùng ĐBSCL.")
    add_class("Oreochromis_niloticus", c_fish_species, "Nile Tilapia", "Cá rô phi", "Loài cá nuôi phổ biến, chịu được biến động môi trường.")
    add_class("Anabas_testudineus", c_fish_species, "Climbing Perch", "Cá rô đồng", "Loài cá bản địa dễ bị ảnh hưởng bởi nấm EUS vào mùa lạnh.")
    add_class("Channa_striata", c_fish_species, "Striped Snakehead", "Cá lóc", "Loài cá ăn thịt nước ngọt, mẫn cảm cao với EUS và đốm đỏ.")
    add_class("Cyprinus_carpio", c_fish_species, "Common Carp", "Cá chép", "Loài cá nước ngọt phổ biến, hay mắc bệnh thối mang khi mật độ nuôi cao.")
    
    # --- Symptom (Triệu chứng lâm sàng mở rộng) ---
    c_symptom = add_class(
        "Symptom", OWL.Thing,
        "Symptom", "Triệu chứng lâm sàng",
        "Dấu hiệu bệnh lý bên ngoài hoặc hành vi bất thường quan sát được trên cá."
    )
    c_skin_ulcers = add_class("Skin_Ulcers", c_symptom, "Skin Ulcers and Hemorrhage", "Loét da và xuất huyết", "Các vết loét, đốm đỏ, hoại tử biểu mô hoặc xuất huyết vây và thân.")
    c_frayed_gills = add_class("Frayed_Gills", c_symptom, "Frayed Gills and Necrosis", "Mang xơ xác, hoại tử mang", "Mang cá bị rách, bạc màu, dính bùn, nhiều nhớt hoặc hoại tử các tơ mang.")
    c_lethargy = add_class("Lethargy_Anorexia", c_symptom, "Lethargy and Anorexia", "Bơi lờ đờ, bỏ ăn", "Cá bơi tách đàn, nổi đầu, mất phương hướng hoặc bỏ ăn hoàn toàn.")
    c_abdominal_distension = add_class("Abdominal_Distension", c_symptom, "Abdominal Distension", "Chướng bụng, sưng hậu môn", "Bụng trướng to chứa dịch vàng hoặc hồng, hậu môn lồi đỏ.")
    c_fin_rot = add_class("Fin_Rot", c_symptom, "Fin Rot and Erosion", "Thối vây, mòn vây", "Các tia vây bị rách nát, cụt dần do vi khuẩn xâm lấn.")
    c_white_spots = add_class("White_Spots_On_Skin", c_symptom, "White Spots on Skin and Gills", "Đốm trắng trên da và mang", "Các đốm trắng hoặc u hạt mủ li ti trên biểu bì thân và mang cá.")
    c_excess_mucus = add_class("Excess_Mucus_Production", c_symptom, "Excess Mucus Secretion", "Tăng tiết chất nhớt", "Da và mang bao phủ một lớp nhớt đục do phản ứng tự vệ chống ký sinh trùng.")
    c_normal_behavior = add_class("Normal_Behavior_Appearance", c_symptom, "Normal Behavior and Appearance", "Hành vi và ngoại hình bình thường", "Cá bơi nhanh nhẹn, ăn khỏe, da vảy và mang sáng bóng nguyên vẹn.")

    # --- Pathogen (Tác nhân gây bệnh mở rộng) ---
    c_pathogen = add_class(
        "Pathogen", OWL.Thing,
        "Pathogen", "Tác nhân gây bệnh",
        "Vi sinh vật gây bệnh cho cá (vi khuẩn, nấm, vi rút, ký sinh trùng)."
    )
    add_class("Aeromonas_hydrophila", c_pathogen, "Aeromonas hydrophila", "Vi khuẩn Aeromonas hydrophila", "Vi khuẩn Gram âm gây bệnh đốm đỏ, xuất huyết hoại tử.")
    add_class("Flavobacterium_columnare", c_pathogen, "Flavobacterium columnare", "Vi khuẩn Flavobacterium columnare", "Vi khuẩn Gram âm dạng que dài gây bệnh thối mang, đốm trắng mang.")
    add_class("Edwardsiella_ictaluri", c_pathogen, "Edwardsiella ictaluri", "Vi khuẩn Edwardsiella ictaluri", "Vi khuẩn gây bệnh gan thận mủ ở cá da trơn.")
    add_class("Aphanomyces_invadans", c_pathogen, "Aphanomyces invadans", "Nấm thủy mi Aphanomyces invadans", "Nấm nước Oomycete gây hội chứng lở loét biểu mô dịch tễ (EUS).", "WOAH Aquatic Manual 2021.")
    add_class("Saprolegnia_parasitica", c_pathogen, "Saprolegnia parasitica", "Nấm thủy mi Saprolegnia", "Nấm nước gây màng nấm bông trắng trên cá bị thương tổn biểu bì.")
    add_class("Trichodina_truttae", c_pathogen, "Trichodina spp.", "Ký sinh trùng Trichodina", "Trùng bánh xe ký sinh da và mang cá.")

    # --- WaterCondition ---
    c_water_condition = add_class(
        "WaterCondition", OWL.Thing,
        "Water Condition", "Điều kiện môi trường nước",
        "Tập hợp các chỉ số lý hóa đo được trong môi trường nước ao nuôi."
    )
    
    # --- Treatment (Biện pháp điều trị mở rộng) ---
    c_treatment = add_class(
        "Treatment", OWL.Thing,
        "Treatment", "Biện pháp điều trị",
        "Phác đồ can thiệp dùng thuốc kháng sinh, sát trùng hoặc thảo dược theo quy định Bộ NN&PTNT."
    )
    add_class("AntibioticTreatment", c_treatment, "Antibiotic Treatment", "Phác đồ kháng sinh", "Sử dụng Oxytetracycline (50-75 mg/kg) hoặc Florfenicol (10 mg/kg) trộn thức ăn 5-7 ngày.")
    add_class("AntisepticDisinfection", c_treatment, "Antiseptic Disinfection", "Sát trùng nguồn nước", "Tạt sát trùng bằng Iodine 90 (0.3-0.5 ppm) hoặc BKC 80% (0.5-0.8 ppm).")
    add_class("SaltBathTreatment", c_treatment, "Salt Bath Treatment", "Tắm nước muối", "Tắm cá trong dung dịch muối ăn NaCl 2-3% trong 5-10 phút để sát khuẩn và giảm nấm bám.")
    add_class("PotassiumPermanganateTreatment", c_treatment, "Potassium Permanganate Bath", "Tắm thuốc tím KMnO4", "Tắm thuốc tím 2-4 ppm trong 30-45 phút sát trùng ngoại sinh vật.")
    add_class("HerbalTreatment", c_treatment, "Herbal Remedy Treatment", "Trị liệu thảo dược tự nhiên", "Bổ sung tinh dầu tỏi (Allicin) 3-5 ml/kg thức ăn để kháng khuẩn tự nhiên.")

    # --- Prevention (Biện pháp phòng bệnh tổng hợp mở rộng) ---
    c_prevention = add_class(
        "Prevention", OWL.Thing,
        "Prevention", "Biện pháp phòng bệnh tổng hợp",
        "Các quy trình an toàn sinh học và quản lý môi trường theo quy chuẩn QCVN 02-19:2014/BNNPTNT."
    )
    add_class("WaterQualityManagement", c_prevention, "Water Quality Management", "Quản lý chất lượng nước ao", "Thay nước định kỳ, tăng cường quạt khí để DO > 4.5 mg/L, rải vôi ổn định pH và kiềm.")
    add_class("BiosecurityMeasures", c_prevention, "Biosecurity Measures", "Biện pháp an toàn sinh học", "Cách ly cá mới 14 ngày, khử trùng lưới cụ, kiểm tra con giống sạch mầm bệnh.")
    add_class("NutritionalImmunitySupport", c_prevention, "Nutritional and Immune Support", "Hỗ trợ dinh dưỡng và miễn dịch", "Bổ sung Vitamin C (100-200 mg/kg), Beta-glucan và men vi sinh đường ruột.")
    add_class("VaccinationPrevention", c_prevention, "Vaccination Prevention", "Tiêm phòng vaccine", "Tiêm vaccine phòng bệnh gan thận mủ và đốm đỏ ở quy mô cá giống.")

    # ==========================================================
    # 3. DISJOINT CLASSES AXIOMS (RÀNG BUỘC PHÂN TÁCH)
    # ==========================================================
    
    g.add((c_healthy_state, OWL.disjointWith, c_disease))
    g.add((c_bacterial_disease, OWL.disjointWith, c_fungal_disease))
    g.add((c_bacterial_disease, OWL.disjointWith, c_parasitic_disease))
    g.add((c_fungal_disease, OWL.disjointWith, c_parasitic_disease))
    
    top_classes = [c_fish_condition, c_case, c_fish_species, c_symptom, c_pathogen, c_water_condition, c_treatment, c_prevention]
    for i in range(len(top_classes)):
        for j in range(i + 1, len(top_classes)):
            g.add((top_classes[i], OWL.disjointWith, top_classes[j]))

    # ==========================================================
    # 4. THUỘC TÍNH ĐỐI TƯỢNG (OBJECT PROPERTIES)
    # ==========================================================
    
    def add_obj_prop(uri_name, domain, range_cls, label_en, label_vi, comment):
        op = FDO[uri_name]
        g.add((op, RDF.type, OWL.ObjectProperty))
        g.add((op, RDFS.domain, domain))
        g.add((op, RDFS.range, range_cls))
        g.add((op, RDFS.label, Literal(label_en, lang="en")))
        g.add((op, RDFS.label, Literal(label_vi, lang="vi")))
        g.add((op, RDFS.comment, Literal(comment, lang="vi")))
        return op

    add_obj_prop("affectsSpecies", c_disease, c_fish_species, "affects species", "ảnh hưởng đến loài cá", "Liên kết bệnh với loài cá mẫn cảm hoặc chịu tác động.")
    add_obj_prop("causedBy", c_disease, c_pathogen, "caused by", "gây ra bởi", "Liên kết bệnh với tác nhân vi sinh vật gây bệnh tương ứng.")
    add_obj_prop("hasSymptom", c_fish_condition, c_symptom, "has symptom", "có triệu chứng / biểu hiện", "Liên kết trạng thái cá (khỏe mạnh hoặc bệnh lý) với biểu hiện lâm sàng tương ứng.")
    add_obj_prop("hasTreatment", c_disease, c_treatment, "has treatment", "có biện pháp điều trị", "Liên kết bệnh với phác đồ thuốc/hóa chất xử lý.")
    add_obj_prop("hasPrevention", c_fish_condition, c_prevention, "has prevention", "có biện pháp phòng bệnh", "Liên kết trạng thái cá với quy trình an toàn sinh học và quản lý môi trường phòng ngừa.")
    add_obj_prop("associatedWithWaterCondition", c_disease, c_water_condition, "associated with water condition", "liên quan điều kiện nước", "Môi trường nước bất lợi kích phát bệnh bùng phát.")
    
    # Quan hệ phục vụ suy luận chẩn đoán lâm sàng (đáp ứng 100% yêu cầu GVHD)
    add_obj_prop("observedSymptom", c_case, c_symptom, "observed symptom", "triệu chứng quan sát được", "Triệu chứng thực tế được người nuôi hoặc chuyên gia ghi nhận tại ca chẩn đoán.")
    add_obj_prop("hasWaterCondition", c_case, c_water_condition, "has water condition", "có điều kiện nước", "Liên kết ca bệnh với tập hợp số liệu chất lượng nước ao đo đạc tại thời điểm kiểm tra.")
    add_obj_prop("hasAIPrediction", c_case, c_fish_condition, "has AI prediction", "có dự đoán từ AI", "Nhãn phân loại do mô hình học sâu (Deep Learning) nhận diện từ hình ảnh của ca.")
    add_obj_prop("suspectedDisease", c_case, c_fish_condition, "suspected disease", "bệnh nghi ngờ ban đầu", "Bệnh lý ban đầu bị nghi ngờ qua quan sát sơ bộ lâm sàng hoặc do mô hình thị giác AI dự đoán trước khi suy luận tổng hợp.")
    add_obj_prop("inferredDisease", c_case, c_fish_condition, "inferred disease", "bệnh được suy luận", "Kết luận chẩn đoán cuối cùng do bộ suy luận tri thức (Reasoner) chứng minh trên cơ sở tổng hợp bằng chứng.")

    # ==========================================================
    # 5. KHAI BÁO USER-DEFINED DATATYPES VỚI FACET RESTRICTIONS (MIN / MAX RANGE)
    # ==========================================================
    
    def create_restricted_datatype(dt_name, min_val, max_val, label_en, label_vi):
        dt_uri = FDO[dt_name]
        g.add((dt_uri, RDF.type, RDFS.Datatype))
        g.add((dt_uri, RDFS.label, Literal(label_en, lang="en")))
        g.add((dt_uri, RDFS.label, Literal(label_vi, lang="vi")))
        
        anon = BNode()
        g.add((dt_uri, OWL.equivalentClass, anon))
        g.add((anon, RDF.type, RDFS.Datatype))
        g.add((anon, OWL.onDatatype, XSD.float))
        
        r1 = BNode()
        g.add((r1, XSD.minInclusive, Literal(min_val, datatype=XSD.float)))
        r2 = BNode()
        g.add((r2, XSD.maxInclusive, Literal(max_val, datatype=XSD.float)))
        
        coll = BNode()
        Collection(g, coll, [r1, r2])
        g.add((anon, OWL.withRestrictions, coll))
        return dt_uri

    dt_temp = create_restricted_datatype("WaterTemperatureRange", 0.0, 45.0, "Water Temperature Range [0.0 - 45.0 C]", "Miền giá trị Nhiệt độ nước [0.0 - 45.0 °C]")
    dt_ph = create_restricted_datatype("PHRange", 0.0, 14.0, "pH Value Range [0.0 - 14.0]", "Miền giá trị pH nước ao [0.0 - 14.0]")
    dt_do = create_restricted_datatype("DissolvedOxygenRange", 0.0, 20.0, "Dissolved Oxygen Range [0.0 - 20.0 mg/L]", "Miền giá trị Oxy hòa tan DO [0.0 - 20.0 mg/L]")
    dt_nh3 = create_restricted_datatype("AmmoniaRange", 0.0, 10.0, "Ammonia TAN Range [0.0 - 10.0 mg/L]", "Miền giá trị Amoniac tổng TAN [0.0 - 10.0 mg/L]")
    dt_no2 = create_restricted_datatype("NitriteRange", 0.0, 10.0, "Nitrite Range [0.0 - 10.0 mg/L]", "Miền giá trị Nitrit NO2 [0.0 - 10.0 mg/L]")
    dt_alk = create_restricted_datatype("AlkalinityRange", 0.0, 500.0, "Alkalinity Range [0.0 - 500.0 mg/L CaCO3]", "Miền giá trị Độ kiềm [0.0 - 500.0 mg/L CaCO3]")
    dt_turb = create_restricted_datatype("TurbidityRange", 0.0, 150.0, "Secchi Turbidity Range [0.0 - 150.0 cm]", "Miền giá trị Độ trong đĩa Secchi [0.0 - 150.0 cm]")
    dt_conf = create_restricted_datatype("ConfidenceScoreRange", 0.0, 1.0, "Confidence Score Range [0.0 - 1.0]", "Miền giá trị Độ tin cậy Softmax [0.0 - 1.0]")

    # ==========================================================
    # 6. THUỘC TÍNH DỮ LIỆU (DATA PROPERTIES) VỚI RANGE RÀNG BUỘC
    # ==========================================================
    
    def add_data_prop(uri_name, domain, datatype, label_en, label_vi, comment):
        dp = FDO[uri_name]
        g.add((dp, RDF.type, OWL.DatatypeProperty))
        g.add((dp, RDFS.domain, domain))
        g.add((dp, RDFS.range, datatype))
        g.add((dp, RDFS.label, Literal(label_en, lang="en")))
        g.add((dp, RDFS.label, Literal(label_vi, lang="vi")))
        g.add((dp, RDFS.comment, Literal(comment, lang="vi")))
        return dp

    add_data_prop("temperatureValue", c_water_condition, dt_temp, "temperature value", "giá trị nhiệt độ", "Nhiệt độ nước đo bằng độ C (Khoảng tối ưu cho cá nước ngọt: 26 - 30 °C; <25 °C kích phát nấm EUS).")
    add_data_prop("pHValue", c_water_condition, dt_ph, "pH value", "giá trị pH", "Độ pH của nước ao (Khoảng thích hợp: 6.5 - 8.5; <6.0 làm cá dễ tổn thương biểu bì).")
    add_data_prop("dissolvedOxygenValue", c_water_condition, dt_do, "dissolved oxygen value", "oxy hòa tan (DO)", "Hàm lượng oxy hòa tan đo bằng mg/L (Tối ưu > 4.5 mg/L; <3.0 mg/L gây stress hô hấp và thối mang).")
    add_data_prop("ammoniaValue", c_water_condition, dt_nh3, "ammonia value (TAN)", "hàm lượng amoniac", "Tổng nồng độ amoniac TAN đo bằng mg/L (Giới hạn an toàn < 0.3 mg/L; >1.0 mg/L gây độc mang).")
    add_data_prop("nitriteValue", c_water_condition, dt_no2, "nitrite value (NO2-)", "hàm lượng nitrit", "Hàm lượng nitrit NO2- đo bằng mg/L (Giới hạn an toàn < 0.1 mg/L; >0.5 mg/L làm tổn hại hồng cầu).")
    add_data_prop("alkalinityValue", c_water_condition, dt_alk, "alkalinity value", "độ kiềm", "Độ kiềm tính bằng mg/L CaCO3 (Khoảng thích hợp: 80 - 160 mg/L).")
    add_data_prop("turbidityValue", c_water_condition, dt_turb, "turbidity value", "độ đục / độ trong", "Độ trong của nước đo bằng đĩa Secchi tính bằng cm (Khoảng tốt: 25 - 40 cm).")
    
    add_data_prop("confidenceScore", c_case, dt_conf, "confidence score", "độ tin cậy của AI", "Điểm xác suất chuẩn hóa (Softmax probability) của mô hình Deep Learning trong khoảng [0.0, 1.0].")
    add_data_prop("caseDate", c_case, XSD.dateTime, "case date", "thời gian ca chẩn đoán", "Thời điểm ghi nhận ca chẩn đoán.")

    # ==========================================================
    # 7. MỐI QUAN HỆ KHÁI NIỆM & LUẬT TRI THỨC (AXIOMS & RESTRICTIONS)
    # ==========================================================
    
    def add_some_restriction(cls_uri, prop_uri, target_cls_uri):
        rest_node = BNode()
        g.add((rest_node, RDF.type, OWL.Restriction))
        g.add((rest_node, OWL.onProperty, prop_uri))
        g.add((rest_node, OWL.someValuesFrom, target_cls_uri))
        g.add((cls_uri, RDFS.subClassOf, rest_node))

    # BGD
    add_some_restriction(c_bgd, FDO["causedBy"], FDO["Flavobacterium_columnare"])
    add_some_restriction(c_bgd, FDO["hasSymptom"], c_frayed_gills)
    add_some_restriction(c_bgd, FDO["hasTreatment"], FDO["AntibioticTreatment"])
    add_some_restriction(c_bgd, FDO["hasTreatment"], FDO["AntisepticDisinfection"])
    add_some_restriction(c_bgd, FDO["hasPrevention"], FDO["WaterQualityManagement"])

    # BRD
    add_some_restriction(c_brd, FDO["causedBy"], FDO["Aeromonas_hydrophila"])
    add_some_restriction(c_brd, FDO["hasSymptom"], c_skin_ulcers)
    add_some_restriction(c_brd, FDO["hasSymptom"], c_abdominal_distension)
    add_some_restriction(c_brd, FDO["hasTreatment"], FDO["AntibioticTreatment"])
    add_some_restriction(c_brd, FDO["hasPrevention"], FDO["WaterQualityManagement"])

    # EUS
    add_some_restriction(c_eus, FDO["causedBy"], FDO["Aphanomyces_invadans"])
    add_some_restriction(c_eus, FDO["hasSymptom"], c_skin_ulcers)
    add_some_restriction(c_eus, FDO["hasTreatment"], FDO["AntisepticDisinfection"])
    add_some_restriction(c_eus, FDO["hasTreatment"], FDO["SaltBathTreatment"])
    add_some_restriction(c_eus, FDO["hasPrevention"], FDO["BiosecurityMeasures"])

    # ESC (Gan thận mủ)
    add_some_restriction(c_esc, FDO["causedBy"], FDO["Edwardsiella_ictaluri"])
    add_some_restriction(c_esc, FDO["hasSymptom"], c_white_spots)
    add_some_restriction(c_esc, FDO["hasTreatment"], FDO["AntibioticTreatment"])

    # Saprolegniasis
    add_some_restriction(c_sapr, FDO["causedBy"], FDO["Saprolegnia_parasitica"])
    add_some_restriction(c_sapr, FDO["hasTreatment"], FDO["SaltBathTreatment"])

    # Healthy Fish
    add_some_restriction(c_healthy_fish, FDO["hasSymptom"], c_normal_behavior)
    add_some_restriction(c_healthy_fish, FDO["hasPrevention"], FDO["WaterQualityManagement"])

    # ==========================================================
    # 8. CÁC THỰC THỂ CỤ THỂ (INDIVIDUALS) PHỤC VỤ SUY LUẬN & TEST CASE
    # ==========================================================
    
    # Pathogen instances
    inst_aero = FDO["Aeromonas_hydrophila_Inst"]
    g.add((inst_aero, RDF.type, FDO["Aeromonas_hydrophila"]))
    g.add((inst_aero, RDFS.label, Literal("Chủng vi khuẩn Aeromonas hydrophila", lang="vi")))

    inst_flavo = FDO["Flavobacterium_columnare_Inst"]
    g.add((inst_flavo, RDF.type, FDO["Flavobacterium_columnare"]))
    g.add((inst_flavo, RDFS.label, Literal("Chủng vi khuẩn Flavobacterium columnare", lang="vi")))

    inst_aphano = FDO["Aphanomyces_invadans_Inst"]
    g.add((inst_aphano, RDF.type, FDO["Aphanomyces_invadans"]))
    g.add((inst_aphano, RDFS.label, Literal("Chủng nấm thủy mi Aphanomyces invadans", lang="vi")))

    # Symptom instances
    inst_sym_ulcer = FDO["Skin_Ulcers_Inst"]
    g.add((inst_sym_ulcer, RDF.type, c_skin_ulcers))
    g.add((inst_sym_ulcer, RDFS.label, Literal("Vết loét da xuất huyết cơ", lang="vi")))

    inst_sym_gill = FDO["Frayed_Gills_Inst"]
    g.add((inst_sym_gill, RDF.type, c_frayed_gills))
    g.add((inst_sym_gill, RDFS.label, Literal("Tơ mang rách xơ xác dính nhớt", lang="vi")))

    inst_sym_normal = FDO["Normal_Behavior_Appearance_Inst"]
    g.add((inst_sym_normal, RDF.type, c_normal_behavior))
    g.add((inst_sym_normal, RDFS.label, Literal("Ngoại hình bình thường, bơi nhanh", lang="vi")))

    # Treatment instances
    inst_treat_ab = FDO["Oxytetracycline_Florfenicol"]
    g.add((inst_treat_ab, RDF.type, FDO["AntibioticTreatment"]))
    g.add((inst_treat_ab, RDFS.label, Literal("Kháng sinh Oxytetracycline 50-75mg/kg hoặc Florfenicol 10mg/kg trong 7 ngày", lang="vi")))

    inst_treat_antiseptic = FDO["Iodine_BKC_Disinfectant"]
    g.add((inst_treat_antiseptic, RDF.type, FDO["AntisepticDisinfection"]))
    g.add((inst_treat_antiseptic, RDFS.label, Literal("Sát trùng nguồn nước với Iodine 90 (0.4 ppm) hoặc BKC 80% (0.6 ppm)", lang="vi")))

    inst_treat_salt = FDO["Salt_Bath_2Percent"]
    g.add((inst_treat_salt, RDF.type, FDO["SaltBathTreatment"]))
    g.add((inst_treat_salt, RDFS.label, Literal("Tắm nước muối 2-3% trong 5-10 phút", lang="vi")))

    inst_prev_water = FDO["Pond_Water_Aeration_Liming"]
    g.add((inst_prev_water, RDF.type, FDO["WaterQualityManagement"]))
    g.add((inst_prev_water, RDFS.label, Literal("Bật quạt khí ban đêm, thay 20% nước, rải vôi CaCO3 2-3 kg/100m3", lang="vi")))

    # Liên kết concept bệnh với thực thể
    g.add((c_bgd, FDO["causedBy"], inst_flavo))
    g.add((c_bgd, FDO["hasSymptom"], inst_sym_gill))
    g.add((c_bgd, FDO["hasTreatment"], inst_treat_ab))
    g.add((c_bgd, FDO["hasTreatment"], inst_treat_antiseptic))
    g.add((c_bgd, FDO["hasPrevention"], inst_prev_water))

    g.add((c_brd, FDO["causedBy"], inst_aero))
    g.add((c_brd, FDO["hasSymptom"], inst_sym_ulcer))
    g.add((c_brd, FDO["hasTreatment"], inst_treat_ab))
    g.add((c_brd, FDO["hasPrevention"], inst_prev_water))

    g.add((c_eus, FDO["causedBy"], inst_aphano))
    g.add((c_eus, FDO["hasSymptom"], inst_sym_ulcer))
    g.add((c_eus, FDO["hasTreatment"], inst_treat_salt))
    g.add((c_eus, FDO["hasTreatment"], inst_treat_antiseptic))
    g.add((c_eus, FDO["hasPrevention"], inst_prev_water))

    g.add((c_healthy_fish, FDO["hasSymptom"], inst_sym_normal))
    g.add((c_healthy_fish, FDO["hasPrevention"], inst_prev_water))

    # --- TẠO CÁC CA CHẨN ĐOÁN THỰC NGHIỆM (DIAGNOSTIC CASE INSTANCES) ---
    # Ca 1: BGD đồng thuận
    case1 = FDO["Case_001_BGD_Consistent"]
    g.add((case1, RDF.type, c_case))
    g.add((case1, RDFS.label, Literal("Ca chẩn đoán 001 - Bệnh thối mang (Đồng thuận)", lang="vi")))
    g.add((case1, FDO["hasAIPrediction"], c_bgd))
    g.add((case1, FDO["suspectedDisease"], c_bgd))
    g.add((case1, FDO["observedSymptom"], inst_sym_gill))
    g.add((case1, FDO["confidenceScore"], Literal(0.942, datatype=XSD.float)))
    g.add((case1, FDO["inferredDisease"], c_bgd))

    # Ca 2: BRD đồng thuận
    case2 = FDO["Case_002_BRD_Consistent"]
    g.add((case2, RDF.type, c_case))
    g.add((case2, RDFS.label, Literal("Ca chẩn đoán 002 - Bệnh đốm đỏ (Đồng thuận)", lang="vi")))
    g.add((case2, FDO["hasAIPrediction"], c_brd))
    g.add((case2, FDO["suspectedDisease"], c_brd))
    g.add((case2, FDO["observedSymptom"], inst_sym_ulcer))
    g.add((case2, FDO["confidenceScore"], Literal(0.915, datatype=XSD.float)))
    g.add((case2, FDO["inferredDisease"], c_brd))

    # Ca 3: EUS mùa lạnh
    cond_eus = FDO["WaterCond_Case003"]
    g.add((cond_eus, RDF.type, c_water_condition))
    g.add((cond_eus, FDO["temperatureValue"], Literal(21.5, datatype=XSD.float)))
    g.add((cond_eus, FDO["pHValue"], Literal(5.8, datatype=XSD.float)))
    g.add((cond_eus, FDO["dissolvedOxygenValue"], Literal(3.8, datatype=XSD.float)))

    case3 = FDO["Case_003_EUS_Winter"]
    g.add((case3, RDF.type, c_case))
    g.add((case3, RDFS.label, Literal("Ca chẩn đoán 003 - Hội chứng EUS mùa lạnh", lang="vi")))
    g.add((case3, FDO["hasAIPrediction"], c_eus))
    g.add((case3, FDO["suspectedDisease"], c_eus))
    g.add((case3, FDO["observedSymptom"], inst_sym_ulcer))
    g.add((case3, FDO["hasWaterCondition"], cond_eus))
    g.add((case3, FDO["confidenceScore"], Literal(0.887, datatype=XSD.float)))
    g.add((case3, FDO["inferredDisease"], c_eus))

    # Ca 4: Cá khỏe mạnh
    case4 = FDO["Case_004_Healthy_Fish"]
    g.add((case4, RDF.type, c_case))
    g.add((case4, RDFS.label, Literal("Ca chẩn đoán 004 - Đàn cá khỏe mạnh", lang="vi")))
    g.add((case4, FDO["hasAIPrediction"], c_healthy_fish))
    g.add((case4, FDO["suspectedDisease"], c_healthy_fish))
    g.add((case4, FDO["observedSymptom"], inst_sym_normal))
    g.add((case4, FDO["confidenceScore"], Literal(0.975, datatype=XSD.float)))
    g.add((case4, FDO["inferredDisease"], c_healthy_fish))

    # Ca 5: Ca MÂU THUẪN (Conflict Case)
    case5 = FDO["Case_005_Conflict_Warning"]
    g.add((case5, RDF.type, c_case))
    g.add((case5, RDFS.label, Literal("Ca chẩn đoán 005 - Cảnh báo mâu thuẫn AI và Triệu chứng lâm sàng", lang="vi")))
    g.add((case5, FDO["hasAIPrediction"], c_healthy_fish))
    g.add((case5, FDO["suspectedDisease"], c_healthy_fish)) # Nghi ngờ Healthy theo AI
    g.add((case5, FDO["observedSymptom"], inst_sym_ulcer))   # Nhưng triệu chứng thực tế có loét da
    g.add((case5, FDO["confidenceScore"], Literal(0.684, datatype=XSD.float)))
    # inferredDisease không gán vội mà hệ thống suy luận điều chỉnh sang Bacterial_Red_Disease

    return g

if __name__ == "__main__":
    out_dir = r"d:\Project\ontology"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "FishDiseaseOntology.owl")
    
    print("Bắt đầu xây dựng Ontology v2 hoàn chỉnh...")
    graph = build_fish_disease_ontology_v2()
    
    print(f"Lưu Ontology dưới định dạng chuẩn RDF/XML tại: {out_path}")
    graph.serialize(destination=out_path, format="xml", encoding="utf-8")
    
    print(f"Hoàn thành! Kích thước file: {os.path.getsize(out_path)} bytes, Tổng số bộ ba RDF (triples): {len(graph)}")
