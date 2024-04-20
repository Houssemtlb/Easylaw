from multiprocessing import Pool, Value, Lock, current_process
import os
import logging
from pdf2image import convert_from_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="conversion.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Define the shared counter and lock globally so that they are inherited
total_files = None  # This will be set later
count = Value('i', 0)  # Shared counter
lock = Lock()  # Mutex for accessing the shared counter

def convert_pdf_to_images(pdf_path):
    try:
        logging.info(f"Starting conversion of {pdf_path}")
        # Create a directory for the images, stripping .pdf and replacing with nothing
        imgs_dir = pdf_path.rsplit(".", 1)[0]
        if not os.path.exists(imgs_dir):
            os.makedirs(imgs_dir)
            logging.info(f"Created directory {imgs_dir}")

        # Convert PDF to images
        convert_from_path(
            pdf_path=pdf_path,
            output_folder=imgs_dir,
            fmt='jpeg',
            output_file="page",
            # Adjust the number of threads as necessary
            thread_count=2,
            paths_only=True,
        )
        logging.info(f"Saved images of {pdf_path} to {imgs_dir}")

        with lock:
            count.value += 1
            percentage_complete = (count.value / total_files) * 100
            print(f"Conversion progress: {percentage_complete:.2f}% ({count.value} / {total_files} files) completed by {current_process().name}.")
    except Exception as e:
        logging.error(f"Error converting {pdf_path}: {e}")

def convert_pdfs_to_images(base_dir):
    global total_files
    # Walk the directory to list all PDF files
    # Construct PDF file path and append it to the list
    pdf_files = [os.path.join(root, file) for root, _, files in os.walk(base_dir) for file in files if file.endswith(".pdf")]
    total_files = len(pdf_files)  # Set the total number of files to be processed

    # Adjust the number of precesses as necessary
    with Pool(processes=8) as pool:
        pool.map(convert_pdf_to_images, pdf_files)

# Adjust the path as necessary
convert_pdfs_to_images("joradp_pdfs_houssem_2")
