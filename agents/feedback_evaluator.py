"""
Feedback Evaluator Agent

This module implements the FeedbackEvaluatorAgent class, which provides intelligent
evaluation of student answers and generates personalized feedback. The agent uses
a combination of rule-based evaluation, NLP techniques, and AI-powered analysis
to assess student performance and provide constructive feedback.

Key Features:
- Multi-format question evaluation (MCQ, True/False, Short Answer, Essay, Fill-in-Blank)
- AI-powered text answer evaluation using Google Gemini
- Semantic similarity analysis for open-ended responses
- Comprehensive feedback generation with different styles
- Learning pattern analysis and personalized study suggestions
- Performance tracking and improvement recommendations

The agent supports various feedback types (Detailed, Summary, Constructive, Encouraging)
and can analyze performance across different cognitive levels using Bloom's taxonomy.

Classes:
    FeedbackEvaluatorAgent: Main agent class for answer evaluation and feedback generation

Dependencies:
    - google.genai: For AI-powered evaluation
    - utils.nlp_processor: For NLP analysis and similarity calculation
    - json, re, datetime: Standard library utilities
"""

import json
import os
from google import genai
from google.genai import types
from utils.nlp_processor import NLPProcessor
import re
from datetime import datetime

class FeedbackEvaluatorAgent:
    """
    Feedback Evaluator Agent for analyzing student responses and providing personalized feedback.

    This agent evaluates student answers across multiple question formats and provides
    detailed, constructive feedback to support learning. It combines automated scoring
    with AI-powered analysis to give comprehensive assessments.

    Attributes:
        client: Google Gemini API client for AI-powered evaluation
        nlp_processor: NLP processor for text analysis and similarity calculation
        agent_id: Unique identifier for this agent
    """

    def __init__(self):
        """Initialize the feedback evaluator agent with required dependencies."""
        # Using Google Gemini 2.5 Flash for free AI feedback evaluation
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.nlp_processor = NLPProcessor()
        self.agent_id = "feedback_evaluator"

    def evaluate_answers(self, questions, user_answers, feedback_type="Detailed", include_suggestions=True):
        """
        Evaluate user answers and provide comprehensive feedback.

        This is the main method that orchestrates the evaluation process. It evaluates
        each answer individually, calculates overall performance metrics, and generates
        detailed feedback with optional study suggestions.

        Args:
            questions (list): List of question dictionaries with answers and metadata
            user_answers (dict): User's answers keyed by question index
            feedback_type (str): Style of feedback ("Detailed", "Summary", "Constructive", "Encouraging")
            include_suggestions (bool): Whether to include personalized study suggestions

        Returns:
            dict: Comprehensive evaluation results including:
                - overall_score: Average score across all questions (0-100)
                - correct_count: Number of correct answers
                - total_questions: Total number of questions
                - detailed_feedback: Formatted feedback text
                - individual_evaluations: Per-question evaluation details
                - learning_analysis: Pattern analysis of learning
                - study_suggestions: Personalized improvement recommendations (if requested)
                - timestamp: Evaluation timestamp

        Raises:
            Exception: If evaluation process fails
        """
        try:
            # Evaluate each answer individually
            individual_evaluations = []
            correct_count = 0
            total_score = 0

            for i, question in enumerate(questions):
                # Handle both integer and string keys for flexibility
                user_answer = user_answers.get(i)
                if user_answer is None:
                    user_answer = user_answers.get(str(i), "")
                evaluation = self._evaluate_single_answer(question, user_answer)
                individual_evaluations.append(evaluation)

                if evaluation['is_correct']:
                    correct_count += 1

                total_score += evaluation['score']

            # Calculate overall performance metrics
            overall_score = (total_score / len(questions)) if questions else 0

            # Generate comprehensive feedback based on type
            detailed_feedback = self._generate_detailed_feedback(
                individual_evaluations, feedback_type
            )

            # Generate personalized study suggestions if requested
            study_suggestions = ""
            if include_suggestions:
                study_suggestions = self._generate_study_suggestions(
                    individual_evaluations, questions
                )

            # Analyze learning patterns and performance trends
            learning_analysis = self._analyze_learning_patterns(individual_evaluations)

            feedback_result = {
                'overall_score': round(overall_score, 1),
                'correct_count': correct_count,
                'total_questions': len(questions),
                'detailed_feedback': detailed_feedback,
                'individual_evaluations': individual_evaluations,
                'learning_analysis': learning_analysis,
                'timestamp': datetime.now().isoformat()
            }

            if include_suggestions:
                feedback_result['study_suggestions'] = study_suggestions

            return feedback_result

        except Exception as e:
            raise Exception(f"Answer evaluation failed: {str(e)}")

    def _evaluate_single_answer(self, question, user_answer):
        """
        Evaluate a single answer based on question type.

        Routes evaluation to appropriate method based on question format.
        Supports multiple choice, true/false, short answer, essay, and fill-in-blank questions.

        Args:
            question (dict): Question data with type, correct answer, etc.
            user_answer (str): Student's answer

        Returns:
            dict: Evaluation results with score, correctness, and feedback
        """
        question_type = question.get('type', 'Unknown')
        correct_answer = question.get('correct_answer', '')

        if question_type == 'Multiple Choice':
            return self._evaluate_mcq(question, user_answer)
        elif question_type == 'True/False':
            return self._evaluate_true_false(question, user_answer)
        elif question_type in ['Short Answer', 'Essay']:
            return self._evaluate_text_answer(question, user_answer)
        elif question_type == 'Fill in the Blank':
            return self._evaluate_fill_blank(question, user_answer)
        else:
            return self._evaluate_generic(question, user_answer)

    def _evaluate_mcq(self, question, user_answer):
        
        """
        Evaluate multiple choice question with exact matching.

        Args:
            question (dict): MCQ question data
            user_answer (str): Selected answer option

        Returns:
            dict: Evaluation with correctness and explanatory feedback
        """
        
        correct_answer = question.get('correct_answer', '')
        is_correct = user_answer.strip() == correct_answer.strip()

        return {
            'question_text': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'score': 100 if is_correct else 0,
            'feedback': self._get_mcq_feedback(question, user_answer, is_correct)
        }

    def _evaluate_true_false(self, question, user_answer):
        
        """
        Evaluate true/false question with case-insensitive matching.

        Args:
            question (dict): True/False question data
            user_answer (str): "True" or "False"

        Returns:
            dict: Simple evaluation with explanation
        """
        
        correct_answer = question.get('correct_answer', '')
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        return {
            'question_text': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'score': 100 if is_correct else 0,
            'feedback': question.get('explanation', 'No explanation available.')
        }

    def _evaluate_text_answer(self, question, user_answer):
        
        """
        Evaluate text-based answers using AI-powered analysis.

        Uses Google Gemini to provide nuanced evaluation of open-ended responses,
        considering accuracy, completeness, and understanding.

        Args:
            question (dict): Text question with sample answer and key points
            user_answer (str): Student's written response

        Returns:
            dict: Detailed evaluation with AI-generated feedback
        """
        
        if not user_answer.strip():
            return {
                'question_text': question['question'],
                'user_answer': user_answer,
                'correct_answer': question.get('sample_answer', ''),
                'is_correct': False,
                'score': 0,
                'feedback': 'No answer provided.'
            }

        # Use LLM for sophisticated text evaluation
        evaluation = self._llm_evaluate_text_answer(question, user_answer)

        return {
            'question_text': question['question'],
            'user_answer': user_answer,
            'correct_answer': question.get('sample_answer', ''),
            'is_correct': evaluation['score'] >= 70,  # Consider 70%+ as correct
            'score': evaluation['score'],
            'feedback': evaluation['feedback']
        }

    def _evaluate_fill_blank(self, question, user_answer):
        
        """
        Evaluate fill-in-the-blank questions with flexible matching.

        Supports partial matching and case-insensitive comparison to handle
        variations in student responses.

        Args:
            question (dict): Fill-in-blank question data
            user_answer (str): Student's answer

        Returns:
            dict: Evaluation with flexible correctness checking
        """
        
        correct_answer = question.get('correct_answer', '')

        # Flexible matching for fill-in-the-blank
        user_clean = user_answer.strip().lower()
        correct_clean = correct_answer.strip().lower()

        # Check exact match or partial containment
        is_correct = (user_clean == correct_clean or
                     user_clean in correct_clean or
                     correct_clean in user_clean)

        return {
            'question_text': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'score': 100 if is_correct else 0,
            'feedback': f"Correct answer: {correct_answer}" if not is_correct else "Correct!"
        }

    def _evaluate_generic(self, question, user_answer):
        
        """
        Generic evaluation fallback for unknown question types.

        Args:
            question (dict): Question data
            user_answer (str): Student's answer

        Returns:
            dict: Basic evaluation indicating inability to assess
        """
        
        return {
            'question_text': question.get('question', 'Unknown question'),
            'user_answer': user_answer,
            'correct_answer': question.get('correct_answer', 'Unknown'),
            'is_correct': False,
            'score': 0,
            'feedback': 'Unable to evaluate this question type.'
        }

    def _get_mcq_feedback(self, question, user_answer, is_correct):
        
        """
        Generate appropriate feedback for multiple choice questions.

        Args:
            question (dict): Question data with explanation
            user_answer (str): Selected answer
            is_correct (bool): Whether answer was correct

        Returns:
            str: Encouraging feedback with explanation
        """
        
        if is_correct:
            return "Correct! " + question.get('explanation', 'Well done!')
        else:
            explanation = question.get('explanation', '')
            correct_answer = question.get('correct_answer', '')
            return f"Incorrect. The correct answer is {correct_answer}. {explanation}"

    def _llm_evaluate_text_answer(self, question, user_answer):
        
        """
        Use Google Gemini LLM to evaluate text-based answers comprehensively.

        Provides nuanced assessment considering multiple factors like accuracy,
        completeness, understanding, and clarity.

        Args:
            question (dict): Question with sample answer and key points
            user_answer (str): Student's response

        Returns:
            dict: Evaluation with score (0-100) and detailed feedback
        """
        
        system_prompt = """You are an expert educational evaluator. Evaluate student answers fairly and constructively.

        Return your evaluation in JSON format:
        {
            "score": number (0-100),
            "feedback": "detailed feedback explaining the score",
            "strengths": ["strength 1", "strength 2"],
            "improvements": ["area for improvement 1", "area 2"]
        }"""

        sample_answer = question.get('sample_answer', '')
        key_points = question.get('key_points', [])

        user_prompt = f"""Evaluate this student answer:

Question: {question['question']}

Student Answer: {user_answer}

Sample/Expected Answer: {sample_answer}

Key Points to Look For: {', '.join(key_points) if key_points else 'General understanding and accuracy'}

Provide a score (0-100) and constructive feedback. Consider:
- Accuracy of information
- Completeness of answer
- Understanding demonstrated
- Clarity of explanation

Be encouraging but honest about areas for improvement."""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )

            if response.text:
                text = response.text.strip()
                # Clean up markdown formatting if present
                if text.startswith('```json'):
                    text = text[7:-3].strip()
                elif text.startswith('```'):
                    text = text[3:-3].strip()

                result = json.loads(text)
            else:
                result = {}
            return {
                'score': max(0, min(100, result.get('score', 0))),
                'feedback': result.get('feedback', 'No feedback available.')
            }

        except Exception:
            # Fallback to simpler evaluation if LLM fails
            return self._fallback_text_evaluation(question, user_answer)

    def _fallback_text_evaluation(self, question, user_answer):
        """
        Fallback text evaluation using keyword matching when LLM is unavailable.

        Args:
            question (dict): Question data
            user_answer (str): Student's answer

        Returns:
            dict: Basic evaluation with keyword overlap scoring
        """
        sample_answer = question.get('sample_answer', '').lower()
        user_lower = user_answer.lower()

        # Simple keyword matching approach
        if sample_answer:
            sample_words = set(sample_answer.split())
            user_words = set(user_lower.split())
            overlap = len(sample_words.intersection(user_words))
            score = min(100, (overlap / len(sample_words)) * 100) if sample_words else 50
        else:
            score = 50  # Give partial credit if no sample answer available

        return {
            'score': score,
            'feedback': f"Answer evaluated. Score: {score:.0f}%. Consider expanding your response with more specific details."
        }

    def _generate_detailed_feedback(self, evaluations, feedback_type):
        """
        Generate comprehensive feedback based on specified type.

        Args:
            evaluations (list): Individual question evaluations
            feedback_type (str): Type of feedback to generate

        Returns:
            str: Formatted feedback text
        """
        if feedback_type == "Summary":
            return self._generate_summary_feedback(evaluations)
        elif feedback_type == "Constructive":
            return self._generate_constructive_feedback(evaluations)
        elif feedback_type == "Encouraging":
            return self._generate_encouraging_feedback(evaluations)
        else:  # Detailed
            return self._generate_comprehensive_feedback(evaluations)

    def _generate_comprehensive_feedback(self, evaluations):
        """
        Generate detailed comprehensive feedback with question-by-question analysis.

        Args:
            evaluations (list): Individual evaluations

        Returns:
            str: Detailed markdown-formatted feedback
        """
        total_questions = len(evaluations)
        correct_answers = sum(1 for eval in evaluations if eval['is_correct'])
        avg_score = sum(eval['score'] for eval in evaluations) / total_questions if evaluations else 0

        feedback_parts = [
            f"## 📊 Performance Summary",
            f"- **Score:** {avg_score:.1f}%",
            f"- **Correct Answers:** {correct_answers}/{total_questions}",
            f"- **Performance Level:** {self._get_performance_level(avg_score)}",
            "",
            "## 📝 Question-by-Question Analysis"
        ]

        for i, eval in enumerate(evaluations, 1):
            status = "✅" if eval['is_correct'] else "❌"
            feedback_parts.append(f"**Question {i}** {status} (Score: {eval['score']:.0f}%)")
            feedback_parts.append(f"*Feedback:* {eval['feedback']}")
            feedback_parts.append("")

        return "\n".join(feedback_parts)

    def _generate_summary_feedback(self, evaluations):
        """
        Generate brief summary feedback.

        Args:
            evaluations (list): Individual evaluations

        Returns:
            str: Concise performance summary
        """
        correct = sum(1 for eval in evaluations if eval['is_correct'])
        total = len(evaluations)
        avg_score = sum(eval['score'] for eval in evaluations) / total if evaluations else 0

        return f"""## 📊 Quick Summary
**Score:** {avg_score:.1f}% | **Correct:** {correct}/{total}

{self._get_performance_message(avg_score)}"""

    def _generate_constructive_feedback(self, evaluations):
        """
        Generate constructive feedback focusing on improvement areas.

        Args:
            evaluations (list): Individual evaluations

        Returns:
            str: Feedback emphasizing areas for growth
        """
        incorrect_evals = [eval for eval in evaluations if not eval['is_correct']]

        if not incorrect_evals:
            return "🎉 Excellent work! You answered all questions correctly. Keep up the great learning!"

        feedback_parts = [
            "## 🎯 Areas for Improvement",
            "",
            "Focus on these areas to enhance your understanding:"
        ]

        for i, eval in enumerate(incorrect_evals[:3], 1):  # Show top 3 areas
            feedback_parts.append(f"{i}. {eval['feedback']}")

        return "\n".join(feedback_parts)

    def _generate_encouraging_feedback(self, evaluations):
        """
        Generate encouraging, positive feedback.

        Args:
            evaluations (list): Individual evaluations

        Returns:
            str: Motivational feedback based on performance
        """
        correct = sum(1 for eval in evaluations if eval['is_correct'])
        total = len(evaluations)

        if correct == total:
            return "🌟 Outstanding! Perfect score! You've mastered this material completely!"
        elif correct >= total * 0.8:
            return "🎉 Excellent work! You're showing strong understanding. Keep building on this solid foundation!"
        elif correct >= total * 0.6:
            return "👍 Good progress! You're getting the hang of this. A bit more practice and you'll excel!"
        else:
            return "💪 Keep going! Every expert was once a beginner. You're learning and improving with each attempt!"

    def _generate_study_suggestions(self, evaluations, questions):
        """
        Generate personalized study suggestions based on performance analysis.

        Uses AI to create tailored recommendations addressing weak areas.

        Args:
            evaluations (list): Individual question evaluations
            questions (list): Original question data

        Returns:
            str: Personalized study recommendations
        """
        # Identify problem areas from incorrect answers
        weak_areas = []
        question_types_missed = []

        for eval in evaluations:
            if not eval['is_correct']:
                # Extract topic from question (simplified analysis)
                question_text = eval['question_text'].lower()

                # Simple topic extraction based on keywords
                if 'definition' in question_text or 'define' in question_text:
                    weak_areas.append("Definitions and terminology")
                elif 'example' in question_text or 'application' in question_text:
                    weak_areas.append("Practical applications")
                elif 'compare' in question_text or 'difference' in question_text:
                    weak_areas.append("Comparisons and contrasts")
                else:
                    weak_areas.append("Core concepts")

        # Generate AI-powered suggestions if weak areas identified
        if weak_areas:
            suggestions_prompt = f"""Based on these learning weaknesses, provide 3-5 specific study suggestions:

Weak areas identified: {', '.join(set(weak_areas))}

Provide actionable study recommendations that address these specific areas."""

            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"You are a helpful study advisor providing specific, actionable learning recommendations.\n\n{suggestions_prompt}"
                )

                return response.text or "No suggestions available"

            except Exception:
                return self._fallback_study_suggestions([])
        else:
            return "🎯 Great work! To maintain your understanding, try teaching these concepts to someone else or applying them to new scenarios."

    def _evaluate_with_semantic_analysis(self, question, user_answer, feedback_type):
        """
        Evaluate answer using semantic similarity and AI analysis (advanced method).

        Combines NLP similarity scoring with AI evaluation for comprehensive assessment.

        Args:
            question (dict): Question data
            user_answer (str): Student's answer
            feedback_type (str): Type of feedback requested

        Returns:
            dict: Comprehensive evaluation with multiple scoring components
        """
        try:
            # Calculate semantic similarity using NLP processor
            semantic_score = self._calculate_semantic_similarity(question, user_answer)

            # Get AI-powered evaluation
            ai_evaluation = self._evaluate_with_ai(question, user_answer, feedback_type)

            # Combine scores with weighted average
            combined_score = (semantic_score * 0.3) + (ai_evaluation['score'] * 0.7)

            return {
                'score': round(combined_score, 1),
                'feedback': ai_evaluation['feedback'],
                'semantic_score': semantic_score,
                'ai_score': ai_evaluation['score'],
                'understanding_level': self._assess_understanding_level(combined_score),
                'key_points_covered': self._identify_covered_concepts(question, user_answer)
            }

        except Exception:
            # Fallback to basic evaluation
            return self._evaluate_single_answer(question, user_answer)

    def _calculate_semantic_similarity(self, question, user_answer):
        """
        Calculate semantic similarity between user answer and expected answer.

        Args:
            question (dict): Question with expected answer
            user_answer (str): Student's response

        Returns:
            float: Similarity score (0-100)
        """
        try:
            expected_answer = question.get('correct_answer', '') or question.get('sample_answer', '')
            key_points = question.get('key_points', [])

            if not expected_answer:
                return 50.0  # Default score if no reference answer

            # Use NLP processor for similarity if available
            if hasattr(self.nlp_processor, 'calculate_similarity'):
                similarity = self.nlp_processor.calculate_similarity(user_answer, expected_answer)
                return min(100, similarity * 100)

            # Simple keyword matching fallback
            user_words = set(user_answer.lower().split())
            expected_words = set(expected_answer.lower().split())

            if expected_words:
                overlap = len(user_words.intersection(expected_words))
                similarity = overlap / len(expected_words)
                return min(100, similarity * 100)

            return 50.0

        except Exception:
            return 50.0

    def _assess_understanding_level(self, score):
        """
        Assess understanding level based on numerical score.

        Args:
            score (float): Evaluation score (0-100)

        Returns:
            str: Understanding level description
        """
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Satisfactory"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Requires Attention"

    def _identify_covered_concepts(self, question, user_answer):
        """
        Identify which key concepts were covered in the student's answer.

        Args:
            question (dict): Question with key concepts
            user_answer (str): Student's response

        Returns:
            list: List of covered concepts
        """
        key_concepts = question.get('key_concepts', [])
        covered = []

        user_answer_lower = user_answer.lower()
        for concept in key_concepts:
            if concept.lower() in user_answer_lower:
                covered.append(concept)

        return covered

    def _generate_comprehensive_feedback_with_history(self, results, avg_score, feedback_type, performance_history):
        """
        Advanced comprehensive feedback incorporating historical performance (not currently used).

        Args:
            results (list): Current evaluation results
            avg_score (float): Average score
            feedback_type (str): Feedback style
            performance_history (list): Historical performance data

        Returns:
            str: Comprehensive feedback with historical context
        """
        try:
            system_prompt = ("You are an expert educational evaluator providing comprehensive feedback.\n\n"
                             f"Feedback Type: {feedback_type}\n\n"
                             "Analyze the student's performance and provide:\n"
                             "1. Overall assessment of understanding\n"
                             "2. Specific strengths demonstrated\n"
                             "3. Areas needing improvement\n"
                             "4. Learning progress indicators\n"
                             "5. Motivational guidance\n\n"
                             "Be encouraging but honest about areas for improvement.")
            total_questions = len(results)
            correct_answers = len([r for r in results if r['score'] >= 70])
            difficulty_breakdown = self._analyze_difficulty_performance(results)
            bloom_breakdown = self._analyze_bloom_performance(results)
            trend = ""
            if performance_history and hasattr(self, '_analyze_performance_trend'):
                try:
                    trend = f"Previous performance trend: {self._analyze_performance_trend(performance_history)}"
                except Exception:
                    trend = ""
            user_prompt = ("Provide comprehensive feedback for a student who:\n"
                           f"- Answered {total_questions} questions\n"
                           f"- Got {correct_answers} answers satisfactory or better (≥70%)\n"
                           f"- Overall score: {avg_score:.1f}%\n"
                           f"- Difficulty performance: {difficulty_breakdown}\n"
                           f"- Bloom's taxonomy performance: {bloom_breakdown}\n\n"
                           f"{trend}\n\n"
                           "Provide specific, actionable feedback that acknowledges strengths and guides improvement.")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )
            return response.text or "Good effort! Keep practicing to improve your understanding."
        except Exception:
            return self._generate_basic_feedback(avg_score, len(results))

    def _generate_basic_feedback(self, avg_score, total_questions):
        """
        Generate basic feedback when advanced methods fail.

        Args:
            avg_score (float): Average score
            total_questions (int): Total questions answered

        Returns:
            str: Simple feedback message
        """
        return (f"Score: {avg_score:.1f}% over {total_questions} questions. "
                f"{self._get_performance_message(avg_score)}")

    def _generate_adaptive_suggestions(self, results, questions, concept_scores, performance_history):
        """
        Generate adaptive study suggestions based on performance patterns (not currently used).

        Args:
            results (list): Evaluation results
            questions (list): Question data
            concept_scores (dict): Concept-wise performance
            performance_history (list): Historical data

        Returns:
            str: Adaptive study recommendations
        """
        try:
            # Identify weak concepts
            weak_concepts = [concept for concept, scores in concept_scores.items()
                           if sum(scores)/len(scores) < 70]

            # Identify difficulty patterns
            difficulty_issues = self._identify_difficulty_patterns(results)

            # Identify Bloom level gaps
            bloom_gaps = self._identify_bloom_gaps(results)

            system_prompt = """You are an expert study advisor. Provide specific, actionable study recommendations."""

            user_prompt = f"""Create personalized study suggestions for a student with:

            Weak Concepts: {', '.join(weak_concepts[:5]) if weak_concepts else 'None identified'}
            Difficulty Struggles: {difficulty_issues}
            Learning Level Gaps: {bloom_gaps}

            Provide 3-5 specific study strategies that address these patterns:
            1. Focus areas for review
            2. Recommended study methods
            3. Practice suggestions
            4. Resources to use
            5. Timeline for improvement

            Make suggestions practical and achievable."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}"
            )

            return response.text or "Continue practicing and reviewing key concepts."

        except Exception:
            return "Focus on reviewing missed concepts and practice similar questions."

    def _analyze_difficulty_performance(self, results):
        """
        Analyze performance by difficulty level.

        Args:
            results (list): Evaluation results with difficulty metadata

        Returns:
            dict: Average scores by difficulty level
        """
        difficulty_scores = {"Easy": [], "Medium": [], "Hard": []}

        for result in results:
            difficulty = result.get('difficulty', 'Medium')
            if difficulty in difficulty_scores:
                difficulty_scores[difficulty].append(result['score'])

        performance = {}
        for difficulty, scores in difficulty_scores.items():
            if scores:
                performance[difficulty] = round(sum(scores) / len(scores), 1)

        return performance

    def _analyze_bloom_performance(self, results):
        """
        Analyze performance by Bloom's taxonomy level.

        Args:
            results (list): Evaluation results with Bloom level metadata

        Returns:
            dict: Average scores by Bloom level
        """
        bloom_scores = {}

        for result in results:
            bloom_level = result.get('bloom_level', 'Unknown')
            if bloom_level not in bloom_scores:
                bloom_scores[bloom_level] = []
            bloom_scores[bloom_level].append(result['score'])

        performance = {}
        for level, scores in bloom_scores.items():
            if scores:
                performance[level] = round(sum(scores) / len(scores), 1)

        return performance

    def _identify_strengths(self, results):
        """
        Identify student's strengths based on performance analysis.

        Args:
            results (list): Evaluation results

        Returns:
            list: List of identified strengths
        """
        strengths = []

        # High-scoring areas
        high_scores = [r for r in results if r['score'] >= 85]
        if len(high_scores) > len(results) * 0.5:
            strengths.append("Strong overall understanding")

        # Difficulty strengths
        difficulty_perf = self._analyze_difficulty_performance(results)
        for difficulty, score in difficulty_perf.items():
            if score >= 80:
                strengths.append(f"Excellent {difficulty.lower()} question performance")

        # Bloom level strengths
        bloom_perf = self._analyze_bloom_performance(results)
        for level, score in bloom_perf.items():
            if score >= 80:
                strengths.append(f"Strong {level.lower()} skills")

        return strengths[:5]  # Top 5 strengths

    def _identify_improvement_areas(self, results, concept_scores):
        """
        Identify areas needing improvement.

        Args:
            results (list): Evaluation results
            concept_scores (dict): Concept-wise performance scores

        Returns:
            list: List of improvement areas...
        """
        improvements = []

        # Low-scoring concepts
        weak_concepts = [concept for concept, scores in concept_scores.items()
                        if sum(scores)/len(scores) < 60]
        if weak_concepts:
            improvements.append(f"Review concepts: {', '.join(weak_concepts[:3])}")

        # Difficulty areas
        difficulty_perf = self._analyze_difficulty_performance(results)
        for difficulty, score in difficulty_perf.items():
            if score < 60:
                improvements.append(f"Practice more {difficulty.lower()} questions")

        # Bloom level gaps
        bloom_perf = self._analyze_bloom_performance(results)
        for level, score in bloom_perf.items():
            if score < 60:
                improvements.append(f"Develop {level.lower()} skills")

        return improvements[:5]  # Top 5 improvement areas

    def _fallback_study_suggestions(self, weak_areas):
        """
        Fallback study suggestions when AI generation fails.

        Returns:
            str: Generic study recommendations in markdown format
        """
        suggestions = [
            "📚 Review the fundamental concepts and definitions",
            "💡 Practice with additional examples and exercises",
            "🔄 Create your own summary notes of key points",
            "👥 Form a study group to discuss challenging topics",
            "🎯 Focus extra time on areas where you missed questions"
        ]

        return "## 💡 Study Suggestions\n\n" + "\n".join(suggestions)

    def _analyze_learning_patterns(self, evaluations):
        """
        Analyze patterns in student learning and performance.

        Args:
            evaluations (list): Individual question evaluations

        Returns:
            dict: Analysis of learning patterns including accuracy, strengths, and weaknesses
        """
        total_questions = len(evaluations)
        if total_questions == 0:
            return {}

        patterns = {
            'accuracy_rate': sum(1 for eval in evaluations if eval['is_correct']) / total_questions,
            'average_score': sum(eval['score'] for eval in evaluations) / total_questions,
            'question_types_performance': {},
            'strengths': [],
            'weaknesses': []
        }

        # Identify strengths and weaknesses based on performance
        if patterns['accuracy_rate'] >= 0.8:
            patterns['strengths'].append("High overall accuracy")
        if patterns['average_score'] >= 85:
            patterns['strengths'].append("Strong detailed understanding")

        if patterns['accuracy_rate'] < 0.6:
            patterns['weaknesses'].append("Needs improvement in basic concepts")
        if patterns['average_score'] < 70:
            patterns['weaknesses'].append("Could benefit from more detailed explanations")

        return patterns

    def _get_performance_level(self, score):
        """
        Get performance level description based on score.

        Args:
            score (float): Numerical score (0-100)

        Returns:
            str: Performance level description
        """
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Satisfactory"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Requires Additional Study"

    def _get_performance_message(self, score):
        """
        Get encouraging performance message based on score.

        Args:
            score (float): Numerical score (0-100)

        Returns:
            str: Motivational message with emoji
        """
        if score >= 90:
            return "🌟 Outstanding performance! You've mastered this material."
        elif score >= 80:
            return "🎉 Great job! You have a solid understanding."
        elif score >= 70:
            return "👍 Good work! You're on the right track."
        elif score >= 60:
            return "💪 Keep practicing! You're making progress."
        else:
            return "📚 Review the material and try again. You can do it!"
