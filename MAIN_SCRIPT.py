import subprocess

scripts = [
    ("newspapers_scraper.py", "scrapy runspider"),
    ("laws_metadata_scraper.py", "python"),
    ("9ita3.py", "python"),
    ("pdfs_to_images_conversion.py", "python"),
    ("ocr_images.py", "python"),
    ("text_extraction.py", "python"),
    ("fix_law_texts.py", "python"),
    ("delete_all_photos.py", "python")
]

def run_scripts(script_list):
    for script, command in script_list:
        try:
            print(f"Executing {script} with command '{command}'...")
            if command == "scrapy runspider":
                result = subprocess.run(['scrapy', 'runspider', script], check=True)
            else:
                result = subprocess.run([command, script], check=True)

            if result.returncode == 0:
                print(f"{script} executed successfully.")
            else:
                print(f"{script} failed with return code {result.returncode}.")
                break 
        except subprocess.CalledProcessError as e:
            print(f"Execution failed: {e}")
            break 
        except Exception as e:
            print(f"An error occurred: {e}")
            break 
if __name__ == "__main__":
    run_scripts(scripts)
