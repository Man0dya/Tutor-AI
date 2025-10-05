"""
Natural Language Processing Utilities for Tutor AI

This module provides NLP functions for text analysis, similarity computation,
content moderation, and educational content processing. Uses NLTK for basic
text processing and scikit-learn for embeddings and similarity.
"""

import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from collections import Counter
import os
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data (only once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('chunkers/maxent_ne_chunker')
except LookupError:
    nltk.download('maxent_ne_chunker')

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

class NLPProcessor:
    """
    Natural Language Processing utilities for the tutoring system.
    
    Handles text analysis, entity extraction, summarization, similarity computation,
    content moderation, and educational content processing.
    """
    
    def __init__(self):
        # Initialize NLP tools
        self.stop_words = set(stopwords.words('english'))  # Common words to ignore
        self.lemmatizer = WordNetLemmatizer()  # Reduce words to base form
        
        # Educational keywords that are important to preserve in analysis
        self.educational_keywords = {
            'definition', 'concept', 'theory', 'principle', 'method', 'process',
            'example', 'application', 'analysis', 'synthesis', 'evaluation',
            'compare', 'contrast', 'explain', 'describe', 'identify', 'calculate',
            'solve', 'prove', 'demonstrate', 'illustrate', 'implement'
        }
        
        # Banned keywords and phrases for content moderation
        self.banned_terms = {
            # Violence and harm
            'bomb', 'explosive', 'gun', 'weapon', 'kill', 'murder', 'suicide', 'harm',
            'attack', 'terrorism', 'violent', 'assault', 'abuse',
            # Illegal activities
            'drug', 'narcotic', 'illegal', 'crime', 'hack', 'steal', 'fraud', 'scam',
            'pirate', 'counterfeit', 'smuggle',
            # Hate and discrimination
            'hate', 'racist', 'sexist', 'discrimination', 'slur', 'offensive',
            # Adult content
            'porn', 'sex', 'nude', 'adult', 'explicit',
            # Other harmful
            'virus', 'malware', 'trojan', 'exploit', 'phishing'
        }
        
        # Initialize TF-IDF vectorizer for embeddings (used in similarity search)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def extract_entities(self, text):
        """
        Extract named entities from text using NLTK
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            list: List of entities with their types and positions
        """
        try:
            # Tokenize and tag parts of speech
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # Extract named entities
            tree = ne_chunk(pos_tags, binary=False)
            
            entities = []
            current_entity = []
            current_label = None
            
            for item in tree:
                if hasattr(item, 'label'):  # It's a named entity
                    if current_label != item.label():
                        if current_entity:
                            entities.append({
                                'text': ' '.join(current_entity),
                                'type': current_label,
                                'confidence': 0.8  # Default confidence for NLTK
                            })
                        current_entity = [child[0] for child in item]
                        current_label = item.label()
                    else:
                        current_entity.extend([child[0] for child in item])
                else:
                    if current_entity:
                        entities.append({
                            'text': ' '.join(current_entity),
                            'type': current_label,
                            'confidence': 0.8
                        })
                        current_entity = []
                        current_label = None
            
            # Add the last entity if any
            if current_entity:
                entities.append({
                    'text': ' '.join(current_entity),
                    'type': current_label,
                    'confidence': 0.8
                })
            
            return entities
            
        except Exception as e:
            # Fallback: extract potential entities using simple heuristics
            return self._fallback_entity_extraction(text)
    
    def _fallback_entity_extraction(self, text):
        """Fallback entity extraction using simple patterns"""
        entities = []
        
        # Extract potential proper nouns (capitalized words)
        words = word_tokenize(text)
        pos_tags = pos_tag(words)
        
        for word, pos in pos_tags:
            if pos in ['NNP', 'NNPS'] and len(word) > 2:  # Proper nouns
                entities.append({
                    'text': word,
                    'type': 'PERSON/ORG',
                    'confidence': 0.6
                })
        
        return entities
    
    def summarize_text(self, text, max_sentences=3):
        """
        Create a summary of the text using extractive summarization
        
        Args:
            text (str): Text to summarize
            max_sentences (int): Maximum number of sentences in summary
            
        Returns:
            str: Text summary
        """
        try:
            sentences = sent_tokenize(text)
            
            if len(sentences) <= max_sentences:
                return text
            
            # Score sentences based on word frequency and educational keywords
            sentence_scores = self._score_sentences(sentences)
            
            # Select top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
            summary_sentences = [sent for sent, score in top_sentences[:max_sentences]]
            
            # Maintain original order
            summary = []
            for sentence in sentences:
                if sentence in summary_sentences:
                    summary.append(sentence)
            
            return ' '.join(summary)
            
        except Exception as e:
            # Fallback: return first few sentences
            sentences = text.split('. ')
            return '. '.join(sentences[:max_sentences]) + '.'
    
    def _score_sentences(self, sentences):
        """Score sentences for importance in educational content"""
        # Calculate word frequencies
        all_words = []
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            words = [self.lemmatizer.lemmatize(word) for word in words 
                    if word.isalpha() and word not in self.stop_words]
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # Score each sentence
        sentence_scores = {}
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            words = [self.lemmatizer.lemmatize(word) for word in words 
                    if word.isalpha() and word not in self.stop_words]
            
            score = 0
            for word in words:
                score += word_freq.get(word, 0)
                
                # Boost score for educational keywords
                if word in self.educational_keywords:
                    score += 5
            
            # Normalize by sentence length
            if words:
                sentence_scores[sentence] = score / len(words)
            else:
                sentence_scores[sentence] = 0
        
        return sentence_scores
    
    def extract_key_phrases(self, text, max_phrases=10):
        """
        Extract key phrases from text
        
        Args:
            text (str): Input text
            max_phrases (int): Maximum number of key phrases to extract
            
        Returns:
            list: List of key phrases with scores
        """
        try:
            # Tokenize and tag
            tokens = word_tokenize(text.lower())
            pos_tags = pos_tag(tokens)
            
            # Extract noun phrases and important terms
            key_phrases = []
            current_phrase = []
            
            for word, pos in pos_tags:
                if pos.startswith('NN') or pos.startswith('JJ'):  # Nouns and adjectives
                    if word not in self.stop_words and len(word) > 2:
                        current_phrase.append(word)
                else:
                    if len(current_phrase) >= 1:
                        phrase = ' '.join(current_phrase)
                        key_phrases.append(phrase)
                    current_phrase = []
            
            # Add last phrase
            if len(current_phrase) >= 1:
                phrase = ' '.join(current_phrase)
                key_phrases.append(phrase)
            
            # Score and rank phrases
            phrase_scores = Counter(key_phrases)
            
            # Boost educational terms
            for phrase in phrase_scores:
                if any(keyword in phrase for keyword in self.educational_keywords):
                    phrase_scores[phrase] *= 2
            
            # Return top phrases
            top_phrases = phrase_scores.most_common(max_phrases)
            return [{'phrase': phrase, 'score': score} for phrase, score in top_phrases]
            
        except Exception as e:
            # Fallback: simple word extraction
            words = text.lower().split()
            filtered_words = [w for w in words if len(w) > 4 and w not in self.stop_words]
            word_counts = Counter(filtered_words)
            return [{'phrase': word, 'score': count} for word, count in word_counts.most_common(max_phrases)]
    
    def analyze_text_complexity(self, text):
        """
        Analyze the complexity of text for educational purposes
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Complexity metrics
        """
        try:
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            # Basic metrics
            word_count = len([w for w in words if w.isalpha()])
            sentence_count = len(sentences)
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Syllable count (approximation)
            syllable_count = self._count_syllables(text)
            
            # Flesch Reading Ease (approximation)
            if sentence_count > 0 and word_count > 0:
                flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * syllable_count / word_count)
            else:
                flesch_score = 0
            
            # Vocabulary complexity
            unique_words = set(w.lower() for w in words if w.isalpha())
            vocabulary_diversity = len(unique_words) / word_count if word_count > 0 else 0
            
            # Educational complexity indicators
            educational_terms = sum(1 for word in words if word.lower() in self.educational_keywords)
            
            complexity_level = self._determine_complexity_level(flesch_score, avg_sentence_length, vocabulary_diversity)
            
            return {
                'word_count': word_count,
                'sentence_count': sentence_count,
                'avg_sentence_length': round(avg_sentence_length, 2),
                'flesch_reading_ease': round(flesch_score, 2),
                'vocabulary_diversity': round(vocabulary_diversity, 3),
                'educational_term_density': round(educational_terms / word_count, 3) if word_count > 0 else 0,
                'complexity_level': complexity_level
            }
            
        except Exception as e:
            return {
                'word_count': 0,
                'sentence_count': 0,
                'avg_sentence_length': 0,
                'flesch_reading_ease': 0,
                'vocabulary_diversity': 0,
                'educational_term_density': 0,
                'complexity_level': 'Unknown'
            }
    
    def _count_syllables(self, text):
        """Approximate syllable counting"""
        vowels = 'aeiouy'
        syllable_count = 0
        
        words = word_tokenize(text.lower())
        for word in words:
            if word.isalpha():
                word_syllables = 0
                prev_was_vowel = False
                
                for char in word:
                    if char in vowels:
                        if not prev_was_vowel:
                            word_syllables += 1
                        prev_was_vowel = True
                    else:
                        prev_was_vowel = False
                
                # Handle silent e
                if word.endswith('e') and word_syllables > 1:
                    word_syllables -= 1
                
                # Ensure at least one syllable per word
                syllable_count += max(1, word_syllables)
        
        return syllable_count
    
    def _determine_complexity_level(self, flesch_score, avg_sentence_length, vocabulary_diversity):
        """Determine overall complexity level"""
        if flesch_score >= 80 and avg_sentence_length < 15:
            return 'Beginner'
        elif flesch_score >= 60 and avg_sentence_length < 20:
            return 'Intermediate'
        else:
            return 'Advanced'
    
    def extract_questions_from_text(self, text):
        """Extract questions from text"""
        sentences = sent_tokenize(text)
        questions = [sent for sent in sentences if sent.strip().endswith('?')]
        return questions
    
    def extract_definitions(self, text):
        """Extract definitions from text using pattern matching"""
        definitions = []
        
        # Pattern: "X is defined as Y" or "X is Y"
        definition_patterns = [
            r'(.+?)\s+is\s+defined\s+as\s+(.+?)(?:\.|$)',
            r'(.+?)\s+is\s+(.+?)(?:\.|$)',
            r'(.+?):\s+(.+?)(?:\.|$)',
            r'Define\s+(.+?)\s*[:-]\s*(.+?)(?:\.|$)'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                
                # Filter out very short or very long terms/definitions
                if 2 <= len(term.split()) <= 5 and 3 <= len(definition.split()) <= 50:
                    definitions.append({
                        'term': term,
                        'definition': definition
                    })
        
        return definitions
    
    def identify_learning_objectives(self, text):
        """Identify potential learning objectives from text"""
        objectives = []
        
        # Look for sentences with learning objective indicators
        objective_indicators = [
            'understand', 'learn', 'identify', 'explain', 'describe', 'analyze',
            'compare', 'evaluate', 'apply', 'create', 'remember', 'comprehend'
        ]
        
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains objective indicators
            if any(indicator in sentence_lower for indicator in objective_indicators):
                # Clean up the sentence
                cleaned_sentence = re.sub(r'^(students\s+will\s+|learners\s+will\s+|you\s+will\s+)', '', sentence_lower)
                objectives.append(cleaned_sentence.strip())
        
        return objectives[:5]  # Return top 5 objectives
    
    def compute_similarity(self, text1, text2):
        """
        Compute similarity between two texts using sequence matching.
        
        Uses difflib's SequenceMatcher for basic string similarity.
        Good for exact/near-exact matches but not semantic understanding.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            # Use SequenceMatcher for simple similarity
            matcher = SequenceMatcher(None, text1.lower(), text2.lower())
            return matcher.ratio()
        except Exception as e:
            return 0.0
    
    def get_embedding(self, text):
        """
        Generate simple TF-IDF based embedding for text.
        
        Creates a basic vector representation using word frequencies.
        Used for semantic similarity in content caching.
        
        Args:
            text (str): Input text
            
        Returns:
            list: Embedding vector as list of floats
        """
        try:
            # For simplicity, use word frequencies as embedding
            words = self.lemmatizer.lemmatize(text.lower()).split()
            words = [w for w in words if w not in self.stop_words and w.isalpha()]
            embedding = [words.count(w) for w in set(words)]  # Simple count vector
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def compute_semantic_similarity(self, embedding1, embedding2):
        """
        Compute cosine similarity between two embedding vectors.
        
        Measures semantic similarity between text embeddings.
        Used in content caching to find similar queries.
        
        Args:
            embedding1 (list): First embedding vector
            embedding2 (list): Second embedding vector
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not embedding1 or not embedding2:
            return 0.0
        try:
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)
            similarity = cosine_similarity(vec1, vec2)[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0.0
    
    def moderate_content(self, query):
        """
        Moderate content query for safety and appropriateness.
        
        Checks the query against banned terms and dangerous patterns to prevent
        generation of harmful, illegal, or inappropriate content.
        
        Args:
            query (str): The content query to check
            
        Returns:
            dict: {"safe": bool, "reason": str} - approval status and explanation
        """
        query_lower = query.lower()
        
        # Check for banned terms (direct keyword matching)
        for term in self.banned_terms:
            if term in query_lower:
                return {
                    "safe": False,
                    "reason": f"Query contains inappropriate content: '{term}'"
                }
        
        # Check for dangerous patterns (e.g., "how to make bomb")
        dangerous_patterns = [
            r"how to.*(?:make|build|create).*(?:bomb|explosive|weapon)",  # Instructions for dangerous items
            r"how to.*(?:hack|steal|kill)",  # Harmful actions
            r"recipe for.*(?:drug|explosive)",  # Illegal recipes
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return {
                    "safe": False,
                    "reason": "Query matches harmful pattern"
                }
        
        # If no issues, approve
        return {
            "safe": True,
            "reason": "Content approved"
        }
