import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import numpy as np
from google import genai
from google.genai import types

class InformationRetrieval:

    """
    Information Retrieval system for the tutoring platform
    Provides search capabilities and knowledge base access using IR techniques
    
    """
    
    def __init__(self):
        # Using Google Gemini 2.5 Flash for free AI-powered information retrieval
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Initialize TF-IDF vectorizer for document similarity
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.8,
            min_df=2
        )
        
        # Initialize LSA for semantic similarity  
        self.lsa = TruncatedSVD(n_components=50, random_state=42)
        
        # Knowledge base storage
        self.knowledge_base = {}
        self.document_vectors = None
        self.document_ids = []
        
        # Initialize with educational knowledge base
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with educational content"""
        
        # Educational content categories and topics
        educational_content = {
            'computer_science': {
                'python_programming': """
                Python is a high-level, interpreted programming language known for its simplicity and readability. 
                It supports multiple programming paradigms including procedural, object-oriented, and functional programming.
                Key concepts include variables, data types, control structures, functions, classes, and modules.
                Python is widely used in web development, data science, artificial intelligence, automation, and scientific computing.
                Important libraries include NumPy for numerical computing, Pandas for data manipulation, and Matplotlib for visualization.
                """,
                
                'data_structures': """
                Data structures are ways of organizing and storing data to enable efficient access and modification.
                Common data structures include arrays, linked lists, stacks, queues, trees, and hash tables.
                Arrays provide constant-time access but fixed size. Linked lists offer dynamic sizing but linear access time.
                Stacks follow Last-In-First-Out (LIFO) principle, while queues follow First-In-First-Out (FIFO).
                Trees are hierarchical structures useful for searching and sorting. Hash tables provide average constant-time operations.
                """,
                
                'algorithms': """
                Algorithms are step-by-step procedures for solving computational problems.
                Algorithm analysis involves studying time and space complexity using Big O notation.
                Sorting algorithms include bubble sort, selection sort, insertion sort, merge sort, and quicksort.
                Searching algorithms include linear search and binary search.
                Graph algorithms include depth-first search, breadth-first search, and shortest path algorithms.
                Dynamic programming optimizes recursive problems by storing intermediate results.
                """
            },
            
            'mathematics': {
                'calculus': """
                Calculus is the mathematical study of continuous change and motion.
                Differential calculus deals with derivatives, which measure rates of change.
                Integral calculus deals with integrals, which measure accumulation of quantities.
                The fundamental theorem of calculus connects derivatives and integrals.
                Applications include optimization, physics, economics, and engineering.
                Key concepts include limits, continuity, differentiation rules, and integration techniques.
                """,
                
                'linear_algebra': """
                Linear algebra studies vector spaces and linear transformations between them.
                Vectors represent quantities with magnitude and direction.
                Matrices are rectangular arrays of numbers used to represent linear transformations.
                Systems of linear equations can be solved using matrix operations.
                Eigenvalues and eigenvectors reveal important properties of linear transformations.
                Applications include computer graphics, machine learning, and quantum mechanics.
                """,
                
                'statistics': """
                Statistics is the science of collecting, analyzing, and interpreting data.
                Descriptive statistics summarize data using measures like mean, median, mode, and standard deviation.
                Probability theory provides the foundation for statistical inference.
                Hypothesis testing helps determine if observed effects are statistically significant.
                Regression analysis models relationships between variables.
                Applications include quality control, market research, and scientific research.
                """
            },
            
            'science': {
                'physics': """
                Physics is the fundamental science that seeks to understand how the universe behaves.
                Classical mechanics describes motion of objects from atoms to galaxies.
                Thermodynamics studies heat, temperature, and energy transfer.
                Electromagnetism deals with electric and magnetic phenomena.
                Quantum mechanics describes behavior at atomic and subatomic scales.
                Relativity theory describes space, time, and gravity at high speeds and large scales.
                """,
                
                'chemistry': """
                Chemistry is the science of matter and the changes it undergoes.
                Atomic structure involves protons, neutrons, and electrons.
                Chemical bonding includes ionic, covalent, and metallic bonds.
                The periodic table organizes elements by atomic number and properties.
                Chemical reactions involve breaking and forming bonds with energy changes.
                Organic chemistry focuses on carbon-based compounds essential to life.
                """,
                
                'biology': """
                Biology is the study of living organisms and their interactions.
                Cell theory states that all life consists of cells, the basic unit of life.
                Evolution by natural selection explains the diversity and unity of life.
                Genetics studies heredity and variation in organisms.
                Ecology examines relationships between organisms and their environment.
                Molecular biology investigates biological processes at the molecular level.
                """
            },
            
            'history': {
                'world_history': """
                World history encompasses the development of human civilization across cultures and time periods.
                Ancient civilizations like Mesopotamia, Egypt, Greece, and Rome laid foundations for modern society.
                The Middle Ages saw the rise of feudalism, trade networks, and religious institutions.
                The Renaissance marked a rebirth of learning, art, and scientific inquiry.
                The Industrial Revolution transformed society through mechanization and urbanization.
                The 20th century featured world wars, technological advancement, and globalization.
                """,
                
                'american_history': """
                American history traces the development of the United States from colonial times to present.
                Colonial period involved European settlement and conflict with Native Americans.
                The American Revolution established independence and democratic principles.
                The Constitution created a federal system with separation of powers.
                The Civil War resolved conflicts over slavery and federal authority.
                The 20th century saw America emerge as a global superpower through two world wars.
                """
            }
        }
        
        # Flatten and store content
        
        doc_id = 0
        for subject, topics in educational_content.items():
            for topic, content in topics.items():
                self.knowledge_base[doc_id] = {
                    'id': doc_id,
                    'subject': subject,
                    'topic': topic,
                    'title': f"{topic.replace('_', ' ').title()}",
                    'content': content.strip(),
                    'type': 'educational_content',
                    'created_at': datetime.now().isoformat()
                }
                doc_id += 1
        
        # Build document vectors for similarity search
        
        self._build_document_vectors()
    
    def _build_document_vectors(self):
        """Build TF-IDF vectors for all documents in knowledge base"""
        if not self.knowledge_base:
            return
        
        documents = []
        self.document_ids = []
        
        for doc_id, doc in self.knowledge_base.items():
            # Combine title and content for better matching
            text = f"{doc['title']} {doc['content']}"
            documents.append(text)
            self.document_ids.append(doc_id)
        
        # Create TF-IDF vectors
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Apply LSA for dimensionality reduction and semantic similarity
            self.document_vectors = self.lsa.fit_transform(tfidf_matrix)
            
        except Exception as e:
            print(f"Error building document vectors: {e}")
            self.document_vectors = None
    
    def search(self, query: str, search_type: str = "General", max_results: int = 5) -> List[Dict[str, Any]]:
        
        """
        Search the knowledge base using IR techniques
        
        Args:
            query (str): Search query
            search_type (str): Type of search (General, Definitions, Examples, Tutorials)
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict]: Search results with relevance scores
        """
        
        try:
            # Enhance query based on search type
            enhanced_query = self._enhance_query(query, search_type)
            
            # Perform vector-based search if vectors are available
            vector_results = []
            if self.document_vectors is not None:
                vector_results = self._vector_search(enhanced_query, max_results)
            
            # Perform keyword-based search as fallback
            keyword_results = self._keyword_search(enhanced_query, max_results)
            
            # Combine and rank results
            combined_results = self._combine_search_results(vector_results, keyword_results)
            
            # If no local results, try AI-generated content
            if not combined_results:
                ai_results = self._ai_generated_search(query, search_type, max_results)
                combined_results.extend(ai_results)
            
            return combined_results[:max_results]
            
        except Exception as e:
            print(f"Search error: {e}")
            return self._fallback_search(query, max_results)
    
    def _enhance_query(self, query: str, search_type: str) -> str:
        """Enhance query based on search type"""
        query = query.lower().strip()
        
        if search_type == "Definitions":
            query += " definition meaning concept explanation"
        elif search_type == "Examples":
            query += " example application practical use case"
        elif search_type == "Tutorials":
            query += " tutorial guide how-to step-by-step instructions"
        
        return query
    
    def _vector_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform vector-based semantic search"""
        try:
            # Transform query to same vector space
            
            query_tfidf = self.vectorizer.transform([query])
            query_vector = self.lsa.transform(query_tfidf)
            
            # Calculate cosine similarities
            
            similarities = cosine_similarity(query_vector, self.document_vectors)[0]
            
            # Get top results
            
            top_indices = np.argsort(similarities)[::-1][:max_results * 2]  # Get more for filtering
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    doc_id = self.document_ids[idx]
                    doc = self.knowledge_base[doc_id]
                    
                    results.append({
                        'id': doc_id,
                        'title': doc['title'],
                        'content': doc['content'],
                        'subject': doc['subject'],
                        'topic': doc['topic'],
                        'source': 'Knowledge Base',
                        'relevance_score': float(similarities[idx]),
                        'search_method': 'vector_similarity',
                        'related_topics': self._extract_related_topics(doc['content'])
                    })
            
            return results
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    def _keyword_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform keyword-based search"""
        query_terms = set(query.lower().split())
        results = []
        
        for doc_id, doc in self.knowledge_base.items():
            content_lower = f"{doc['title']} {doc['content']}".lower()
            content_terms = set(content_lower.split())
            
            # Calculate keyword overlap
            overlap = len(query_terms.intersection(content_terms))
            total_terms = len(query_terms)
            
            if overlap > 0:
                relevance_score = overlap / total_terms
                
                # Boost score for title matches
                title_lower = doc['title'].lower()
                if any(term in title_lower for term in query_terms):
                    relevance_score *= 1.5
                
                results.append({
                    'id': doc_id,
                    'title': doc['title'],
                    'content': doc['content'],
                    'subject': doc['subject'],
                    'topic': doc['topic'],
                    'source': 'Knowledge Base',
                    'relevance_score': relevance_score,
                    'search_method': 'keyword_match',
                    'related_topics': self._extract_related_topics(doc['content'])
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:max_results]
    
    def _combine_search_results(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """Combine and deduplicate search results"""
        seen_ids = set()
        combined_results = []
        
        # Add vector results first (usually higher quality)
        for result in vector_results:
            if result['id'] not in seen_ids:
                combined_results.append(result)
                seen_ids.add(result['id'])
        
        # Add keyword results that weren't already included
        for result in keyword_results:
            if result['id'] not in seen_ids:
                combined_results.append(result)
                seen_ids.add(result['id'])
        
        # Sort by combined relevance score
        for result in combined_results:
            if result['search_method'] == 'vector_similarity':
                result['final_score'] = result['relevance_score'] * 1.2  # Prefer semantic results
            else:
                result['final_score'] = result['relevance_score']
        
        combined_results.sort(key=lambda x: x['final_score'], reverse=True)
        return combined_results
    
    def _ai_generated_search(self, query: str, search_type: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate search results using AI when no local matches found"""
        try:
            system_prompt = f"""You are an educational content expert. Generate helpful educational content based on the search query.
            
            Search Type: {search_type}
            
            Return response in JSON format:
            {{
                "results": [
                    {{
                        "title": "Content Title",
                        "content": "Detailed educational content",
                        "subject": "Subject area",
                        "topic": "Specific topic",
                        "related_topics": ["topic1", "topic2", "topic3"]
                    }}
                ]
            }}
            
            Generate {min(max_results, 3)} high-quality educational results."""
            
            user_prompt = f"Create educational content for the search query: {query}"
            
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
                
                ai_data = json.loads(text)
            else:
                ai_data = {}
            
            results = []
            for i, result in enumerate(ai_data.get('results', [])):
                results.append({
                    'id': f'ai_generated_{i}',
                    'title': result.get('title', 'AI Generated Content'),
                    'content': result.get('content', ''),
                    'subject': result.get('subject', 'General'),
                    'topic': result.get('topic', query),
                    'source': 'AI Generated',
                    'relevance_score': 0.8,  # High relevance for AI-generated content
                    'search_method': 'ai_generation',
                    'related_topics': result.get('related_topics', [])
                })
            
            return results
            
        except Exception as e:
            print(f"AI search error: {e}")
            return []
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback search when all other methods fail"""
        # Simple fallback based on available documents
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in list(self.knowledge_base.items())[:max_results]:
            content = f"{doc['title']} {doc['content']}"
            
            # Simple relevance check
            if any(word in content.lower() for word in query_lower.split()):
                results.append({
                    'id': doc_id,
                    'title': doc['title'],
                    'content': doc['content'][:500] + "...",  # Truncate for fallback
                    'subject': doc['subject'],
                    'topic': doc['topic'],
                    'source': 'Knowledge Base (Fallback)',
                    'relevance_score': 0.5,
                    'search_method': 'fallback',
                    'related_topics': []
                })
        
        if not results:
            # Last resort: return a helpful message
            results.append({
                'id': 'no_results',
                'title': f'Search Results for "{query}"',
                'content': f'No specific content found for "{query}". Try using different keywords or browse the available topics.',
                'subject': 'General',
                'topic': 'Search Help',
                'source': 'System Message',
                'relevance_score': 0.1,
                'search_method': 'fallback',
                'related_topics': ['search tips', 'available topics', 'help']
            })
        
        return results
    
    def _extract_related_topics(self, content: str) -> List[str]:
        """Extract related topics from content"""
        # Simple topic extraction based on common educational terms
        common_topics = {
            'programming': ['python', 'java', 'javascript', 'coding', 'software', 'algorithm'],
            'mathematics': ['algebra', 'calculus', 'geometry', 'statistics', 'probability'],
            'science': ['physics', 'chemistry', 'biology', 'experiment', 'theory'],
            'history': ['civilization', 'revolution', 'war', 'culture', 'society']
        }
        
        content_lower = content.lower()
        related = []
        
        for category, keywords in common_topics.items():
            if any(keyword in content_lower for keyword in keywords):
                related.append(category)
        
        return related[:5]  # Return top 5 related topics
    
    def add_document(self, title: str, content: str, subject: str = "General", topic: str = "General") -> int:
        """Add a new document to the knowledge base"""
        doc_id = max(self.knowledge_base.keys()) + 1 if self.knowledge_base else 0
        
        self.knowledge_base[doc_id] = {
            'id': doc_id,
            'title': title,
            'content': content,
            'subject': subject,
            'topic': topic,
            'type': 'user_generated',
            'created_at': datetime.now().isoformat()
        }
        
        # Rebuild vectors to include new document
        self._build_document_vectors()
        
        return doc_id
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by ID"""
        return self.knowledge_base.get(doc_id)
    
    def get_documents_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific subject"""
        return [doc for doc in self.knowledge_base.values() if doc['subject'] == subject]
    
    def get_similar_documents(self, doc_id: int, max_results: int = 5) -> List[Dict[str, Any]]:
        """Find documents similar to a given document"""
        if doc_id not in self.knowledge_base or self.document_vectors is None:
            return []
        
        try:
            # Find index of the document
            target_idx = self.document_ids.index(doc_id)
            target_vector = self.document_vectors[target_idx].reshape(1, -1)
            
            # Calculate similarities
            similarities = cosine_similarity(target_vector, self.document_vectors)[0]
            
            # Get top similar documents (excluding itself)
            top_indices = np.argsort(similarities)[::-1][1:max_results+1]
            
            results = []
            for idx in top_indices:
                similar_doc_id = self.document_ids[idx]
                doc = self.knowledge_base[similar_doc_id]
                
                results.append({
                    'id': similar_doc_id,
                    'title': doc['title'],
                    'content': doc['content'],
                    'subject': doc['subject'],
                    'topic': doc['topic'],
                    'similarity_score': float(similarities[idx])
                })
            
            return results
            
        except Exception as e:
            print(f"Error finding similar documents: {e}")
            return []
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        # Extract terms from knowledge base titles and topics
        terms = set()
        for doc in self.knowledge_base.values():
            title_words = doc['title'].lower().split()
            topic_words = doc['topic'].replace('_', ' ').split()
            terms.update(title_words + topic_words)
        
        # Find matching terms
        matching_terms = [term for term in terms if partial_lower in term and len(term) > 2]
        
        # Sort by relevance (length and alphabetical)
        matching_terms.sort(key=lambda x: (len(x), x))
        
        return matching_terms[:10]
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        subjects = {}
        total_docs = len(self.knowledge_base)
        total_words = 0
        
        for doc in self.knowledge_base.values():
            subject = doc['subject']
            subjects[subject] = subjects.get(subject, 0) + 1
            total_words += len(doc['content'].split())
        
        return {
            'total_documents': total_docs,
            'total_words': total_words,
            'subjects': subjects,
            'avg_words_per_doc': total_words / total_docs if total_docs > 0 else 0,
            'has_vectors': self.document_vectors is not None
        }
