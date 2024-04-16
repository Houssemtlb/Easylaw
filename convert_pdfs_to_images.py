import os
import logging
from pdf2image import convert_from_path

# Configure logging
logging.basicConfig(level=logging.INFO,
                    filename='conversion.log',
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def convert_pdfs_to_images(base_dir, batch_size=5):
    pdf_files = []
    # Walk the directory to list all PDF files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".pdf"):
                # Construct PDF file path and append it to the list
                pdf_files.append(os.path.join(root, file))

    # Process PDFs in batches
    for i in range(0, len(pdf_files), batch_size):
        batch = pdf_files[i : i + batch_size]
        for pdf_path in batch:
            logging.info(f"Starting conversion of {pdf_path}")
            # Create a directory for the images, stripping .pdf and replacing with nothing
            img_dir = pdf_path.rsplit(".", 1)[0]
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
                logging.info(f"Created directory {img_dir}")

            try:
                # Convert PDF to images
                images = convert_from_path(pdf_path)
                
                # Save each page as an image
                for j, image in enumerate(images):
                    image_path = os.path.join(img_dir, f"{j+1}.jpg")
                    image.save(image_path, "JPEG")
                    logging.info(f"Saved image {image_path}")
            except Exception as e:
                logging.error(f"Error converting {pdf_path}: {e}")

convert_pdfs_to_images("joradp_pdfs")
