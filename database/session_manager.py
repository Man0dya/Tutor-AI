"""
Session Manager Module

This module implements the SessionManager class, which provides comprehensive
session management and data persistence for the Tutor AI system. It handles
user sessions, content storage, progress tracking, and maintains persistent
data across application restarts.

Key Features:
- User session lifecycle management (create, update, delete)
- Persistent storage of generated content, questions, and feedback
- Progress tracking and analytics
- User preferences and statistics
- Automatic data cleanup and export/import functionality
- Thread-safe data structures with JSON-based persistence

Data Structures:
- Sessions: Active user sessions with metadata
- User Data: User profiles, preferences, and statistics
- Content History: Generated educational content per user
- Question History: Generated question sets per user
- Feedback History: Assessment results and evaluations

Storage Format:
- JSON files for persistence in configurable storage path
- Automatic data loading on initialization
- Incremental saves to prevent data loss

Author: Tutor AI Team
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pickle
from collections import defaultdict

class SessionManager:
    """
    Session Manager for the tutoring system.

    This class manages all user-related data persistence and session handling
    for the Tutor AI application. It provides methods for creating sessions,
    storing content, tracking progress, and maintaining user preferences.

    Attributes:
        storage_path (str): Directory path for data persistence
        sessions (dict): Active user sessions
        user_data (defaultdict): User profile and preference data
        content_history (defaultdict): Generated content per user
        question_history (defaultdict): Generated questions per user
        feedback_history (defaultdict): Assessment feedback per user

    Methods:
        create_session: Create new user sessions
        get_session: Retrieve session data
        save_content: Store generated educational content
        save_questions: Store generated question sets
        save_feedback: Store assessment results
        get_user_progress: Retrieve comprehensive progress data
        get_user_stats: Get user statistics and activity
        cleanup_old_data: Remove outdated data
        export_user_data: Export user data for backup
    """
    
    def __init__(self, storage_path: str = "data/sessions"):
        """
        Initialize the Session Manager.

        Sets up data structures for session management and loads existing
        data from persistent storage. Creates storage directory if it doesn't exist.

        Args:
            storage_path (str): Directory path for storing session data files.
                Defaults to "data/sessions".
        """
        self.storage_path = storage_path
        self.sessions = {}
        self.user_data = defaultdict(dict)
        self.content_history = defaultdict(dict)
        self.question_history = defaultdict(dict)
        self.feedback_history = defaultdict(dict)

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Load existing data from persistent storage
        self._load_session_data()
    
    def _load_session_data(self):
        """
        Load session data from persistent storage.

        Attempts to load all session-related data from JSON files in the
        storage directory. If files don't exist or loading fails, initializes
        with empty data structures.

        Handles loading of:
        - User sessions
        - User profile data
        - Content generation history
        - Question generation history
        - Feedback evaluation history

        Note: Uses defaultdict to maintain compatibility with existing data.
        """
        try:
            # Load user sessions from JSON file
            sessions_file = os.path.join(self.storage_path, "sessions.json")
            if os.path.exists(sessions_file):
                with open(sessions_file, 'r') as f:
                    self.sessions = json.load(f)

            # Load user profile and preference data
            user_data_file = os.path.join(self.storage_path, "user_data.json")
            if os.path.exists(user_data_file):
                with open(user_data_file, 'r') as f:
                    loaded_data = json.load(f)
                    self.user_data = defaultdict(dict, loaded_data)

            # Load content generation history
            content_file = os.path.join(self.storage_path, "content_history.json")
            if os.path.exists(content_file):
                with open(content_file, 'r') as f:
                    loaded_content = json.load(f)
                    self.content_history = defaultdict(dict, loaded_content)

            # Load question generation history
            question_file = os.path.join(self.storage_path, "question_history.json")
            if os.path.exists(question_file):
                with open(question_file, 'r') as f:
                    loaded_questions = json.load(f)
                    self.question_history = defaultdict(dict, loaded_questions)

            # Load feedback evaluation history
            feedback_file = os.path.join(self.storage_path, "feedback_history.json")
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r') as f:
                    loaded_feedback = json.load(f)
                    self.feedback_history = defaultdict(dict, loaded_feedback)

        except Exception as e:
            print(f"Error loading session data: {e}")
            # Initialize with empty data structures if loading fails
            self.sessions = {}
            self.user_data = defaultdict(dict)
            self.content_history = defaultdict(dict)
            self.question_history = defaultdict(dict)
            self.feedback_history = defaultdict(dict)
    
    def _save_session_data(self):
        """
        Save session data to persistent storage.

        Persists all session-related data to JSON files in the storage directory.
        Each data structure is saved to a separate file for better organization
        and easier debugging.

        Saves:
        - sessions.json: Active user sessions
        - user_data.json: User profiles and preferences
        - content_history.json: Generated content history
        - question_history.json: Generated questions history
        - feedback_history.json: Assessment feedback history

        Note: Uses pretty-printing (indent=2) for better file readability.
        """
        try:
            # Save active sessions to JSON file
            sessions_file = os.path.join(self.storage_path, "sessions.json")
            with open(sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)

            # Save user profile data
            user_data_file = os.path.join(self.storage_path, "user_data.json")
            with open(user_data_file, 'w') as f:
                json.dump(dict(self.user_data), f, indent=2)

            # Save content generation history
            content_file = os.path.join(self.storage_path, "content_history.json")
            with open(content_file, 'w') as f:
                json.dump(dict(self.content_history), f, indent=2)

            # Save question generation history
            question_file = os.path.join(self.storage_path, "question_history.json")
            with open(question_file, 'w') as f:
                json.dump(dict(self.question_history), f, indent=2)

            # Save feedback evaluation history
            feedback_file = os.path.join(self.storage_path, "feedback_history.json")
            with open(feedback_file, 'w') as f:
                json.dump(dict(self.feedback_history), f, indent=2)

        except Exception as e:
            print(f"Error saving session data: {e}")
    
    def create_session(self, user_id: str, session_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new user session.

        Generates a unique session ID and initializes session data with
        creation timestamp and user association. Also updates user statistics.

        Args:
            user_id (str): Unique identifier for the user.
            session_data (dict, optional): Initial session data. Defaults to empty dict.

        Returns:
            str: Unique session identifier for the created session.
        """
        session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"

        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'data': session_data or {}
        }

        # Initialize user data if this is their first session
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'created_at': datetime.now().isoformat(),
                'total_sessions': 0,
                'preferences': {}
            }

        # Update user statistics
        self.user_data[user_id]['total_sessions'] += 1
        self.user_data[user_id]['last_login'] = datetime.now().isoformat()

        self._save_session_data()
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data by session ID.

        Updates the session's last active timestamp when accessed.

        Args:
            session_id (str): Unique session identifier.

        Returns:
            dict or None: Session data if found, None otherwise.
        """
        session = self.sessions.get(session_id)
        if session:
            # Update last active timestamp
            session['last_active'] = datetime.now().isoformat()
            self._save_session_data()
        return session

    def update_session(self, session_id: str, data: Dict[str, Any]):
        """
        Update session data.

        Merges new data with existing session data and updates last active timestamp.

        Args:
            session_id (str): Unique session identifier.
            data (dict): Data to update in the session.
        """
        if session_id in self.sessions:
            self.sessions[session_id]['data'].update(data)
            self.sessions[session_id]['last_active'] = datetime.now().isoformat()
            self._save_session_data()

    def delete_session(self, session_id: str):
        """
        Delete a user session.

        Removes the session from active sessions and persists the change.

        Args:
            session_id (str): Unique session identifier to delete.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_session_data()
    
    def save_content(self, user: str, topic: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Save generated educational content for a user.

        Stores content with metadata and maintains a history of recent content.
        Automatically manages storage limits by keeping only the most recent entries.

        Args:
            user (str): User identifier.
            topic (str): Topic or subject of the content.
            content (str): The generated educational content.
            metadata (dict, optional): Additional metadata about the content.
        """
        if not user:
            return

        content_id = f"content_{int(datetime.now().timestamp())}_{len(self.content_history[user])}"

        content_data = {
            'id': content_id,
            'topic': topic,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.content_history[user][content_id] = content_data

        # Maintain storage limit - keep only recent 50 entries per user
        if len(self.content_history[user]) > 50:
            oldest_items = sorted(
                self.content_history[user].items(),
                key=lambda x: x[1]['created_at']
            )
            for old_id, _ in oldest_items[:-50]:
                del self.content_history[user][old_id]

        self._save_session_data()

    def get_recent_content(self, user: str, limit: int = 10) -> Dict[str, str]:
        """
        Retrieve recent content generated by a user.

        Returns the most recently generated content, sorted by creation time.

        Args:
            user (str): User identifier.
            limit (int): Maximum number of content items to return. Defaults to 10.

        Returns:
            dict: Mapping of topic names to content strings.
        """
        if not user or user not in self.content_history:
            return {}

        user_content = self.content_history[user]

        # Sort by creation time (most recent first)
        sorted_content = sorted(
            user_content.items(),
            key=lambda x: x[1]['created_at'],
            reverse=True
        )

        # Return topic -> content mapping for recent items
        recent_content = {}
        for content_id, content_data in sorted_content[:limit]:
            topic = content_data['topic']
            recent_content[topic] = content_data['content']

        return recent_content

    def save_questions(self, user: str, questions: List[Dict], content_source: str = "Unknown"):
        """
        Save generated question sets for a user.

        Stores question data with source information and maintains question history.
        Automatically manages storage by keeping only recent question sets.

        Args:
            user (str): User identifier.
            questions (list): List of question dictionaries.
            content_source (str): Source topic or content the questions are based on.
        """
        if not user:
            return

        question_set_id = f"questions_{int(datetime.now().timestamp())}_{len(self.question_history[user])}"

        question_data = {
            'id': question_set_id,
            'questions': questions,
            'content_source': content_source,
            'created_at': datetime.now().isoformat()
        }

        self.question_history[user][question_set_id] = question_data

        # Maintain storage limit - keep only recent 20 question sets per user
        if len(self.question_history[user]) > 20:
            oldest_items = sorted(
                self.question_history[user].items(),
                key=lambda x: x[1]['created_at']
            )
            for old_id, _ in oldest_items[:-20]:
                del self.question_history[user][old_id]

        self._save_session_data()

    def get_recent_questions(self, user: str, limit: int = 5) -> Dict[str, List]:
        """
        Retrieve recent question sets generated for a user.

        Returns the most recently generated question sets with descriptive names.

        Args:
            user (str): User identifier.
            limit (int): Maximum number of question sets to return. Defaults to 5.

        Returns:
            dict: Mapping of descriptive names to question lists.
        """
        if not user or user not in self.question_history:
            return {}

        user_questions = self.question_history[user]

        # Sort by creation time (most recent first)
        sorted_questions = sorted(
            user_questions.items(),
            key=lambda x: x[1]['created_at'],
            reverse=True
        )

        # Return descriptive_name -> questions mapping
        recent_questions = {}
        for question_id, question_data in sorted_questions[:limit]:
            source = question_data['content_source']
            timestamp = datetime.fromisoformat(question_data['created_at']).strftime("%m/%d %H:%M")
            display_name = f"{source} ({timestamp})"
            recent_questions[display_name] = question_data['questions']

        return recent_questions
    
    def save_feedback(self, user: str, feedback: Dict[str, Any], question_set: str = "Unknown"):
        """
        Save assessment feedback and evaluation results for a user.

        Stores feedback data with question set information and maintains
        feedback history for progress tracking and analytics.

        Args:
            user (str): User identifier.
            feedback (dict): Feedback evaluation data from assessment.
            question_set (str): Name or identifier of the question set assessed.
        """
        if not user:
            return

        feedback_id = f"feedback_{int(datetime.now().timestamp())}_{len(self.feedback_history[user])}"

        feedback_data = {
            'id': feedback_id,
            'feedback': feedback,
            'question_set': question_set,
            'created_at': datetime.now().isoformat()
        }

        self.feedback_history[user][feedback_id] = feedback_data

        # Maintain storage limit - keep only recent 30 feedback entries per user
        if len(self.feedback_history[user]) > 30:
            oldest_items = sorted(
                self.feedback_history[user].items(),
                key=lambda x: x[1]['created_at']
            )
            for old_id, _ in oldest_items[:-30]:
                del self.feedback_history[user][old_id]

        self._save_session_data()

    def get_user_progress(self, user: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive progress data and analytics for a user.

        Aggregates data from content generation, assessments, and feedback
        to provide insights into learning progress and performance.

        Args:
            user (str): User identifier.

        Returns:
            dict: Comprehensive progress data including:
                - content_count: Number of content items generated
                - questions_answered: Total questions answered in assessments
                - average_score: Average assessment score
                - study_streak: Current consecutive study days
                - score_history: Historical scores with dates
                - subject_performance: Performance breakdown by subject
                - recent_activity: Recent learning activities
        """
        if not user:
            return {}

        progress_data = {
            'content_count': 0,
            'questions_answered': 0,
            'average_score': 0,
            'study_streak': 0,
            'score_history': [],
            'subject_performance': {},
            'recent_activity': []
        }

        # Calculate content statistics
        if user in self.content_history:
            progress_data['content_count'] = len(self.content_history[user])

        # Calculate assessment and scoring statistics from feedback
        if user in self.feedback_history:
            feedback_data = self.feedback_history[user]
            scores = []
            subject_scores = defaultdict(list)

            for feedback_entry in feedback_data.values():
                feedback_info = feedback_entry['feedback']
                score = feedback_info.get('overall_score', 0)
                scores.append(score)

                # Add to score history with date
                created_at = feedback_entry['created_at']
                progress_data['score_history'].append({
                    'date': created_at,
                    'score': score
                })

                # Track subject performance
                metadata = feedback_entry['feedback'].get('metadata', {})
                subject = metadata.get('subject', 'General')
                subject_scores[subject].append(score)

                # Count total questions answered
                progress_data['questions_answered'] += feedback_info.get('total_questions', 0)

            # Calculate average scores
            if scores:
                progress_data['average_score'] = sum(scores) / len(scores)

            # Calculate subject averages
            for subject, subject_score_list in subject_scores.items():
                progress_data['subject_performance'][subject] = sum(subject_score_list) / len(subject_score_list)

            # Sort score history chronologically
            progress_data['score_history'].sort(key=lambda x: x['date'])

        # Calculate study streak
        progress_data['study_streak'] = self._calculate_study_streak(user)

        # Get recent activity summary
        progress_data['recent_activity'] = self._get_recent_activity(user)

        return progress_data
    
    def _calculate_study_streak(self, user: str) -> int:
        """
        Calculate the current study streak for a user.

        A study streak is the number of consecutive days where the user
        has been active (generated content or completed assessments).

        Args:
            user (str): User identifier.

        Returns:
            int: Number of consecutive study days (current streak).
        """
        if user not in self.feedback_history:
            return 0

        # Collect all activity dates from feedback and content
        activity_dates = []

        # Feedback activity dates
        for feedback_entry in self.feedback_history[user].values():
            date_str = feedback_entry['created_at']
            date_obj = datetime.fromisoformat(date_str).date()
            activity_dates.append(date_obj)

        # Content generation dates
        if user in self.content_history:
            for content_entry in self.content_history[user].values():
                date_str = content_entry['created_at']
                date_obj = datetime.fromisoformat(date_str).date()
                activity_dates.append(date_obj)

        if not activity_dates:
            return 0

        # Sort dates and find consecutive streak
        unique_dates = sorted(set(activity_dates), reverse=True)

        streak = 0
        today = datetime.now().date()

        for i, date in enumerate(unique_dates):
            expected_date = today - timedelta(days=i)
            if date == expected_date:
                streak += 1
            else:
                break

        return streak

    def _get_recent_activity(self, user: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent learning activities for a user.

        Compiles a chronological list of recent content generation and
        assessment activities for progress tracking.

        Args:
            user (str): User identifier.
            limit (int): Maximum number of activities to return. Defaults to 10.

        Returns:
            list: List of activity dictionaries with type, description, date, and optional score.
        """
        activities = []

        # Add content generation activities
        if user in self.content_history:
            for content_entry in self.content_history[user].values():
                activities.append({
                    'type': 'Content Generated',
                    'description': f"Generated content for: {content_entry['topic']}",
                    'date': datetime.fromisoformat(content_entry['created_at']).strftime("%Y-%m-%d %H:%M")
                })

        # Add assessment completion activities
        if user in self.feedback_history:
            for feedback_entry in self.feedback_history[user].values():
                feedback_info = feedback_entry['feedback']
                activities.append({
                    'type': 'Assessment Completed',
                    'description': f"Completed assessment: {feedback_entry['question_set']}",
                    'date': datetime.fromisoformat(feedback_entry['created_at']).strftime("%Y-%m-%d %H:%M"),
                    'score': feedback_info.get('overall_score', 0)
                })

        # Sort by date (most recent first) and limit results
        activities.sort(key=lambda x: x['date'], reverse=True)

        return activities[:limit]

    def get_user_preferences(self, user: str) -> Dict[str, Any]:
        """
        Retrieve user preferences and settings.

        Args:
            user (str): User identifier.

        Returns:
            dict: User preferences dictionary, empty if user not found.
        """
        if user in self.user_data:
            return self.user_data[user].get('preferences', {})
        return {}

    def set_user_preference(self, user: str, key: str, value: Any):
        """
        Set or update a user preference.

        Args:
            user (str): User identifier.
            key (str): Preference key.
            value: Preference value (any type).
        """
        if user not in self.user_data:
            self.user_data[user] = {'preferences': {}}

        if 'preferences' not in self.user_data[user]:
            self.user_data[user]['preferences'] = {}

        self.user_data[user]['preferences'][key] = value
        self._save_session_data()

    def get_user_stats(self, user: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive user statistics.

        Args:
            user (str): User identifier.

        Returns:
            dict: User statistics including membership info, activity counts, etc.
        """
        if user not in self.user_data:
            return {}

        user_info = self.user_data[user]

        stats = {
            'member_since': user_info.get('created_at', 'Unknown'),
            'total_sessions': user_info.get('total_sessions', 0),
            'last_login': user_info.get('last_login', 'Never'),
            'content_generated': len(self.content_history.get(user, {})),
            'assessments_taken': len(self.feedback_history.get(user, {})),
            'questions_generated': len(self.question_history.get(user, {}))
        }

        return stats
    
    def cleanup_old_data(self, days_old: int = 30):
        """
        Clean up old session data and maintain storage efficiency.

        Removes sessions inactive for more than the specified days and
        trims content histories to maintain reasonable storage limits.

        Args:
            days_old (int): Age threshold in days for data removal. Defaults to 30.

        Returns:
            int: Number of old sessions removed.
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_str = cutoff_date.isoformat()

        # Remove old inactive sessions
        sessions_to_remove = []
        for session_id, session_data in self.sessions.items():
            if session_data['last_active'] < cutoff_str:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.sessions[session_id]

        # Trim content histories (keep last 20 per user)
        for user in self.content_history:
            user_content = self.content_history[user]
            if len(user_content) > 20:
                sorted_content = sorted(
                    user_content.items(),
                    key=lambda x: x[1]['created_at']
                )
                for old_id, _ in sorted_content[:-20]:
                    del user_content[old_id]

        self._save_session_data()
        return len(sessions_to_remove)

    def export_user_data(self, user: str) -> Dict[str, Any]:
        """
        Export all data for a user (for backup or migration).

        Args:
            user (str): User identifier.

        Returns:
            dict: Complete user data export including all histories and metadata.
        """
        user_export = {
            'user_info': self.user_data.get(user, {}),
            'content_history': dict(self.content_history.get(user, {})),
            'question_history': dict(self.question_history.get(user, {})),
            'feedback_history': dict(self.feedback_history.get(user, {})),
            'export_timestamp': datetime.now().isoformat()
        }

        return user_export

    def import_user_data(self, user: str, import_data: Dict[str, Any]):
        """
        Import user data from an export (for restore or migration).

        Args:
            user (str): User identifier.
            import_data (dict): User data export to import.
        """
        if 'user_info' in import_data:
            self.user_data[user] = import_data['user_info']

        if 'content_history' in import_data:
            self.content_history[user] = import_data['content_history']

        if 'question_history' in import_data:
            self.question_history[user] = import_data['question_history']

        if 'feedback_history' in import_data:
            self.feedback_history[user] = import_data['feedback_history']

        self._save_session_data()
