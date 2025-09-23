import os
import sys
from resume_parser import ResumeParser
from advanced_parser import AdvancedResumeParser
from utils import save_parsed_resume, export_to_csv, generate_summary_report
import argparse
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_single_resume(file_path: str, use_advanced: bool = False):
    """Parse a single resume file"""
    # Initialize parser
    if use_advanced:
        parser = AdvancedResumeParser()
        parsed_data = parser.parse_advanced(file_path)
    else:
        parser = ResumeParser()
        parsed_data = parser.parse(file_path)
    
    # Save results
    output_path = save_parsed_resume(parsed_data)
    logger.info(f"Saved parsed data to: {output_path}")
    
    # Generate and print summary
    summary = generate_summary_report(parsed_data)
    print(summary)
    
    return parsed_data

def parse_multiple_resumes(directory: str, use_advanced: bool = False):
    """Parse all resumes in a directory"""
    results = []
    
    # Get all resume files
    resume_files = []
    for file in os.listdir(directory):
        if file.endswith(('.pdf', '.docx', '.txt')):
            resume_files.append(os.path.join(directory, file))
    
    logger.info(f"Found {len(resume_files)} resume files")
    
    # Parse each file
    for file_path in resume_files:
        logger.info(f"Parsing: {file_path}")
        try:
            parsed_data = parse_single_resume(file_path, use_advanced)
            results.append(parsed_data)
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            results.append({'error': str(e), 'file': file_path})
    
    # Export to CSV
    if results:
        csv_path = export_to_csv(results)
        logger.info(f"Exported results to: {csv_path}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Resume Parser & Information Extractor')
    parser.add_argument('path', help='Path to resume file or directory')
    parser.add_argument('--advanced', action='store_true', help='Use advanced NLP parsing')
    parser.add_argument('--output', default='output', help='Output directory for results')
    
    args = parser.parse_args()
    
    # Check if path exists
    if not os.path.exists(args.path):
        logger.error(f"Path does not exist: {args.path}")
        sys.exit(1)
    
    # Parse resume(s)
    if os.path.isfile(args.path):
        # Single file
        parse_single_resume(args.path, args.advanced)
    elif os.path.isdir(args.path):
        # Directory of resumes
        parse_multiple_resumes(args.path, args.advanced)
    else:
        logger.error("Invalid path provided")
        sys.exit(1)

if __name__ == "__main__":
    main()