import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class PipelineStep:
    """Represents a single step in the data generation pipeline."""
    step_number: int
    timestamp: str
    generation_prompt: str
    meta_statistics: Dict[str, float]
    samples: List[Dict[str, str]] = field(default_factory=list)
    feedback: List[Dict[str, Any]] = field(default_factory=list)
    updated_prompt: Optional[str] = None
    
    def to_dict(self):
        """Convert the step to a dictionary for serialization."""
        return {
            'step_number': self.step_number,
            'timestamp': self.timestamp,
            'generation_prompt': self.generation_prompt,
            'meta_statistics': self.meta_statistics,
            'samples': self.samples,
            'feedback': self.feedback,
            'updated_prompt': self.updated_prompt
        }

class PipelineTracker:
    """Tracks the entire data generation pipeline with all its steps."""
    
    def __init__(self, output_dir: str = "pipeline_logs"):
        """Initialize the pipeline tracker.
        
        Args:
            output_dir: Directory to save pipeline logs
        """
        self.steps: List[PipelineStep] = []
        self.current_step: Optional[PipelineStep] = None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create a unique run ID
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.output_dir / f"pipeline_run_{self.run_id}.json"
        
    def start_step(self, generation_prompt: str, meta_statistics: Dict[str, float]) -> None:
        """Start a new pipeline step.
        
        Args:
            generation_prompt: The prompt used for this generation step
            meta_statistics: The meta statistics used for this step
        """
        self.current_step = PipelineStep(
            step_number=len(self.steps) + 1,
            timestamp=datetime.now().isoformat(),
            generation_prompt=generation_prompt,
            meta_statistics=meta_statistics.copy()
        )
    
    def add_samples(self, samples: List[Dict[str, str]]) -> None:
        """Add generated samples to the current step.
        
        Args:
            samples: List of generated samples with their metadata
        """
        if self.current_step:
            self.current_step.samples = samples
    
    def add_feedback(self, feedback: List[Dict[str, Any]]) -> None:
        """Add user feedback to the current step.
        
        Args:
            feedback: List of feedback items with approval status and comments
        """
        if self.current_step:
            self.current_step.feedback = feedback
    
    def update_prompt(self, updated_prompt: str) -> None:
        """Update the prompt after feedback.
        
        Args:
            updated_prompt: The new prompt after incorporating feedback
        """
        if self.current_step:
            self.current_step.updated_prompt = updated_prompt
    
    def end_step(self) -> None:
        """Finalize the current step and save to log."""
        if self.current_step:
            self.steps.append(self.current_step)
            self._save_log()
            self.current_step = None
    
    def _save_log(self) -> None:
        """Save the current pipeline state to a JSON log file."""
        log_data = {
            'run_id': self.run_id,
            'start_time': self.steps[0].timestamp if self.steps else datetime.now().isoformat(),
            'current_time': datetime.now().isoformat(),
            'total_steps': len(self.steps),
            'steps': [step.to_dict() for step in self.steps]
        }
        
        # Save the complete log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        # Also save a human-readable version
        human_readable = self._format_human_readable(log_data)
        with open(str(self.log_file).replace('.json', '.txt'), 'w', encoding='utf-8') as f:
            f.write(human_readable)
    
    def _format_human_readable(self, log_data: Dict) -> str:
        """Format the log data in a human-readable way."""
        output = [
            f"DataForge Pipeline Run: {log_data['run_id']}",
            f"Started: {log_data['start_time']}",
            f"Current: {log_data['current_time']}",
            f"Total Steps: {log_data['total_steps']}",
            "=" * 80,
            ""
        ]
        
        for step in log_data['steps']:
            output.extend([
                f"Step {step['step_number']} - {step['timestamp']}",
                "-" * 40,
                "\nMeta Statistics:",
                "\n".join(f"- {k}: {v:.4f}" for k, v in step['meta_statistics'].items()),
                "\nGeneration Prompt:",
                step['generation_prompt'],
                "\nSamples:"
            ])
            
            for i, sample in enumerate(step['samples'], 1):
                output.append(f"\nSample {i}:")
                for k, v in sample.items():
                    output.append(f"  {k}: {v[:200]}{'...' if len(str(v)) > 200 else ''}")
            
            if step['feedback']:
                output.append("\nFeedback:")
                for i, fb in enumerate(step['feedback'], 1):
                    approved = "✓" if fb.get('approved', False) else "✗"
                    comment = fb.get('qualitative', 'No comment')
                    output.append(f"  {approved} {comment}")
            
            if step['updated_prompt']:
                output.extend([
                    "\nUpdated Prompt:",
                    step['updated_prompt']
                ])
            
            output.append("\n" + "=" * 80 + "\n")
        
        return "\n".join(output)
    
    def get_summary(self) -> str:
        """Get a summary of the pipeline run."""
        if not self.steps:
            return "No steps completed yet."
            
        last_step = self.steps[-1]
        return (
            f"Pipeline Run: {self.run_id}\n"
            f"Steps: {len(self.steps)}\n"
            f"Samples Generated: {sum(len(step.samples) for step in self.steps)}\n"
            f"Latest Statistics: {', '.join(f'{k}={v:.2f}' for k, v in last_step.meta_statistics.items())}"
        )
