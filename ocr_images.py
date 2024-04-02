import os
from PIL import Image
import pytesseract

def image_to_text(base_dir, lang='eng'):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Construct image file path
                img_path = os.path.join(root, file)
                
                # Attempt to perform OCR using pytesseract
                try:
                    text = pytesseract.image_to_string(Image.open(img_path), lang=lang)
                    
                    # Construct text file path
                    txt_file_path = f"{img_path.rsplit('.', 1)[0]}.txt"
                    
                    # Save the extracted text to a .txt file
                    with open(txt_file_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")

image_to_text('joradp_pdfs', 'ara')
