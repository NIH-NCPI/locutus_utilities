import subprocess
import argparse
import os
import sys

def run_make(target, project_id):
    """Run a make command with the specified target.

    Args:
        target (str): The make target to execute.
        project_id (str): The project ID to set as an environment variable.
    """

    command = ["make", target, "-p", project_id]

    try:
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
        print(f"Successfully executed target '{target}' in Makefile.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing make target '{target}': {e}")

def main():
    """Main function to handle command-line arguments and execute make commands.
    """
    command_name = os.path.basename(sys.argv[0])

    # Set the target based on the command name
    if command_name == "update_all_seed_data":
        target = "update_all_seed_data"
    else:
        print("Unknown command.")
        return

    # Parse the project argument
    parser = argparse.ArgumentParser(description="Wrapper to run Makefile actions.")
    parser.add_argument('-p', '--project', required=True, help="GCP Project ID to set.")

    args = parser.parse_args()

    # Run the make command with the specified target and project ID
    run_make(target, args.project)

if __name__ == "__main__":
    main()
