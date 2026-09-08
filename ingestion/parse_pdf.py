import pymupdf  # Modern PyMuPDF import  # PyMuPDF
import json
import os

def extract_pdf_blocks(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return []

    # 1. Open the PDF document
    # Change doc = fitz.open(pdf_path) to:
    doc = pymupdf.open(pdf_path)
    extracted_data = []

    # 2. Iterate through each page
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 3. Extract text blocks: returns tuples of (x0, y0, x1, y1, "text", block_no, block_type)
        blocks = page.get_text("blocks")
        
        for b in blocks:
            # b[6] == 0 indicates text (b[6] == 1 indicates image)
            if b[6] == 0:
                text = b[4].strip()
                if text:  # Filter out empty whitespace blocks
                    extracted_data.append({
                        "page_number": page_num + 1,  # 1-indexed page numbering
                        "bbox": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)],
                        "text": text
                    })

    return extracted_data

if __name__ == "__main__":
    # Specify your test PDF path
    pdf_file = "sample.pdf"  
    output_json = "ingestion/extracted_output.json"

    data = extract_pdf_blocks(pdf_file)

    if data:
        # Save output to JSON
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Successfully extracted {len(data)} text blocks into '{output_json}'.")