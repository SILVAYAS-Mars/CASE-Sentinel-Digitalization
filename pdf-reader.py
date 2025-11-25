import pdfplumber
import json
#test commit
pdf_path = "KM PEDIGREE Puppy Nutridefense RL22 1.pdf"

import re


def extract_header(page):
    """
    Extrai Product Name, Analysis Date, Species e Life Stage,"""

    # filtra só o texto do header por regex
    full_text = page.extract_text() or ""
    clean = " ".join(full_text.split()) 

    header_data = {}

    # -----------------------------
    # Product Name
    # -----------------------------
    m = re.search(r"Product Name\s*:\s*(.+?)\s*(Product Details|Analysis Date|Species|$)", 
                  clean, re.IGNORECASE)
    if m:
        header_data["Product Name"] = m.group(1).strip()

    # -----------------------------
    # Analysis Date
    # -----------------------------
    m = re.search(r"Analysis Date\s*:\s*([\d/]+)", clean, re.IGNORECASE)
    if m:
        header_data["Analysis Date"] = m.group(1).strip()

    # Species + Life Stage 
    m = re.search(
        r"Species\s*:\s*(.+?)\s*Life Stage\s*:\s*(.+?)(?=per\s*1000\s*kcal)",
        clean,
        re.IGNORECASE
    )

    if m:
        header_data["Species"] = m.group(1).strip()
        header_data["Life Stage"] = m.group(2).strip()

    return header_data



def extract_table(page, bbox):
    #extrai o texto das tabelas
    text = page.within_bbox(bbox).extract_text()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    data = []

    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            nutrient = parts[0]
            unit = parts[1]
            val1 = parts[2]
            val2 = parts[3] if len(parts) > 3 else ""
            val3 = parts[4] if len(parts) > 4 else ""
            data.append({
                "Nutrient": nutrient,
                "Unit": unit,
                "Diet Analysis per 1000kcal": val1,
                "min": val2,
                "max": val3
            })
    return data


with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]

    # Cabeçalho
    header_data = extract_header(page)

    # Tabela da esquerda (Diet Analysis)
    left_box = (0, 220, 290, page.height)
    diet_data = extract_table(page, left_box)

    # Tabela da direita (LAB Results)
    right_box = (290, 220, page.width, page.height)
    lab_data = extract_table(page, right_box)

# Montar JSON 
final_json = {
    "Header": header_data,
    "DietAnalysis": diet_data,
    "LabResults": lab_data
}

# === Salvar ===
with open("resultado.json", "w", encoding="utf-8") as f:
    json.dump(final_json, f, indent=4, ensure_ascii=False)


print("✅ JSON criado com sucesso: resultado.json")
