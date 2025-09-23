import json
import os
from typing import Dict, List
import pandas as pd
from datetime import datetime

def save_parsed_resume(parsed_data: Dict, output_dir: str = "output"):
    """Save parsed resume data to JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    name = parsed_data.get('contact', {}).get('name', 'unknown')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name.replace(' ', '_')}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Save to JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)
    
    return filepath

def export_to_csv(parsed_results: List[Dict], output_file: str = "parsed_resumes.csv"):
    """Export multiple parsed resumes to CSV"""
    rows = []
    
    for result in parsed_results:
        if 'error' in result:
            continue
        
        row = {
            'Name': result.get('contact', {}).get('name', ''),
            'Email': result.get('contact', {}).get('email', ''),
            'Phone': result.get('contact', {}).get('phone', ''),
            'LinkedIn': result.get('contact', {}).get('linkedin', ''),
            'Skills': ', '.join(result.get('skills', [])),
            'Experience_Count': len(result.get('experience', [])),
            'Education_Count': len(result.get('education', [])),
            'Overall_Score': result.get('scores', {}).get('overall', 0)
        }
        
        # Add experience details
        for i, exp in enumerate(result.get('experience', [])[:3]):  # First 3 experiences
            row[f'Experience_{i+1}_Position'] = exp.get('position', '')
            row[f'Experience_{i+1}_Company'] = exp.get('company', '')
        
        # Add education details
        for i, edu in enumerate(result.get('education', [])[:2]):  # First 2 educations
            row[f'Education_{i+1}_Degree'] = edu.get('degree', '')
            row[f'Education_{i+1}_Institution'] = edu.get('institution', '')
        
        rows.append(row)
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False)
    
    return output_file

def generate_summary_report(parsed_data: Dict) -> str:
    """Generate a text summary of the parsed resume"""
    summary = []
    
    # Header
    summary.append("=" * 50)
    summary.append("RESUME SUMMARY REPORT")
    summary.append("=" * 50)
    
    # Contact Info
    contact = parsed_data.get('contact', {})
    summary.append(f"\nName: {contact.get('name', 'N/A')}")
    summary.append(f"Email: {contact.get('email', 'N/A')}")
    summary.append(f"Phone: {contact.get('phone', 'N/A')}")
    
    # Skills
    skills = parsed_data.get('skills', [])
    summary.append(f"\nSkills ({len(skills)}):")
    for skill in skills[:10]:  # Top 10 skills
        summary.append(f"  - {skill}")
    
    # Experience
    experience = parsed_data.get('experience', [])
    summary.append(f"\nExperience ({len(experience)} positions):")
    for i, exp in enumerate(experience[:3], 1):
        summary.append(f"\n  {i}. {exp.get('position', 'N/A')}")
        summary.append(f"     Company: {exp.get('company', 'N/A')}")
        summary.append(f"     Duration: {exp.get('duration', 'N/A')}")
    
    # Education
    education = parsed_data.get('education', [])
    summary.append(f"\nEducation ({len(education)} degrees):")
    for edu in education:
        summary.append(f"  - {edu.get('degree', 'N/A')}")
        summary.append(f"    {edu.get('institution', 'N/A')}")
    
    # Scores
    scores = parsed_data.get('scores', {})
    summary.append("\nCompleteness Scores:")
    summary.append(f"  - Contact Info: {scores.get('contact_info', 0):.1f}%")
    summary.append(f"  - Experience: {scores.get('experience', 0):.1f}%")
    summary.append(f"  - Education: {scores.get('education', 0):.1f}%")
    summary.append(f"  - Skills: {scores.get('skills', 0):.1f}%")
    summary.append(f"  - Overall: {scores.get('overall', 0):.1f}%")
    
    return "\n".join(summary)