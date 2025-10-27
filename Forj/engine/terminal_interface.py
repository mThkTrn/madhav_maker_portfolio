import os
import sys
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from synthesizer import Synthesizer

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the DataForge header."""
    clear_screen()
    print("""
╔══════════════════════════════════════════════╗
║             DATAFORGE ENGINE                ║
║    Custom Text Dataset Generation Tool      ║
╚══════════════════════════════════════════════╝
""")

def get_yes_no(prompt: str, default: str = 'y') -> bool:
    """Get yes/no input from user."""
    while True:
        response = input(f"{prompt} [{'Y/n' if default.lower() == 'y' else 'y/N'}] ").strip().lower()
        if not response:
            response = default
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        print("Please enter 'y' or 'n'.")

def get_required_input(prompt: str, default: str = None) -> str:
    """Get required input from user."""
    while True:
        response = input(f"{prompt} " + (f"[{default}]: " if default else ": ")).strip()
        if not response and default is not None:
            return default
        if response:
            return response
        print("This field is required. Please enter a value.")

def get_columns() -> List[str]:
    """Get column names from user."""
    print("\nEnter column names (comma-separated):")
    print("Example: patient_id,age,gender,complaint,duration,severity")
    while True:
        columns_input = input("> ").strip()
        if not columns_input:
            print("Please enter at least one column name.")
            continue
        
        columns = [col.strip() for col in columns_input.split(',')]
        columns = [col for col in columns if col]  # Remove empty strings
        
        if not columns:
            print("Please enter valid column names.")
            continue
            
        print("\nYou've entered the following columns:")
        for i, col in enumerate(columns, 1):
            print(f"{i}. {col}")
            
        if get_yes_no("\nIs this correct?"):
            return columns

def get_volume() -> int:
    """Get the number of rows to generate."""
    while True:
        try:
            volume = input("\nEnter the number of rows to generate (default: 100): ").strip()
            if not volume:
                return 100
            volume = int(volume)
            if volume <= 0:
                print("Please enter a positive number.")
                continue
            return volume
        except ValueError:
            print("Please enter a valid number.")

def save_dataset(dataset: List[List[str]], columns: List[str], description: str) -> str:
    """
    Save the dataset to a CSV file.
    
    Args:
        dataset: List of rows to save
        columns: List of column names
        description: Dataset description for filename
        
    Returns:
        Path to the saved file, or empty string on failure
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_description = "".join(c if c.isalnum() else "_" for c in description)[:50]
        filename = f"dataset_{safe_description}_{timestamp}.csv"
        
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write UTF-8 BOM for better Excel compatibility
            f.write("\ufeff")
            # Write header
            f.write(",".join(f'"{col}"' for col in columns) + "\n")
            # Write data
            for row in dataset:
                # Escape any double quotes and wrap in quotes
                escaped_row = []
                for value in row:
                    if not isinstance(value, str):
                        value = str(value)
                    escaped = value.replace('"', '""')
                    escaped_row.append(f'"{escaped}"')
                f.write(",".join(escaped_row) + "\n")
                
        return str(filepath.absolute())
    except Exception as e:
        print(f"Error saving dataset: {e}")
        import traceback
        traceback.print_exc()
        return ""

def display_sample(dataset: List[List[str]], columns: List[str], num_samples: int = 5):
    """Display a sample of the generated dataset."""
    print("\nSample of generated data:")
    print("-" * 80)
    
    # Print header
    print("  " + " | ".join(f"{col:<15}" for col in columns))
    print("-" * 80)
    
    # Print sample rows
    for i, row in enumerate(dataset[:num_samples], 1):
        print(f"{i:2}.", end=" ")
        for j, value in enumerate(row):
            display_value = (value[:12] + '...') if len(value) > 15 else value
            print(f"{display_value:<15}", end=" | " if j < len(row) - 1 else "\n")
    
    print("-" * 80)
    print(f"Total rows generated: {len(dataset)}")

def main():
    """Main terminal interface for DataForge."""
    print_header()
    
    # Initialize synthesizer with default API key
    try:
        synthesizer = Synthesizer()
    except Exception as e:
        print(f"Error initializing synthesizer: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)
    
    # Main loop
    while True:
        print_header()
        print("1. Create a new dataset")
        print("2. Exit")
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == '1':
            create_dataset_flow(synthesizer)
        elif choice == '2':
            print("\nThank you for using DataForge. Goodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")
            input("Press Enter to continue...")

def create_dataset_flow(synthesizer: Synthesizer):
    """Guide the user through the dataset creation process."""
    print_header()
    print("📊 Dataset Creation")
    print("-" * 40)
    
    # Get dataset description
    description = get_required_input("\nEnter a description of the dataset you want to generate:")
    
    # Get columns
    columns = get_columns()
    
    # Get volume
    volume = get_volume()
    
    print("\nGenerating dataset. This may take a few minutes...")
    
    try:
        # Generate dataset with pipeline tracking
        dataset, log_path = synthesizer.create_dataset(description, columns, volume)
        
        # Display sample of the final dataset
        display_sample(dataset, columns)
        
        # Save the final dataset to file
        filepath = save_dataset(dataset, columns, description)
        
        # Show results to user
        if filepath:
            print(f"\n✅ Dataset saved to: {filepath}")
            print(f"📝 Pipeline log saved to: {log_path}")
            print("\nPipeline Summary:")
            print("-" * 40)
            if hasattr(synthesizer, 'pipeline'):
                print(synthesizer.pipeline.get_summary())
        else:
            print("\n❌ Failed to save dataset.")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        if hasattr(synthesizer, 'pipeline') and hasattr(synthesizer.pipeline, 'log_file'):
            print(f"Check the log file for details: {synthesizer.pipeline.log_file.absolute()}")
    
    input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
