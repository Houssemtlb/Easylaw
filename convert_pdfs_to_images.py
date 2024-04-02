import os
from pdf2image import convert_from_path

def convert_pdfs_to_images(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.pdf'):
                # Construct PDF file path
                pdf_path = os.path.join(root, file)
                
                # Create a directory for the images, stripping .pdf and replacing with nothing
                img_dir = pdf_path.rsplit('.', 1)[0]
                if not os.path.exists(img_dir):
                    os.makedirs(img_dir)

                # Convert PDF to images
                images = convert_from_path(pdf_path)
                
                # Save each page as an image
                for i, image in enumerate(images):
                    image_path = os.path.join(img_dir, f'{i+1}.jpg')
                    image.save(image_path, 'JPEG')

convert_pdfs_to_images('joradp_pdfs')
