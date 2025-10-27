from openai import OpenAI
import random
from typing import List, Dict, Any, Tuple, Optional, Union
import json
from meta_statistics import MetaStatistics, StatisticRange
from pipeline_tracker import PipelineTracker
import os
from datetime import datetime

# Initialize the OpenAI client with the hardcoded API key
DEFAULT_API_KEY = "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"
client = OpenAI(api_key=DEFAULT_API_KEY)

class Synthesizer:
    def __init__(self, model: str = "gpt-4-1106-preview", log_dir: str = "pipeline_logs"):
        """
        Initialize the DataForge Synthesizer.
        
        Args:
            model: The OpenAI model to use for generation (default: gpt-4-1106-preview).
            log_dir: Directory to save pipeline logs
        """
        self.model = model
        self.generation_prompt = ""
        self.columns = []  # Will store the current columns being used
        self.meta_stats = MetaStatistics()  # Initialize meta statistics
        self.current_stats = {}  # Store stats for the current generation
        self.pipeline = PipelineTracker(output_dir=log_dir)  # Initialize pipeline tracker
        
    def prompt_llm(self, prompt: str) -> str:
        """
        Interface with OpenAI's API to get a completion using the chat API.

        Args:
            prompt: The prompt to send to the LLM.

        Returns:
            The generated text response.
        """
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates synthetic data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                top_p=0.95
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise

    
    def _get_statistics_prompt(self) -> str:
        """Get the prompt section for current statistics."""
        if not hasattr(self, 'current_stats') or not self.current_stats:
            return ""
            
        stats = self.current_stats
        prompt_parts = ["\n\nGeneration Guidelines:"]
        
        # Word count guidance
        if 'word_count' in stats:
            wc = stats['word_count']
            if wc < 10:
                prompt_parts.append("- Be very concise (under 10 words).")
            elif wc < 20:
                prompt_parts.append("- Be brief (10-20 words).")
            elif wc > 30:
                prompt_parts.append("- Be detailed (30+ words).")
        
        # Sentiment guidance
        if 'sentiment' in stats:
            sentiment = stats['sentiment']
            if sentiment < 0.3:
                prompt_parts.append("- Use a negative tone.")
            elif sentiment < 0.6:
                prompt_parts.append("- Use a neutral tone.")
            else:
                prompt_parts.append("- Use a positive tone.")
        
        # Formality guidance
        if 'formality' in stats:
            formality = stats['formality']
            if formality < 0.3:
                prompt_parts.append("- Use casual, conversational language.")
            elif formality > 0.7:
                prompt_parts.append("- Use formal, professional language.")
        
        return "\n".join(prompt_parts)

    def create_initial_generation_prompt(self, description: str, columns: List[str]) -> str:
        """
        Create the initial prompt for data generation.
        
        Args:
            description: Description of the dataset.
            columns: List of column names.
            
        Returns:
            Formatted prompt string.
        """
        self.columns = columns  # Store columns for later use
        columns_str = ", ".join(columns)
        
        # Get statistics for this generation
        self.current_stats = self.meta_stats.get_all_statistics()
        stats_prompt = self._get_statistics_prompt()
        
        prompt = f"""You are a synthetic data generation engine which creates custom text datasets. 
Create a row for a dataset which is described as: "{description}"

Generate exactly {len(columns)} columns with these exact names: {columns_str}

IMPORTANT RULES:
1. Generate EXACTLY {len(columns)} columns - no more, no less
2. Separate values with commas
3. If a value contains a comma, enclose it in double quotes
4. Do not include any additional text or explanations
5. Do not include the column headers in the output
{stats_prompt}

Example output for 3 columns (name, age, city):
John Doe,42,"New York, NY"

Now generate a row with these {len(columns)} columns: {columns_str}

Generated row:"""
        self.generation_prompt = prompt
        return prompt
    
    def _parse_csv_row(self, response: str) -> List[str]:
        """Parse a single CSV row from the LLM response."""
        row = []
        in_quotes = False
        current_value = []
        
        i = 0
        while i < len(response):
            char = response[i]
            if char == '"':
                if i + 1 < len(response) and response[i+1] == '"':  # escaped quote
                    current_value.append('"')
                    i += 1
                else:
                    in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                row.append(''.join(current_value).strip())
                current_value = []
                # If we've reached the expected number of columns, stop parsing
                if len(row) >= len(self.columns):
                    break
            else:
                current_value.append(char)
            i += 1
        
        # Add the last value if we haven't reached the column limit
        if current_value and len(row) < len(self.columns):
            row.append(''.join(current_value).strip())
        
        # Ensure we have exactly the right number of columns
        if len(row) > len(self.columns):
            row = row[:len(self.columns)]
        elif len(row) < len(self.columns):
            # If we're short, pad with empty strings
            row.extend([''] * (len(self.columns) - len(row)))
            
        return row
    
    def generate_samples(self, count: int = 5, prompt: str = None) -> List[List[str]]:
        """
        Generate multiple unrelated rows of data at once.
        
        Args:
            count: Number of rows to generate (default: 5).
            prompt: Optional custom prompt. If not provided, uses the current generation_prompt.
            
        Returns:
            List of rows, where each row is a list of column values.
        """
        current_prompt = prompt or self.generation_prompt
        
        # Update prompt to request multiple unrelated rows
        batch_prompt = f"""{current_prompt}

IMPORTANT: Generate {count} COMPLETELY UNRELATED rows of data. Each row should be distinct and independent.
Make sure the data is diverse and covers different scenarios.

Format your response as:
""Value 1","Value 2",...
"Value 1","Value 2",...
...""

Generated rows:"""
        
        response = self.prompt_llm(batch_prompt)
        
        # Split response into lines and parse each line as a separate row
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        rows = []
        
        for line in lines[:count]:  # Take up to 'count' rows
            if line:  # Skip empty lines
                try:
                    row = self._parse_csv_row(line)
                    if len(row) == len(self.columns):  # Only add if it has the right number of columns
                        rows.append(row)
                except Exception as e:
                    print(f"Warning: Error parsing row: {e}")
        
        return rows
    
    def create_sample_set(self, num_samples: int = 5) -> List[List[str]]:
        """
        Generate multiple samples for user review.
        
        Args:
            num_samples: Number of samples to generate.
            
        Returns:
            List of generated samples, each as a list of column values.
        """
        # Generate samples in batches of 5 for efficiency
        samples = []
        remaining = num_samples
        
        while remaining > 0:
            batch_size = min(5, remaining)
            batch = self.generate_samples(count=batch_size)
            samples.extend(batch)
            remaining -= len(batch)
            
            # If we didn't get enough samples, try again with a smaller batch
            if remaining > 0 and len(batch) < batch_size:
                print(f"Warning: Only got {len(batch)}/{batch_size} samples. Retrying...")
                continue
                
        return samples[:num_samples]  # Ensure we don't return more than requested
    
    def collect_feedback(self, samples: List[List[str]]) -> Dict[str, Dict[str, Any]]:
        """
        Collect feedback on generated samples.
        
        Args:
            samples: List of generated samples.
            
        Returns:
            Dictionary with feedback for each sample.
        """
        feedback = {}
        print("\nPlease review the following samples:")
        
        for i, sample in enumerate(samples, 1):
            sample_str = ", ".join(f'"{val}"' for val in sample)
            print(f"\nSample {i}:")
            print(sample_str)
            
            approved = input("Are you satisfied with this sample? (y/n): ").lower().strip() == 'y'
            qualitative = input("Any qualitative feedback (or press Enter for none): ").strip()
            
            feedback[sample_str] = {
                "approved": approved,
                "qualitative": qualitative if qualitative else "No feedback provided"
            }
            
        return feedback
    
    def update_generation_prompt(self, feedback: Dict[str, Dict[str, Any]]) -> str:
        """
        Update the generation prompt based on feedback.
        
        Args:
            feedback: Dictionary containing feedback on samples.
            
        Returns:
            Updated generation prompt.
        """
        if not feedback:
            return self.generation_prompt
            
        feedback_summary = []
        
        for sample, fb in feedback.items():
            status = "APPROVED" if fb.get("approved", False) else "REJECTED"
            feedback_summary.append(f"- Sample: {sample}\n  Status: {status}\n  Feedback: {fb.get('qualitative', 'No feedback')}")
        
        feedback_text = "\n".join(feedback_summary)
        
        # Update meta statistics based on feedback
        self.meta_stats.update_from_feedback(feedback)
        
        # Get new statistics for the next generation
        self.current_stats = self.meta_stats.get_all_statistics()
        stats_prompt = self._get_statistics_prompt()
        
        # Create a more structured update prompt
        update_prompt = f"""I need to improve the data generation prompt based on user feedback. 
Current prompt:
```
{self.generation_prompt}
```

User feedback on previous samples:
{feedback_text}

Please generate an improved version of the prompt that:
1. Maintains all the original requirements
2. Addresses the feedback provided
3. Is even more explicit about generating exactly {len(self.columns)} columns
4. Includes any specific formatting requirements mentioned in the feedback
5. Incorporates these generation guidelines:
{stats_prompt}
6. Is clear and unambiguous

IMPORTANT: The response should ONLY contain the new prompt, with no additional commentary or explanation.

Improved prompt:"""
        
        try:
            updated_instructions = self.prompt_llm(update_prompt).strip()
            # Ensure the updated instructions maintain the required format
            if 'Generated row:' not in updated_instructions:
                updated_instructions += "\n\nGenerated row:"
            self.generation_prompt = updated_instructions
            return updated_instructions
        except Exception as e:
            print(f"Error updating generation prompt: {e}")
            return self.generation_prompt  # Return the old prompt if update fails
    
    def _format_samples_for_display(self, samples: List[List[str]]) -> List[Dict[str, str]]:
        """Format samples as a list of dictionaries with column names as keys."""
        return [dict(zip(self.columns, sample)) for sample in samples]

    def collect_feedback(self, samples: List[List[str]]) -> Dict[str, Dict[str, Any]]:
        """
        Collect feedback on generated samples with pipeline tracking.
        
        Args:
            samples: List of generated samples.
            
        Returns:
            Dictionary with feedback for each sample.
        """
        feedback = {}
        formatted_samples = self._format_samples_for_display(samples)
        
        # Log the samples to the pipeline
        if hasattr(self, 'pipeline') and self.pipeline.current_step:
            self.pipeline.add_samples(formatted_samples)
        
        print("\nPlease review the following samples:")
        
        for i, (sample, formatted_sample) in enumerate(zip(samples, formatted_samples), 1):
            sample_str = ", ".join(f'"{val}"' for val in sample)
            print(f"\nSample {i}:")
            print(sample_str)
            
            approved = input("Are you satisfied with this sample? (y/n): ").lower().strip() == 'y'
            qualitative = input("Any qualitative feedback (or press Enter for none): ").strip()
            
            feedback[sample_str] = {
                "approved": approved,
                "qualitative": qualitative if qualitative else "No feedback provided"
            }
        
        # Add feedback to pipeline
        if hasattr(self, 'pipeline') and self.pipeline.current_step:
            self.pipeline.add_feedback(list(feedback.values()))
            
        return feedback

    def create_dataset(self, description: str, columns: List[str], volume: int = 100, interactive: bool = True) -> tuple:
        """
        Create a dataset with the given description and columns.
        
        Args:
            description: Description of the dataset.
            columns: List of column names.
            volume: Number of rows to generate.
            interactive: Whether to run in interactive mode (show prompts in terminal).
            
        Returns:
            Tuple of (dataset, log_path) where dataset is a list of rows and log_path is the path to the pipeline log.
        """
        # Initialize pipeline tracking
        self.pipeline = PipelineTracker()
        
        # Create initial generation prompt
        self.create_initial_generation_prompt(description, columns)
        
        feedback_round = 0
        
        # Skip feedback loop in non-interactive mode
        if interactive:
            # Initial feedback loop
            while feedback_round < 5:  # Maximum of 5 feedback rounds
                # Start a new pipeline step
                self.pipeline.start_step(
                    generation_prompt=self.generation_prompt,
                    meta_statistics=self.current_stats
                )
                
                # Generate samples for review
                print(f"\n--- Feedback Round {feedback_round + 1} ---")
                samples = self.create_sample_set()
                
                # Get feedback
                feedback = self.collect_feedback(samples)
                
                # Check if all samples are approved
                all_approved = all(fb.get("approved", False) for fb in feedback.values())
                
                # Update prompt based on feedback
                if not all_approved:
                    print("\nUpdating generation prompt based on feedback...")
                    updated_prompt = self.update_generation_prompt(feedback)
                    if hasattr(self, 'pipeline') and self.pipeline.current_step:
                        self.pipeline.update_prompt(updated_prompt)
                
                # End the current pipeline step
                if hasattr(self, 'pipeline') and self.pipeline.current_step:
                    self.pipeline.end_step()
                
                if all_approved:
                    print("\nAll samples approved! Generating full dataset...")
                    break
                    
                feedback_round += 1
        
        # Generate final dataset in batches for efficiency
        final_dataset = []
        remaining = volume
        
        # Generate in batches of 5
        while remaining > 0:
            batch_size = min(5, remaining)
            batch = self.generate_samples(count=batch_size)
            final_dataset.extend(batch)
            remaining -= len(batch)
            
            if interactive:
                print(f"Generated {len(final_dataset)}/{volume} rows...")
            
            # If we didn't get enough samples, try again with a smaller batch
            if remaining > 0 and len(batch) < batch_size:
                if interactive:
                    print(f"Warning: Only got {len(batch)}/{batch_size} samples. Retrying...")
                continue
        
        # Ensure we have exactly the requested number of rows
        final_dataset = final_dataset[:volume]
        
        # Save final pipeline state
        if hasattr(self, 'pipeline'):
            log_path = str(self.pipeline.log_file.absolute())
            if interactive:
                print(f"\nPipeline log saved to: {log_path}")
        else:
            log_path = ""
            
        return final_dataset, log_path

# Example usage
if __name__ == "__main__":
    # Initialize with your OpenAI API key
    synthesizer = Synthesizer(api_key="your-api-key-here")
    
    # Example usage
    description = "patient complaints due to early stage lung cancer in a clinic in Ghana"
    columns = ["patient_id", "age", "gender", "complaint", "duration", "severity"]
    volume = 10  # Number of rows in final dataset
    
    dataset = synthesizer.create_dataset(description, columns, volume)
    
    # Print the final dataset
    print("\nFinal Dataset:")
    for row in dataset:
        print(", ".join(f'"{val}"' for val in row))
