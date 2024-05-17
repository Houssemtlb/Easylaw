import subprocess
import os

# List of script filenames
scripts = [
    "script1.py",
    "script2.py",
    "script3.py",
    # Add more scripts as needed
]

def run_scripts(script_list):
    for script in script_list:
        try:
            print(f"Executing {script}...")
            # Execute the script
            result = subprocess.run(['python', script], check=True)
            # Check if the script executed successfully
            if result.returncode == 0:
                print(f"{script} executed successfully.")
            else:
                print(f"{script} failed with return code {result.returncode}.")
                break  # Optional: stop if a script fails
        except subprocess.CalledProcessError as e:
            print(f"Execution failed: {e}")
            break  # Optional: stop if a script fails
        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Optional: stop if a script fails

if __name__ == "__main__":
    run_scripts(scripts)
