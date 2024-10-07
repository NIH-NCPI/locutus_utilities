import subprocess
import argparse
import os
import sys

def run_make(target, project_id=None):
    """Run a make command with the specified target.

    Args:
        target (str): The make target to execute.
        project_id (str, optional): The project ID to set as an environment variable.
    
    Raises:
        subprocess.CalledProcessError: If the make command fails.
    """

    command = ["make", target]

    # Set the project ID as an environment variable if provided
    if project_id:
        env = os.environ.copy()  # Copy the current environment
        env["PROJECT_ID"] = project_id  # Set the new project ID
        try:
            print(f"Running command: {' '.join(command)}")
            subprocess.run(command, check=True, env=env)  # Pass the modified environment
            print(f"Successfully executed target '{target}' in Makefile.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing make target '{target}': {e}")
    else:
        try:
            print(f"Running command: {' '.join(command)}")
            subprocess.run(command, check=True)
            print(f"Successfully executed target '{target}' in Makefile.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing make target '{target}': {e}")

def main():
    """Main function to handle command-line arguments and execute make commands."""
    # Determine the command name
    command_name = os.path.basename(sys.argv[0])

    # Set the target based on the command name
    if command_name == "update_all_seed_data":
        target = "update_all_seed_data"
    else:
        print("Unknown command.")
        return

    # Parse the project argument
    parser = argparse.ArgumentParser(description="Wrapper to run Makefile actions.")
    parser.add_argument('-p', '--project', help="GCP Project ID to set.")

    args = parser.parse_args()

    # Run the make command with the specified target and project ID
    run_make(target, args.project)

if __name__ == "__main__":
    main()
