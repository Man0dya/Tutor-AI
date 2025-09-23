import json
import os
from google import genai
from google.genai import types
from utils.nlp_processor import NLPProcessor
import re

class QuestionSetterAgent:
    """
    Question Setter Agent for generating questions and assessments
    Uses NLP techniques for content analysis and question generation
    """
    
    def __init__(self):
        # Using Google Gemini 2.5 Flash for free AI question generation
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.nlp_processor = NLPProcessor()
        self.agent_id = "question_setter"
    
    def generate_questions(self, content, question_count=5, question_types=None, difficulty_distribution=None, bloom_levels=None):
        """
        Generate questions using Bloom's taxonomy and advanced NLP
        
        Args:
            content (str or dict): Educational content to generate questions from
            question_count (int): Number of questions to generate
            question_types (list): Types of questions to generate
            difficulty_distribution (dict): Distribution of Easy/Medium/Hard questions
            bloom_levels (list): Bloom's taxonomy levels to target
            
        Returns:
            dict: Generated questions with metadata and difficulty labels
        """
        if question_types is None:
            question_types = ["Multiple Choice", "Short Answer", "True/False"]
        
        if difficulty_distribution is None:
            difficulty_distribution = {"Easy": 0.3, "Medium": 0.5, "Hard": 0.2}
        
        if bloom_levels is None:
            bloom_levels = ["Remember", "Understand", "Apply", "Analyze"]
        
        try:
            # Extract content if it's a structured object
            if isinstance(content, dict):
                text_content = content.get('content', str(content))
                key_concepts = content.get('key_concepts', [])
                learning_objectives = content.get('learning_objectives', [])
            else:
                text_content = content
                key_concepts = self._extract_key_concepts(content)
                learning_objectives = []
            
            # Analyze content structure
            content_analysis = self._analyze_content_structure(text_content)
            
            # Generate questions using Bloom's taxonomy
            questions = self._generate_bloom_based_questions(
                text_content, key_concepts, learning_objectives, 
                question_count, question_types, difficulty_distribution, bloom_levels
            )
            
            # Add difficulty labels and metadata
            labeled_questions = self._label_question_difficulty(questions, difficulty_distribution)
            
            # Create plausible distractors for MCQ
            enhanced_questions = self._enhance_with_distractors(labeled_questions, key_concepts)
            
            return {
                'questions': enhanced_questions,
                'metadata': {
                    'total_count': len(enhanced_questions),
                    'difficulty_distribution': self._calculate_actual_distribution(enhanced_questions),
                    'question_types': list(set([q['type'] for q in enhanced_questions])),
                    'bloom_levels': list(set([q.get('bloom_level', 'Unknown') for q in enhanced_questions])),
                    'key_concepts_covered': key_concepts[:10]
                }
            }
            
        except Exception as e:
            raise Exception(f"Question generation failed: {str(e)}")
    
    def _extract_key_concepts(self, content):
        """Extract key concepts from content using NLP"""
        try:
            # Extract entities and important terms
            entities = self.nlp_processor.extract_entities(content)
            
            # Extract key phrases (simplified approach)
            sentences = content.split('.')
            key_phrases = []
            
            for sentence in sentences[:10]:  # Analyze first 10 sentences
                if len(sentence.strip()) > 20:  # Skip very short sentences
                    # Simple keyword extraction based on capitalization and length
                    words = sentence.split()
                    important_words = [w for w in words if len(w) > 4 and (w[0].isupper() or w.lower() in ['important', 'key', 'main'])]
                    key_phrases.extend(important_words[:3])
            
            # Combine entities and key phrases
            concepts = [ent['text'] for ent in entities] + key_phrases
            return list(set(concepts))[:20]  # Return unique concepts, max 20
            
        except Exception:
            # Fallback to simple word extraction
            words = content.split()
            return [w for w in words if len(w) > 6][:10]
    
    def _analyze_content_structure(self, content):
        """Analyze the structure of the content"""
        structure = {
            'has_examples': 'example' in content.lower() or 'for instance' in content.lower(),
            'has_definitions': ':' in content or 'is defined as' in content.lower(),
            'has_processes': 'step' in content.lower() or 'process' in content.lower(),
            'has_comparisons': 'compare' in content.lower() or 'versus' in content.lower(),
            'length': len(content.split()),
            'complexity': len([w for w in content.split() if len(w) > 8]) / len(content.split()) if content.split() else 0
        }
        return structure
    
    def _generate_questions_by_type(self, content, question_type, count, key_concepts):
        """Generate questions of a specific type"""
        
        if question_type == "Multiple Choice":
            return self._generate_mcq(content, count, key_concepts)
        elif question_type == "True/False":
            return self._generate_true_false(content, count)
        elif question_type == "Short Answer":
            return self._generate_short_answer(content, count, key_concepts)
        elif question_type == "Essay":
            return self._generate_essay(content, count)
        elif question_type == "Fill in the Blank":
            return self._generate_fill_blank(content, count, key_concepts)
        else:
            return self._generate_short_answer(content, count, key_concepts)
    
    def _generate_mcq(self, content, count, key_concepts):
        """Generate multiple choice questions"""
        
        system_prompt = """You are an expert question generator. Create multiple choice questions that test understanding of the given content. 
        Each question should have exactly 4 options (A, B, C, D) with only one correct answer.
        
        Return the response in JSON format with this structure:
        {
            "questions": [
                {
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option B",
                    "explanation": "Why this answer is correct",
                    "type": "Multiple Choice"
                }
            ]
        }"""
        
        user_prompt = f"""Based on this content, generate {count} multiple choice questions that test comprehension and application:

{content}

Key concepts to focus on: {', '.join(key_concepts[:10])}

Make questions challenging but fair, testing different levels of understanding."""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            
            if response.text:
                # Extract JSON from response
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3].strip()
                elif text.startswith('```'):
                    text = text[3:-3].strip()
                
                result = json.loads(text)
                return result.get("questions", [])
            return []
            
        except Exception as e:
            # Fallback: create simple questions
            return self._create_fallback_questions(content, count, "Multiple Choice")
    
    def _generate_true_false(self, content, count):
        """Generate true/false questions"""
        
        system_prompt = """Create true/false questions based on the content. Mix true and false statements.
        
        Return in JSON format:
        {
            "questions": [
                {
                    "question": "Statement to evaluate",
                    "correct_answer": "True" or "False",
                    "explanation": "Explanation of why this is true/false",
                    "type": "True/False"
                }
            ]
        }"""
        
        user_prompt = f"""Create {count} true/false questions from this content:

{content}

Make some statements true and others false. Test important facts and concepts."""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            
            if response.text:
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3].strip()
                elif text.startswith('```'):
                    text = text[3:-3].strip()
                
                result = json.loads(text)
                return result.get("questions", [])
            return []
            
        except Exception:
            return self._create_fallback_questions(content, count, "True/False")
    
    def _generate_short_answer(self, content, count, key_concepts):
        """Generate short answer questions"""
        
        system_prompt = """Create short answer questions that require 1-3 sentence responses.
        
        Return in JSON format:
        {
            "questions": [
                {
                    "question": "Question requiring short answer?",
                    "sample_answer": "Example of a good answer",
                    "key_points": ["Point 1", "Point 2"],
                    "type": "Short Answer"
                }
            ]
        }"""
        
        user_prompt = f"""Create {count} short answer questions from this content:

{content}

Focus on these key concepts: {', '.join(key_concepts[:8])}

Questions should test understanding and application, not just memorization."""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            
            if response.text:
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3].strip()
                elif text.startswith('```'):
                    text = text[3:-3].strip()
                
                result = json.loads(text)
                return result.get("questions", [])
            return []
            
        except Exception:
            return self._create_fallback_questions(content, count, "Short Answer")
    
    def _generate_essay(self, content, count):
        """Generate essay questions"""
        
        system_prompt = """Create essay questions that require detailed, analytical responses.
        
        Return in JSON format:
        {
            "questions": [
                {
                    "question": "Essay question that requires analysis?",
                    "guidance": "What should be included in a good answer",
                    "rubric_points": ["Point 1", "Point 2", "Point 3"],
                    "type": "Essay"
                }
            ]
        }"""
        
        user_prompt = f"""Create {count} essay questions from this content:

{content}

Questions should require critical thinking, analysis, and synthesis of information."""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            
            if response.text:
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3].strip()
                elif text.startswith('```'):
                    text = text[3:-3].strip()
                
                result = json.loads(text)
                return result.get("questions", [])
            return []
            
        except Exception:
            return self._create_fallback_questions(content, count, "Essay")
    
    def _generate_bloom_based_questions(self, content, key_concepts, learning_objectives, 
                                      question_count, question_types, difficulty_distribution, bloom_levels):
        """Generate questions based on Bloom's taxonomy levels"""
        questions = []
        
        # Calculate questions per Bloom level
        bloom_distribution = self._calculate_bloom_distribution(bloom_levels, question_count)
        
        for bloom_level, count in bloom_distribution.items():
            if count > 0:
                bloom_questions = self._generate_questions_for_bloom_level(
                    content, key_concepts, bloom_level, count, question_types
                )
                questions.extend(bloom_questions)
        
        return questions
    
    def _calculate_bloom_distribution(self, bloom_levels, total_count):
        """Calculate how many questions for each Bloom level"""
        distribution = {}
        questions_per_level = total_count // len(bloom_levels)
        remainder = total_count % len(bloom_levels)
        
        for i, level in enumerate(bloom_levels):
            distribution[level] = questions_per_level
            if i < remainder:  # Distribute remainder
                distribution[level] += 1
        
        return distribution
    
    def _generate_questions_for_bloom_level(self, content, key_concepts, bloom_level, count, question_types):
        """Generate questions targeting specific Bloom's taxonomy level"""
        bloom_prompts = {
            "Remember": "Create questions that test recall of facts, terms, and basic concepts.",
            "Understand": "Create questions that test comprehension and explanation of ideas.",
            "Apply": "Create questions that test application of knowledge in new situations.",
            "Analyze": "Create questions that test ability to break down information and identify relationships.",
            "Evaluate": "Create questions that test ability to make judgments and justify decisions.",
            "Create": "Create questions that test ability to synthesize information into new forms."
        }
        
        system_prompt = f"""You are an expert question generator using Bloom's Taxonomy.
        
        Target Level: {bloom_level}
        Focus: {bloom_prompts.get(bloom_level, "General understanding")}
        
        Return in JSON format:
        {{
            "questions": [
                {{
                    "question": "Question text?",
                    "type": "Multiple Choice" or "Short Answer" or "True/False",
                    "options": ["A", "B", "C", "D"] (if MCQ),
                    "correct_answer": "Correct option or answer",
                    "explanation": "Why this is correct",
                    "bloom_level": "{bloom_level}",
                    "difficulty": "Easy" or "Medium" or "Hard",
                    "key_concepts": ["concept1", "concept2"]
                }}
            ]
        }}"""
        
        user_prompt = f"""Create {count} questions at {bloom_level} level from this content:
        
        {content}
        
        Key concepts to focus on: {', '.join(key_concepts[:10])}
        
        Question types to use: {', '.join(question_types)}
        
        {bloom_level} level means: {bloom_prompts.get(bloom_level, "")}
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            
            if response.text:
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3].strip()
                elif text.startswith('```'):
                    text = text[3:-3].strip()
                
                result = json.loads(text)
                return result.get("questions", [])
            return []
            
        except Exception:
            return self._create_fallback_questions_for_bloom(content, count, bloom_level)
    
    def _label_question_difficulty(self, questions, difficulty_distribution):
        """Label questions with difficulty based on distribution"""
        total_questions = len(questions)
        easy_count = int(total_questions * difficulty_distribution.get("Easy", 0.3))
        medium_count = int(total_questions * difficulty_distribution.get("Medium", 0.5))
        hard_count = total_questions - easy_count - medium_count
        
        # Assign difficulty labels
        for i, question in enumerate(questions):
            if i < easy_count:
                question['difficulty'] = 'Easy'
            elif i < easy_count + medium_count:
                question['difficulty'] = 'Medium'
            else:
                question['difficulty'] = 'Hard'
        
        return questions
    
    def _enhance_with_distractors(self, questions, key_concepts):
        """Create plausible distractors for multiple choice questions"""
        enhanced_questions = []
        
        for question in questions:
            if question.get('type') == 'Multiple Choice' and 'options' in question:
                # Generate better distractors using NLP
                enhanced_options = self._generate_plausible_distractors(
                    question, key_concepts
                )
                question['options'] = enhanced_options
            
            enhanced_questions.append(question)
        
        return enhanced_questions
    
    def _generate_plausible_distractors(self, question, key_concepts):
        """Generate plausible but incorrect options for MCQ"""
        try:
            existing_options = question.get('options', [])
            correct_answer = question.get('correct_answer', '')
            
            # Use AI to generate better distractors
            distractor_prompt = f"""Create 3 plausible but incorrect options for this multiple choice question:
            
            Question: {question['question']}
            Correct Answer: {correct_answer}
            
            Key concepts: {', '.join(key_concepts[:5])}
            
            Make distractors that:
            - Are plausible but clearly wrong to someone who understands the concept
            - Use similar terminology but incorrect relationships
            - Avoid obvious wrong answers
            
            Return just the 3 distractor options, one per line."""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=distractor_prompt
            )
            
            if response.text:
                distractors = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
                distractors = distractors[:3]  # Take only 3
                
                # Combine correct answer with distractors
                all_options = [correct_answer] + distractors
                import random
                random.shuffle(all_options)  # Randomize order
                
                return all_options[:4]  # Ensure exactly 4 options
            
            return existing_options if existing_options else [correct_answer, "Option B", "Option C", "Option D"]
            
        except Exception:
            return existing_options if existing_options else [correct_answer, "Option B", "Option C", "Option D"]
    
    def _calculate_actual_distribution(self, questions):
        """Calculate actual difficulty distribution of generated questions"""
        distribution = {"Easy": 0, "Medium": 0, "Hard": 0}
        total = len(questions)
        
        for question in questions:
            difficulty = question.get('difficulty', 'Medium')
            if difficulty in distribution:
                distribution[difficulty] += 1
        
        # Convert to percentages
        if total > 0:
            for key in distribution:
                distribution[key] = round(distribution[key] / total, 2)
        
        return distribution
    
    def _create_fallback_questions_for_bloom(self, content, count, bloom_level):
        """Create simple fallback questions for specific Bloom level"""
        questions = []
        
        # Extract some content for basic questions
        lines = [line.strip() for line in content.split('\n') if line.strip() and len(line) > 20]
        
        for i in range(min(count, len(lines), 3)):
            line = lines[i]
            if '.' in line:
                question = {
                    'question': f"What is the main point about: {line[:50]}...?",
                    'type': 'Short Answer',
                    'sample_answer': line,
                    'bloom_level': bloom_level,
                    'difficulty': 'Easy',
                    'key_concepts': []
                }
                questions.append(question)
        
        return questions
    
    def _generate_fill_blank(self, content, count, key_concepts):
        """Generate fill-in-the-blank questions"""
        
        # Extract sentences with key concepts
        sentences = content.split('.')
        suitable_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and any(concept.lower() in sentence.lower() for concept in key_concepts):
                suitable_sentences.append(sentence)
        
        questions = []
        for i, sentence in enumerate(suitable_sentences[:count]):
            # Find key concept to blank out
            concept_to_blank = None
            for concept in key_concepts:
                if concept.lower() in sentence.lower():
                    concept_to_blank = concept
                    break
            
            if concept_to_blank:
                blank_sentence = sentence.replace(concept_to_blank, "________")
                questions.append({
                    "question": f"Fill in the blank: {blank_sentence}",
                    "correct_answer": concept_to_blank,
                    "type": "Fill in the Blank"
                })
        
        return questions
    
    def _create_fallback_questions(self, content, count, question_type):
        """Create simple fallback questions if AI generation fails"""
        questions = []
        sentences = content.split('.')[:count * 2]  # Get enough sentences
        
        for i in range(min(count, len(sentences))):
            sentence = sentences[i].strip()
            if len(sentence) > 20:
                if question_type == "Multiple Choice":
                    questions.append({
                        "question": f"Based on the content, which statement is most accurate about: {sentence[:50]}...?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "type": "Multiple Choice"
                    })
                elif question_type == "True/False":
                    questions.append({
                        "question": sentence,
                        "correct_answer": "True",
                        "type": "True/False"
                    })
                else:  # Short Answer
                    questions.append({
                        "question": f"Explain the concept mentioned in: {sentence[:50]}...?",
                        "type": "Short Answer"
                    })
        
        return questions
    
    def validate_questions(self, questions):
        """Validate generated questions for quality and completeness"""
        validated_questions = []
        
        for question in questions:
            if self._is_valid_question(question):
                validated_questions.append(question)
        
        return validated_questions
    
    def _is_valid_question(self, question):
        """Check if a question meets quality criteria"""
        if not question.get('question') or len(question['question']) < 10:
            return False
        
        if question.get('type') == 'Multiple Choice':
            if not question.get('options') or len(question['options']) < 2:
                return False
            if not question.get('correct_answer'):
                return False
        
        return True
