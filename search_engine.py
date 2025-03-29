from typing import Dict, List, Any, Tuple
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download necessary NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Initialize stemmer and stopwords
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text: str) -> List[str]:
    """
    Preprocess text for indexing or searching
    
    Args:
        text: Raw text content
        
    Returns:
        List of preprocessed tokens
    """
    # Tokenize
    tokens = word_tokenize(text.lower())
    
    # Remove punctuation and non-alphabetic tokens
    tokens = [token for token in tokens if token.isalpha()]
    
    # Remove stopwords
    tokens = [token for token in tokens if token not in stop_words]
    
    # Stem tokens
    tokens = [stemmer.stem(token) for token in tokens]
    
    return tokens

def create_index(documents: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Create a search index from the documents
    
    Args:
        documents: Dictionary of document objects
        
    Returns:
        Index mapping terms to documents with term frequency
    """
    index = {}  # {term: {doc_id: frequency}}
    
    # Calculate document frequencies
    for doc_id, doc in documents.items():
        content = doc['content']
        tokens = preprocess_text(content)
        
        # Count term frequency
        term_freq = {}
        for token in tokens:
            if token in term_freq:
                term_freq[token] += 1
            else:
                term_freq[token] = 1
        
        # Add to index with normalized frequency
        max_freq = max(term_freq.values()) if term_freq else 1
        for token, freq in term_freq.items():
            if token not in index:
                index[token] = {}
            
            # Normalize term frequency
            index[token][doc_id] = freq / max_freq
    
    return index

def search_documents(query: str, index: Dict[str, Dict[str, float]], 
                     documents: Dict[str, Dict[str, Any]], max_results: int = 10) -> List[Dict]:
    """
    Search for documents matching the query
    
    Args:
        query: User search query
        index: Search index
        documents: Dictionary of document objects
        max_results: Maximum number of results to return
        
    Returns:
        List of search result dictionaries
    """
    # Process query
    query_tokens = preprocess_text(query)
    
    if not query_tokens:
        return []
    
    # Calculate query vector
    query_vector = {token: 1 for token in query_tokens}
    
    # Score documents
    scores = {}
    for token in query_tokens:
        if token in index:
            for doc_id, term_weight in index[token].items():
                if doc_id not in scores:
                    scores[doc_id] = 0
                scores[doc_id] += term_weight
    
    # Sort by score
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Format search results
    results = []
    for doc_id, score in ranked_results[:max_results]:
        doc = documents[doc_id]
        filename = doc['filename']
        content = doc['content']
        
        # Find context for matches (extract snippets around matching terms)
        snippets = extract_snippets(content, query_tokens, 3, 200)
        
        results.append({
            'doc_id': doc_id,
            'filename': filename,
            'score': score,
            'snippets': snippets,
            'metadata': doc.get('metadata', {})
        })
    
    return results

def extract_snippets(content: str, query_terms: List[str], num_snippets: int = 3, 
                     max_length: int = 200) -> List[str]:
    """
    Extract snippets from content that contain query terms
    
    Args:
        content: Document content
        query_terms: Preprocessed query terms
        num_snippets: Number of snippets to extract
        max_length: Maximum length of each snippet
        
    Returns:
        List of text snippets
    """
    # Get original form query terms for matching
    # (since content isn't stemmed yet)
    original_terms = []
    for term in query_terms:
        # Get first 3 characters of the stemmed term to find potential matches
        # This is an approximation since we can't reverse stemming
        prefix = term[:3] if len(term) > 3 else term
        pattern = r'\b' + prefix + r'[a-zA-Z]*\b'
        matches = re.findall(pattern, content.lower())
        original_terms.extend(matches)
    
    original_terms = list(set(original_terms))  # Remove duplicates
    
    # If no terms matched, return empty snippets
    if not original_terms:
        # Just return the beginning of the document
        return [content[:max_length] + "..."]
    
    # Split content into sentences
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    # Find sentences with matching terms
    matching_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(term in sentence_lower for term in original_terms):
            matching_sentences.append(sentence)
    
    # If no matching sentences, return the beginning of the document
    if not matching_sentences:
        return [content[:max_length] + "..."]
    
    # Select top snippets
    snippets = []
    for i, sentence in enumerate(matching_sentences[:num_snippets]):
        # Highlight matching terms
        highlighted = sentence
        for term in original_terms:
            # Case insensitive replacement with highlighting
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted = pattern.sub(f"**{term}**", highlighted)
        
        # Truncate if too long
        if len(highlighted) > max_length:
            # Find a good breaking point
            break_point = highlighted.rfind(' ', max_length//2, max_length)
            if break_point == -1:
                break_point = max_length
            
            highlighted = highlighted[:break_point] + "..."
            
        snippets.append(highlighted)
    
    return snippets
