import spacy
from spacy.matcher import Matcher
import nltk
from typing import Dict, List
from resume_parser import ResumeParser

class AdvancedResumeParser(ResumeParser):
    def __init__(self):
        super().__init__()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize matcher for pattern matching
        self.matcher = Matcher(self.nlp.vocab)
        self._setup_matchers()
        
        # Download NLTK data
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
    
    def _setup_matchers(self):
        """Setup spaCy matchers for various patterns"""
        # Job title patterns
        job_patterns = [
            [{"POS": "ADJ", "OP": "?"}, {"POS": "NOUN"}, {"TEXT": {"IN": ["Engineer", "Developer", "Manager", "Analyst"]}}],
            [{"TEXT": {"IN": ["Senior", "Junior", "Lead"]}}, {"POS": "NOUN"}, {"POS": "NOUN"}],
        ]
        self.matcher.add("JOB_TITLE", job_patterns)
        
        # Company patterns
        company_patterns = [
            [{"POS": "PROPN", "OP": "+"}, {"TEXT": {"IN": ["Inc", "LLC", "Corp", "Corporation", "Ltd", "Limited"]}}],
            [{"POS": "PROPN", "OP": "+"}, {"TEXT": {"IN": ["Technologies", "Solutions", "Systems", "Software", "Consulting"]}}],
        ]
        self.matcher.add("COMPANY", company_patterns)
    
    def extract_name_nlp(self, text: str) -> Optional[str]:
        """Extract name using advanced NLP"""
        # Process first few lines where name is likely to be
        first_lines = '\n'.join(text.split('\n')[:10])
        doc = self.nlp(first_lines)
        
        # Look for PERSON entities
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        # Filter and validate person names
        for person in persons:
            # Check if it's a valid name format
            words = person.split()
            if 2 <= len(words) <= 4:
                # Check if all words start with capital
                if all(w[0].isupper() for w in words if w):
                    # Avoid common false positives
                    if not any(skip in person.lower() for skip in ['university', 'college', 'company']):
                        return person
        
        return super().extract_name(text)  # Fallback to regex method
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract all named entities from text"""
        doc = self.nlp(text)
        
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'money': [],
            'percentages': []
        }
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities['persons'].append(ent.text)
            elif ent.label_ == "ORG":
                entities['organizations'].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities['locations'].append(ent.text)
            elif ent.label_ == "DATE":
                entities['dates'].append(ent.text)
            elif ent.label_ == "MONEY":
                entities['money'].append(ent.text)
            elif ent.label_ == "PERCENT":
                entities['percentages'].append(ent.text)
        
        return entities
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases using NLP"""
        doc = self.nlp(text)
        
        key_phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            # Filter out common/stop words
            if len(chunk.text.split()) > 1 and not all(token.text.lower() in self.stopwords for token in chunk):
                key_phrases.append(chunk.text)
        
        # Extract verb phrases for action items
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                # Get the verb phrase
                phrase_tokens = [child for child in token.subtree]
                phrase = ' '.join([t.text for t in phrase_tokens])
                if len(phrase.split()) > 2 and len(phrase.split()) < 8:
                    key_phrases.append(phrase)
        
        return list(set(key_phrases))[:20]  # Return top 20 unique phrases
    
    def extract_achievements(self, text: str) -> List[str]:
        """Extract achievements and accomplishments"""
        achievements = []
        
        # Patterns that indicate achievements
        achievement_keywords = [
            'achieved', 'accomplished', 'awarded', 'earned', 'recognized',
            'improved', 'increased', 'decreased', 'reduced', 'saved',
            'generated', 'developed', 'created', 'built', 'established',
            'led', 'managed', 'directed', 'spearheaded', 'initiated'
        ]
        
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        for sentence in sentences:
            # Check if sentence contains achievement keywords
            if any(keyword in sentence.lower() for keyword in achievement_keywords):
                # Check if sentence contains numbers/metrics
                if any(char.isdigit() for char in sentence) or any(symbol in sentence for symbol in ['%', '$']):
                    achievements.append(sentence.strip())
        
        return achievements[:10]  # Return top 10 achievements
    
    def analyze_experience_level(self, parsed_data: Dict) -> str:
        """Analyze and determine experience level"""
        experience = parsed_data.get('experience', [])
        
        if not experience:
            return "Entry Level"
        
        # Calculate total years of experience
        total_months = 0
        
        for exp in experience:
            duration = exp.get('duration', '')
            # Extract dates and calculate duration
            dates = re.findall(r'(\w+\s+\d{4})', duration)
            
            if len(dates) >= 2:
                try:
                    start_date = datetime.strptime(dates[0], '%B %Y')
                    if 'present' in duration.lower():
                        end_date = datetime.now()
                    else:
                        end_date = datetime.strptime(dates[1], '%B %Y')
                    
                    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    total_months += months
                except:
                    pass
        
        years = total_months / 12
        
        if years < 2:
            return "Entry Level"
        elif years < 5:
            return "Mid Level"
        elif years < 10:
            return "Senior Level"
        else:
            return "Expert/Executive Level"
    
    def parse_advanced(self, file_path: str) -> Dict:
        """Enhanced parsing with NLP features"""
        # Get basic parsing results
        parsed_data = super().parse(file_path)
        
        if 'error' in parsed_data:
            return parsed_data
        
        # Read text for NLP processing
        text = self.read_file(file_path)
        
        # Add advanced features
        parsed_data['advanced'] = {
            'name_nlp': self.extract_name_nlp(text),
            'entities': self.extract_entities(text),
            'key_phrases': self.extract_key_phrases(text),
            'achievements': self.extract_achievements(text),
            'experience_level': self.analyze_experience_level(parsed_data)
        }
        
        return parsed_data