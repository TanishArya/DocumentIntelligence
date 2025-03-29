import random
import re
from typing import List, Dict, Any, Optional

class SimpleTextGenerator:
    """
    A lightweight text generation and summarization system that simulates
    GPT-like capabilities without requiring the actual model.
    """
    
    def __init__(self):
        # Common vocabulary and phrases for document analysis
        self.vocab = {
            "document_types": [
                "This document appears to be a", 
                "Based on the content, this is a",
                "The text suggests this is a",
                "This content is characteristic of a"
            ],
            "document_categories": [
                "technical report", "research paper", "business memo", 
                "article", "academic publication", "manual", "guide",
                "analysis", "case study", "review"
            ],
            "summarize_start": [
                "In summary, this document discusses", 
                "The main points of this document are",
                "Key takeaways from this text include",
                "This document primarily focuses on",
                "The core content of this text revolves around"
            ],
            "qa_prefixes": [
                "Based on the document content,", 
                "According to the text,",
                "The document suggests that",
                "From analyzing the content,"
            ],
            "transitions": [
                "Additionally,", "Furthermore,", "Moreover,", 
                "Also,", "In addition,", "What's more,"
            ]
        }
    
    def _extract_key_phrases(self, text: str, count: int = 5) -> List[str]:
        """Extract potentially important phrases from the text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Simple extraction based on sentence boundaries and common patterns
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Select sentences that might contain key information
        candidates = []
        for sentence in sentences:
            # Prioritize sentences with potential key indicators
            if (len(sentence.split()) > 5 and len(sentence.split()) < 25 and
                any(kw in sentence.lower() for kw in 
                    ["important", "significant", "key", "main", "primary", 
                     "essential", "critical", "fundamental", "crucial"])):
                candidates.append(sentence)
        
        # If we don't have enough candidates, add some sentences based on position
        if len(candidates) < count:
            # Add first sentence (often contains topic information)
            if sentences and sentences[0] not in candidates:
                candidates.append(sentences[0])
            
            # Add some sentences from the middle
            mid_point = len(sentences) // 2
            if len(sentences) > mid_point and sentences[mid_point] not in candidates:
                candidates.append(sentences[mid_point])
            
            # Add some from positions likely to contain conclusions
            if len(sentences) > 3:
                for i in range(max(0, len(sentences) - 3), len(sentences)):
                    if sentences[i] not in candidates:
                        candidates.append(sentences[i])
                        if len(candidates) >= count:
                            break
        
        # Return up to the requested number of candidates
        return candidates[:min(count, len(candidates))]
    
    def _get_common_terms(self, text: str, count: int = 8) -> List[str]:
        """Extract frequently occurring non-stopword terms"""
        # Simple stopwords list
        stopwords = set(["the", "and", "a", "an", "in", "to", "for", "of", "on", 
                         "with", "by", "at", "from", "as", "is", "are", "was", 
                         "were", "be", "been", "being", "have", "has", "had", 
                         "do", "does", "did", "but", "or", "not", "this", "that",
                         "these", "those", "it", "they", "them", "their", "its"])
        
        # Tokenize and count terms
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        word_counts = {}
        
        for word in words:
            if word not in stopwords:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:count]]
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of the provided text
        
        Args:
            text: The document text to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Generated summary text
        """
        if not text or len(text) < 50:
            return "The provided text is too short to generate a meaningful summary."
        
        # Extract key phrases and terms
        key_phrases = self._extract_key_phrases(text)
        common_terms = self._get_common_terms(text)
        
        # Construct a summary
        summary_parts = []
        
        # Start with an introduction
        intro = random.choice(self.vocab["summarize_start"])
        topic_terms = ", ".join(common_terms[:3])
        summary_parts.append(f"{intro} {topic_terms}.")
        
        # Add key points
        for i, phrase in enumerate(key_phrases[:3]):
            if i > 0:
                transition = random.choice(self.vocab["transitions"])
                summary_parts.append(f"{transition} {phrase}")
            else:
                summary_parts.append(phrase)
        
        # Combine and limit length
        summary = " ".join(summary_parts)
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
            
        return summary
    
    def analyze_document(self, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze document content and metadata to provide insights
        
        Args:
            content: Document text content
            metadata: Optional document metadata
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {}
        
        # Document type prediction
        doc_type_prefix = random.choice(self.vocab["document_types"])
        doc_category = random.choice(self.vocab["document_categories"])
        
        # Use metadata if available to improve the prediction
        if metadata and isinstance(metadata, dict):
            title = metadata.get("Title", "")
            # Check if title is a string before calling lower()
            if title and isinstance(title, str) and "manual" in title.lower():
                doc_category = "technical manual"
            # Check if metadata has Author and Title keys with non-empty values
            elif metadata.get("Author") and metadata.get("Title"):
                doc_category = "academic paper"
        
        analysis["document_type"] = f"{doc_type_prefix} {doc_category}."
        
        # Generate a summary
        analysis["summary"] = self.generate_summary(content)
        
        # Extract key topics
        analysis["key_topics"] = self._get_common_terms(content, 5)
        
        # Estimate reading time (average reading speed of 200 words per minute)
        word_count = len(content.split())
        reading_minutes = max(1, round(word_count / 200))
        analysis["reading_time"] = f"{reading_minutes} minute{'s' if reading_minutes != 1 else ''}"
        
        return analysis
    
    def answer_question(self, question: str, document_content: str) -> str:
        """
        Generate an answer to a question based on document content
        
        Args:
            question: The question to answer
            document_content: The document text to reference
            
        Returns:
            Generated answer text
        """
        if not question or not document_content:
            return "Unable to generate an answer. Please provide both a question and document content."
        
        # Extract relevant sentences that might contain the answer
        sentences = re.split(r'(?<=[.!?])\s+', document_content)
        
        # Simple keyword matching to find relevant sentences
        question_keywords = set(re.findall(r'\b[a-zA-Z]{3,}\b', question.lower()))
        
        relevant_sentences = []
        for sentence in sentences:
            sentence_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower()))
            # Calculate overlap between question keywords and sentence
            overlap = len(question_keywords.intersection(sentence_words))
            if overlap > 0:
                relevant_sentences.append((sentence, overlap))
        
        # Sort by relevance
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Construct an answer
        if relevant_sentences:
            # Start with a prefix
            answer_prefix = random.choice(self.vocab["qa_prefixes"])
            
            # Use the most relevant sentences (up to 3)
            answer_content = " ".join([s[0] for s in relevant_sentences[:3]])
            
            return f"{answer_prefix} {answer_content}"
        else:
            return "Based on the document content, I couldn't find specific information to answer this question."
    
    def generate_insights(self, documents: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate insights across multiple documents
        
        Args:
            documents: Dictionary of document objects
            
        Returns:
            Dictionary of insights
        """
        insights = {
            "common_themes": [],
            "recommendations": [],
            "connections": []
        }
        
        if not documents:
            return insights
        
        # Collect common terms across documents
        all_terms = []
        for doc_id, doc in documents.items():
            content = doc.get("content", "")
            terms = self._get_common_terms(content, 10)
            all_terms.extend(terms)
        
        # Count term frequencies
        term_counts = {}
        for term in all_terms:
            term_counts[term] = term_counts.get(term, 0) + 1
        
        # Sort by frequency
        common_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Extract common themes
        insights["common_themes"] = [term for term, count in common_terms[:5] if count > 1]
        
        # Generate recommendations
        if insights["common_themes"]:
            recommendations = []
            
            if len(insights["common_themes"]) >= 2:
                recommendations.append(
                    f"Consider exploring the relationship between {insights['common_themes'][0]} and {insights['common_themes'][1]}."
                )
            
            if insights["common_themes"]:
                recommendations.append(
                    f"Documents frequently mention {insights['common_themes'][0]}, which may be a key area for further research."
                )
                
            recommendations.append(
                "The analysis suggests potential connections between multiple topics that could be examined in more detail."
            )
            
            insights["recommendations"] = recommendations
            
            # Generate connections
            if len(documents) > 1:
                doc_names = [doc["filename"] for _, doc in documents.items()]
                insights["connections"] = [
                    f"Both {doc_names[0]} and {doc_names[1]} address similar themes.",
                    f"Consider cross-referencing information between documents to get a more complete understanding."
                ]
        
        return insights