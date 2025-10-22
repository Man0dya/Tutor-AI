"""
Question Setter Agent Module

This module implements the QuestionSetterAgent class, which is responsible for generating
educational questions and assessments using advanced NLP techniques and Bloom's taxonomy.
The agent leverages Google Gemini AI for intelligent question generation and incorporates
content analysis, difficulty tuning, and multiple question types.

Key Features:
- Bloom's taxonomy-based question generation (Remember, Understand, Apply, Analyze, Evaluate, Create)
- Multiple question types: Multiple Choice, True/False, Short Answer, Essay, Fill-in-the-Blank
- Difficulty distribution control (Easy, Medium, Hard)
- Content structure analysis and key concept extraction
- Plausible distractor generation for multiple choice questions
- Fallback question generation for reliability

Dependencies:
- google.genai: For AI-powered question generation
- utils.nlp_processor: For natural language processing tasks
- json, os, re: Standard Python libraries for data handling

Author: Tutor AI Team
"""

import json
import os
from google import genai
from google.genai import types
from utils.nlp_processor import NLPProcessor
import re
from server.config import QS_BATCH_MODE, QS_SUMMARIZE_INPUT, QS_MAX_EXPLANATION_SENTENCES, QS_DEFAULT_MODEL

class QuestionSetterAgent:
    """
    Question Setter Agent for generating educational questions and assessments.

    This agent uses advanced NLP techniques and AI to create pedagogically sound
    questions based on Bloom's taxonomy. It analyzes content structure, extracts
    key concepts, and generates questions with appropriate difficulty levels.

    Attributes:
        client: Google Gemini AI client for question generation
        nlp_processor: NLP processor for content analysis and entity extraction
        agent_id: Unique identifier for this agent ("question_setter")

    Methods:
        generate_questions: Main method for question generation
        validate_questions: Quality validation of generated questions
        _extract_key_concepts: Extract important concepts from content
        _analyze_content_structure: Analyze content for question generation hints
        _generate_bloom_based_questions: Generate questions using Bloom's taxonomy
        _label_question_difficulty: Assign difficulty labels to questions
        _enhance_with_distractors: Create plausible wrong answers for MCQs
    """
    
    def __init__(self):
        """
        Initialize the Question Setter Agent.

        Sets up the Google Gemini AI client for question generation,
        initializes the NLP processor for content analysis, and
        assigns a unique agent identifier.
        """
        # Using Google Gemini 2.5 Flash for free AI question generation
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.nlp_processor = NLPProcessor()
        self.agent_id = "question_setter"
    
    def generate_questions(self, content, question_count=5, question_types=None, difficulty_distribution=None, bloom_levels=None):
        """
        Generate educational questions using natural language prompts for quality and speed.

        Sends raw content to Gemini with clear instructions, parses flexibly,
        and returns high-quality questions without over-engineering.

        Args:
            content (str or dict): Educational content to generate questions from.
            question_count (int, optional): Number of questions to generate. Defaults to 5.
            question_types (list, optional): Types of questions to generate.
            difficulty_distribution (dict, optional): Distribution of Easy/Medium/Hard questions.
            bloom_levels (list, optional): Bloom's taxonomy levels to target.

        Returns:
            dict: Generated questions with metadata.
        """
        # Set default parameters if not provided
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
                key_concepts = []
                learning_objectives = []

            # Generate questions with a single fast LLM call using raw content
            questions = self._generate_questions_fast(
                text_content,
                question_count=question_count,
                question_types=question_types,
                difficulty_distribution=difficulty_distribution,
                bloom_levels=bloom_levels,
            )

            # Return structured response with questions and metadata
            return {
                'questions': questions,
                'metadata': {
                    'total_count': len(questions),
                    'difficulty_distribution': self._calculate_actual_distribution(questions),
                    'question_types': list(set([q.get('type', 'Unknown') for q in questions])),
                    'bloom_levels': list(set([q.get('bloom_level', 'Unknown') for q in questions])),
                }
            }

        except Exception as e:
            raise Exception(f"Question generation failed: {str(e)}")


    def _generate_questions_fast(self, content: str, question_count: int, question_types: list, 
                                 difficulty_distribution: dict, bloom_levels: list):
        """
        Fast question generation using natural prompts and flexible parsing.
        
        Sends raw content to Gemini with clear, natural instructions for better quality.
        No strict JSON enforcement—parses flexibly from natural response.
        """
        # Build natural, clear prompt
        types_str = ", ".join(question_types)
        bloom_str = ", ".join(bloom_levels)
        
        # Calculate target counts per difficulty
        easy_count = int(question_count * difficulty_distribution.get("Easy", 0.3))
        medium_count = int(question_count * difficulty_distribution.get("Medium", 0.5))
        hard_count = question_count - easy_count - medium_count

        prompt = f"""You are an expert educator creating high-quality assessment questions.

Based on the content below, generate exactly {question_count} questions with the following distribution:
- Question Types: {types_str}
- Difficulty: {easy_count} Easy, {medium_count} Medium, {hard_count} Hard
- Cognitive Levels (Bloom's): {bloom_str}

CONTENT:
{content}

INSTRUCTIONS:
1. For Multiple Choice questions:
   - Provide 4 clear, distinct options (A, B, C, D)
   - One option must be unambiguously correct
   - Make wrong options plausible but clearly incorrect to someone who understands
   - No tricks or overly pedantic distinctions

2. For True/False questions:
   - Make clear, testable statements
   - Mix true and false answers

3. For Short Answer questions:
   - Ask for 1-3 sentence responses
   - Test understanding and application, not just recall

4. Label each question with:
   - Type (Multiple Choice, True/False, Short Answer)
   - Difficulty (Easy, Medium, Hard)
   - Bloom Level ({bloom_str})

5. Provide brief explanations (1-2 sentences) for correct answers

Format each question clearly with:
Question: [question text]
Type: [type]
Difficulty: [difficulty]
Bloom Level: [level]
Options: (for MCQ only)
  A) [option]
  B) [option]
  C) [option]
  D) [option]
Correct Answer: [answer]
Explanation: [explanation]

Generate {question_count} diverse, high-quality questions now:"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",  # Fast, reliable model
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2500,
                )
            )

            if response.text:
                # Parse the natural response flexibly
                questions = self._parse_natural_response(response.text)
                return questions[:question_count]  # Ensure exact count
            
            return []

        except Exception as e:
            # Fallback to simple questions if generation fails
            return self._create_simple_fallback_questions(content, question_count)

    def _parse_natural_response(self, text: str) -> list:
        """Parse questions from natural language response flexibly."""
        questions = []
        
        # Split by "Question:" markers
        blocks = text.split("Question:")
        
        for block in blocks[1:]:  # Skip first empty split
            try:
                lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
                
                q_dict = {
                    'question': '',
                    'type': 'Multiple Choice',
                    'difficulty': 'Medium',
                    'bloom_level': 'Understand',
                    'options': [],
                    'correct_answer': '',
                    'explanation': ''
                }
                
                # Extract question text (first line)
                if lines:
                    q_dict['question'] = lines[0].strip()
                
                # Parse remaining lines
                current_section = None
                for line in lines[1:]:
                    line_lower = line.lower()
                    
                    if line_lower.startswith('type:'):
                        q_dict['type'] = line.split(':', 1)[1].strip()
                    elif line_lower.startswith('difficulty:'):
                        q_dict['difficulty'] = line.split(':', 1)[1].strip()
                    elif line_lower.startswith('bloom level:'):
                        q_dict['bloom_level'] = line.split(':', 1)[1].strip()
                    elif line_lower.startswith('options:'):
                        current_section = 'options'
                    elif line_lower.startswith('correct answer:'):
                        q_dict['correct_answer'] = line.split(':', 1)[1].strip()
                        current_section = None
                    elif line_lower.startswith('explanation:'):
                        q_dict['explanation'] = line.split(':', 1)[1].strip()
                        current_section = 'explanation'
                    elif current_section == 'options' and line:
                        # Parse option (A), B), etc.
                        if line[0] in 'ABCDabcd' and len(line) > 2:
                            option_text = line[2:].strip()
                            if option_text:
                                q_dict['options'].append(option_text)
                    elif current_section == 'explanation':
                        # Multi-line explanation
                        q_dict['explanation'] += ' ' + line
                
                # Clean up and validate
                q_dict['explanation'] = q_dict['explanation'].strip()
                
                # For MCQ, ensure we have options
                if q_dict['type'] == 'Multiple Choice' and len(q_dict['options']) < 2:
                    continue
                
                # Map correct answer for MCQ (if letter format like "A" or "B)")
                if q_dict['type'] == 'Multiple Choice' and q_dict['options']:
                    ans = q_dict['correct_answer'].strip().upper()
                    if ans in 'ABCD' and len(ans) == 1:
                        idx = ord(ans) - ord('A')
                        if 0 <= idx < len(q_dict['options']):
                            q_dict['correct_answer'] = q_dict['options'][idx]
                
                # Add valid question
                if q_dict['question'] and q_dict['correct_answer']:
                    questions.append(q_dict)
                    
            except Exception:
                continue
        
        return questions

    def _create_simple_fallback_questions(self, content: str, count: int) -> list:
        """Create simple fallback questions if parsing fails."""
        questions = []
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 30]
        
        for i in range(min(count, len(sentences), 5)):
            questions.append({
                'question': f"What is the main idea conveyed in: '{sentences[i][:80]}...'?",
                'type': 'Short Answer',
                'difficulty': 'Medium',
                'bloom_level': 'Understand',
                'correct_answer': sentences[i],
                'explanation': 'Based on the content provided.'
            })
        
        return questions

    
    def _extract_key_concepts(self, content):
        
        """
        Extract key concepts from content using NLP techniques.

        Uses entity extraction and keyword analysis to identify important
        terms and concepts that should be tested in questions.

        Args:
            content (str): The educational content to analyze.

        Returns:
            list: List of unique key concepts and important terms (max 20).
        """
        
        try:
            # Extract named entities using NLP processor
            entities = self.nlp_processor.extract_entities(content)

            # Extract key phrases from important sentences
            sentences = content.split('.')
            key_phrases = []

            for sentence in sentences[:10]:  # Analyze first 10 sentences
                if len(sentence.strip()) > 20:  # Skip very short sentences
                    # Simple keyword extraction based on capitalization and length
                    words = sentence.split()
                    important_words = [w for w in words if len(w) > 4 and (w[0].isupper() or w.lower() in ['important', 'key', 'main'])]
                    key_phrases.extend(important_words[:3])

            # Combine entities and key phrases, remove duplicates
            concepts = [ent['text'] for ent in entities] + key_phrases
            return list(set(concepts))[:20]  # Return unique concepts, max 20

        except Exception:
            # Fallback to simple word extraction if NLP fails
            words = content.split()
            return [w for w in words if len(w) > 6][:10]
    
    def _analyze_content_structure(self, content):
        
        """
        Analyze the structure and characteristics of the content.

        Examines the content for pedagogical features that can guide
        question generation, such as examples, definitions, processes, etc.

        Args:
            content (str): The content to analyze.

        Returns:
            dict: Analysis results containing:
                - has_examples: Whether content contains examples
                - has_definitions: Whether content has definitions
                - has_processes: Whether content describes processes
                - has_comparisons: Whether content makes comparisons
                - length: Word count of the content
                - complexity: Ratio of complex words (length > 8)
        """
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
        
        """
        Generate questions of a specific type using AI.

        Routes to the appropriate generation method based on question type.

        Args:
            content (str): The content to generate questions from.
            question_type (str): Type of questions to generate.
            count (int): Number of questions to generate.
            key_concepts (list): Key concepts to focus on.

        Returns:
            list: List of generated questions of the specified type.
        """
        
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
        
        """
        Generate multiple choice questions using AI.

        Creates MCQs with 4 options each, ensuring one correct answer
        and plausible distractors.

        Args:
            content (str): Content to generate questions from.
            count (int): Number of MCQs to generate.
            key_concepts (list): Key concepts to focus on.

        Returns:
            list: List of MCQ dictionaries with question, options, correct_answer, etc.
        """
        
        system_prompt = """You are an expert question generator. Create multiple choice questions that test understanding of the given content.
        Strict requirements:
        - Provide exactly 4 options as plain, self-contained answer strings (no letter prefixes like A., B., no numbering like 1., 2.).
        - Do not output options that reference other options (e.g., "B", "Option B"). Each option must stand alone.
        - The `correct_answer` must be exactly one of the strings from the `options` array, not a letter or index.
        - Ensure plausible distractors and one unambiguous correct answer.

        Return the response in JSON format with this structure:
        {
            "questions": [
                {
                    "question": "Question text here?",
                    "options": ["Answer text 1", "Answer text 2", "Answer text 3", "Answer text 4"],
                    "correct_answer": "Answer text 2",
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
                # Extract JSON from response (handle markdown formatting)
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3].strip()
                elif text.startswith('```'):
                    text = text[3:-3].strip()

                result = json.loads(text)
                qs = result.get("questions", [])
                # Normalize immediately to guard against misformatted options/correct_answer
                return self._normalize_all_questions(qs, key_concepts)
            return []

        except Exception as e:
            # Fallback to simple question generation if AI fails
            return self._create_fallback_questions(content, count, "Multiple Choice")
    
    def _generate_true_false(self, content, count):
        """
        Generate true/false questions using AI.

        Creates statements that are either true or false based on the content,
        testing factual knowledge and understanding.

        Args:
            content (str): Content to generate questions from.
            count (int): Number of true/false questions to generate.

        Returns:
            list: List of true/false question dictionaries.
        """
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
        """
        Generate short answer questions using AI.

        Creates questions requiring 1-3 sentence responses that test
        understanding and application of concepts.

        Args:
            content (str): Content to generate questions from.
            count (int): Number of short answer questions to generate.
            key_concepts (list): Key concepts to focus on.

        Returns:
            list: List of short answer question dictionaries.
        """
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
        """
        Generate essay questions using AI.

        Creates questions requiring detailed, analytical responses that
        test critical thinking and synthesis of information.

        Args:
            content (str): Content to generate questions from.
            count (int): Number of essay questions to generate.

        Returns:
            list: List of essay question dictionaries.
        """
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
        """
        Generate questions based on Bloom's taxonomy levels.

        Distributes questions across different Bloom's levels and generates
        questions targeting specific cognitive levels (Remember, Understand, Apply, etc.).

        Args:
            content (str): The educational content.
            key_concepts (list): Key concepts extracted from content.
            learning_objectives (list): Learning objectives (if provided).
            question_count (int): Total number of questions to generate.
            question_types (list): Types of questions to generate.
            difficulty_distribution (dict): Difficulty distribution preferences.
            bloom_levels (list): Bloom's taxonomy levels to target.

        Returns:
            list: List of questions with Bloom's level metadata.
        """
        questions = []

        # Calculate how many questions per Bloom level
        bloom_distribution = self._calculate_bloom_distribution(bloom_levels, question_count)

        for bloom_level, count in bloom_distribution.items():
            if count > 0:
                bloom_questions = self._generate_questions_for_bloom_level(
                    content, key_concepts, bloom_level, count, question_types
                )
                questions.extend(bloom_questions)

        return questions
    
    def _calculate_bloom_distribution(self, bloom_levels, total_count):
        """
        Calculate how many questions to generate for each Bloom level.

        Distributes the total question count evenly across the specified
        Bloom's taxonomy levels, handling remainders appropriately.

        Args:
            bloom_levels (list): List of Bloom's levels to target.
            total_count (int): Total number of questions to generate.

        Returns:
            dict: Mapping of Bloom level to number of questions for that level.
        """
        distribution = {}
        questions_per_level = total_count // len(bloom_levels)
        remainder = total_count % len(bloom_levels)

        for i, level in enumerate(bloom_levels):
            distribution[level] = questions_per_level
            if i < remainder:  # Distribute remainder
                distribution[level] += 1

        return distribution
    
    def _generate_questions_for_bloom_level(self, content, key_concepts, bloom_level, count, question_types):
        """
        Generate questions targeting a specific Bloom's taxonomy level.

        Uses AI to create questions that specifically test the cognitive
        processes associated with the given Bloom's level.

        Args:
            content (str): The educational content.
            key_concepts (list): Key concepts to focus on.
            bloom_level (str): The Bloom's level to target (Remember, Understand, etc.).
            count (int): Number of questions to generate for this level.
            question_types (list): Types of questions to generate.

        Returns:
            list: List of questions targeting the specified Bloom's level.
        """
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
        """
        Assign difficulty labels to questions based on the requested distribution.

        Distributes Easy, Medium, and Hard labels across the questions
        according to the specified percentages.

        Args:
            questions (list): List of question dictionaries to label.
            difficulty_distribution (dict): Target distribution with keys "Easy", "Medium", "Hard"
                and float values representing proportions.

        Returns:
            list: Questions with 'difficulty' field added to each question.
        """
        total_questions = len(questions)
        easy_count = int(total_questions * difficulty_distribution.get("Easy", 0.3))
        medium_count = int(total_questions * difficulty_distribution.get("Medium", 0.5))
        hard_count = total_questions - easy_count - medium_count

        # Assign difficulty labels sequentially
        for i, question in enumerate(questions):
            if i < easy_count:
                question['difficulty'] = 'Easy'
            elif i < easy_count + medium_count:
                question['difficulty'] = 'Medium'
            else:
                question['difficulty'] = 'Hard'

        return questions
    
    def _enhance_with_distractors(self, questions, key_concepts):
        """
        Create plausible distractors for multiple choice questions.

        For MCQs, generates better wrong answer options using AI to make
        them challenging but clearly incorrect to knowledgeable students.

        Args:
            questions (list): List of question dictionaries.
            key_concepts (list): Key concepts to guide distractor generation.

        Returns:
            list: Questions with enhanced distractors for MCQs.
        """
        enhanced_questions = []

        for question in questions:
            if question.get('type') == 'Multiple Choice' and 'options' in question:
                # Generate better distractors using NLP and AI
                enhanced_options = self._generate_plausible_distractors(
                    question, key_concepts
                )
                question['options'] = enhanced_options

            enhanced_questions.append(question)

        return enhanced_questions
    
    def _generate_plausible_distractors(self, question, key_concepts):
        """
        Generate plausible but incorrect options for multiple choice questions.

        Uses AI to create distractors that are tempting but wrong, making
        questions more pedagogically effective.

        Args:
            question (dict): The MCQ question dictionary.
            key_concepts (list): Key concepts to guide distractor creation.

        Returns:
            list: List of 4 options including the correct answer and 3 distractors.
        """
        # Initialize safe defaults outside try to avoid UnboundLocalError in except
        existing_options = []
        correct_answer = ''

        try:
            # Question should be a dict; if not, bail out to fallback
            if not isinstance(question, dict):
                raise ValueError("question must be a dict with keys 'question', 'options', 'correct_answer'")

            existing_options = question.get('options', []) if isinstance(question.get('options'), list) else []
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
                raw_lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
                # Strip leading labels like "A.", "1)", "B :" and filter out letter-only tokens
                def strip_label(s: str) -> str:
                    t = s.strip()
                    t = re.sub(r'^[A-Da-d][).:-]?\s+', '', t)
                    t = re.sub(r'^\d+[).:-]?\s+', '', t)
                    return t.strip()
                cleaned = [strip_label(x) for x in raw_lines]
                # Filter out bad/too-short items and references
                def bad_opt(x: str) -> bool:
                    if not isinstance(x, str):
                        return True
                    xx = x.strip()
                    if len(xx) < 6:
                        return True
                    if re.fullmatch(r'[A-Da-d]', xx):
                        return True
                    if re.fullmatch(r'Option\s+[A-Da-d]', xx, flags=re.IGNORECASE):
                        return True
                    return False
                distractors = [x for x in cleaned if not bad_opt(x)]
                distractors = distractors[:3]  # Take only 3

                # Combine sanitized correct answer (if valid) with distractors and randomize
                def is_letter_answer(s: str) -> bool:
                    return isinstance(s, str) and re.fullmatch(r'[A-Da-d]', s.strip()) is not None
                base = []
                if isinstance(correct_answer, str):
                    ca_str = correct_answer.strip()
                    if ca_str and not is_letter_answer(ca_str) and len(ca_str) >= 4:
                        base.append(ca_str)
                all_options = base + distractors
                import random
                random.shuffle(all_options)  # Randomize order

                return all_options[:4]  # Ensure exactly 4 options

            # Fallback minimal set (avoid injecting letter-only correct answers)
            return existing_options if existing_options else [
                "Plausible but incorrect detail",
                "Common misconception",
                "Related but wrong concept",
                "Confusing alternative"
            ]

        except Exception:
            # Robust fallback if anything goes wrong (avoid letter-only answers)
            return existing_options if existing_options else [
                "Plausible but incorrect detail",
                "Common misconception",
                "Related but wrong concept",
                "Confusing alternative"
            ]
    
    def _calculate_actual_distribution(self, questions):
        """
        Calculate the actual difficulty distribution of generated questions.

        Analyzes the generated questions and returns the percentage breakdown
        of Easy, Medium, and Hard questions.

        Args:
            questions (list): List of question dictionaries with difficulty labels.

        Returns:
            dict: Dictionary with "Easy", "Medium", "Hard" keys and percentage values.
        """
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
        """
        Create simple fallback questions for a specific Bloom level.

        Generates basic questions when AI generation fails, ensuring
        the system remains functional even with API issues.

        Args:
            content (str): The educational content.
            count (int): Number of questions to generate.
            bloom_level (str): The Bloom's level to target.

        Returns:
            list: List of simple fallback questions.
        """
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
        """
        Generate fill-in-the-blank questions.

        Creates questions where students must fill in missing key concepts
        from the content, testing recognition and recall.

        Args:
            content (str): Content to generate questions from.
            count (int): Number of fill-in-the-blank questions to generate.
            key_concepts (list): Key concepts to potentially blank out.

        Returns:
            list: List of fill-in-the-blank question dictionaries.
        """
        
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
        """
        Create simple fallback questions if AI generation fails.

        Provides basic question generation as a safety net when
        the AI service is unavailable or returns errors.

        Args:
            content (str): Content to generate questions from.
            count (int): Number of questions to generate.
            question_type (str): Type of questions to create.

        Returns:
            list: List of simple fallback questions.
        """
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
        """
        Validate generated questions for quality and completeness.

        Filters out questions that don't meet minimum quality criteria
        such as having valid questions, options, and answers.

        Args:
            questions (list): List of question dictionaries to validate.

        Returns:
            list: List of validated questions that pass quality checks.
        """
        validated_questions = []

        for question in questions:
            if self._is_valid_question(question):
                validated_questions.append(question)

        return validated_questions

    def _is_valid_question(self, question):
        """
        Check if a question meets quality criteria.

        Validates that the question has required fields and meets
        minimum length and completeness requirements.

        Args:
            question (dict): Question dictionary to validate.

        Returns:
            bool: True if question passes validation, False otherwise.
        """
        if not question.get('question') or len(question['question']) < 10:
            return False

        if question.get('type') == 'Multiple Choice':
            if not question.get('options') or len(question['options']) < 2:
                return False
            if not question.get('correct_answer'):
                return False

        return True

    # --- Normalization helpers to improve MCQ quality and structure ---
    def _normalize_all_questions(self, questions, key_concepts):
        normalized = []
        for q in questions or []:
            if q.get('type') == 'Multiple Choice':
                normalized.append(self._normalize_mcq(q, key_concepts))
            else:
                normalized.append(q)
        return normalized

    def _normalize_mcq(self, q, key_concepts):
        # Ensure options is a list of strings
        opts = q.get('options') or []
        if not isinstance(opts, list):
            opts = []
        # Flatten any nested or labeled options and strip labels like "A.", "B)", "C :"
        def strip_label(s: str) -> str:
            if not isinstance(s, str):
                return ''
            t = s.strip()
            # Remove leading label patterns
            t = re.sub(r'^[A-Da-d][).:-]?\s+', '', t)
            t = re.sub(r'^\d+[).:-]?\s+', '', t)
            return t.strip()

        clean_opts = [strip_label(o) for o in opts if isinstance(o, str) and o.strip()]
        # Filter out letter-only or referenced options like "B" or "Option C"
        def bad_opt(x: str) -> bool:
            if not isinstance(x, str):
                return True
            xx = x.strip()
            if len(xx) < 4:
                return True
            if re.fullmatch(r'[A-Da-d]', xx):
                return True
            if re.fullmatch(r'Option\s+[A-Da-d]', xx, flags=re.IGNORECASE):
                return True
            return False
        clean_opts = [o for o in clean_opts if not bad_opt(o)]
        # Deduplicate while preserving order
        seen = set()
        dedup_opts = []
        for o in clean_opts:
            if o not in seen:
                seen.add(o)
                dedup_opts.append(o)

        # Ensure exactly 4 options: truncate or pad with plausible distractors
        if len(dedup_opts) > 4:
            dedup_opts = dedup_opts[:4]
        while len(dedup_opts) < 4:
            # Generate a simple distractor placeholder if lacking; avoid empty strings
            # Pass the full question dict (not just the text) so the generator can use correct_answer/options
            filler = self._generate_plausible_distractors(q, key_concepts) or []
            for f in filler:
                ft = strip_label(f)
                if ft and ft not in seen:
                    dedup_opts.append(ft)
                    seen.add(ft)
                    if len(dedup_opts) == 4:
                        break
            if len(dedup_opts) < 4:
                # Last resort filler
                candidate = f"None of the above ({len(dedup_opts)+1})"
                if candidate not in seen:
                    dedup_opts.append(candidate)
                    seen.add(candidate)

        # Normalize correct_answer: if it's a letter, map to option; else match by text
        ca = q.get('correct_answer')
        ca_text = ''
        if isinstance(ca, str):
            ca_stripped = strip_label(ca)
            # If answer is a single letter A-D, map index
            m = re.fullmatch(r'[A-Da-d]', ca_stripped)
            if m:
                idx = ord(ca_stripped.upper()) - ord('A')
                if 0 <= idx < len(dedup_opts):
                    ca_text = dedup_opts[idx]
            else:
                # Try exact text match; fall back to first option
                if ca_stripped in dedup_opts:
                    ca_text = ca_stripped
                else:
                    # loose match ignoring case
                    for o in dedup_opts:
                        if o.lower() == ca_stripped.lower():
                            ca_text = o
                            break
        if not ca_text and dedup_opts:
            # Prefer a concept-aligned option if possible
            ca_text = dedup_opts[0]

        q['options'] = dedup_opts
        q['correct_answer'] = ca_text
        q['type'] = 'Multiple Choice'
        return q
