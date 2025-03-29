import streamlit as st
from typing import List, Dict, Any

def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension without the dot
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ""

def display_results(results: List[Dict[str, Any]]) -> None:
    """
    Display search results in a structured format
    
    Args:
        results: List of search result dictionaries
    """
    if not results:
        st.info("No matching documents found.")
        return
    
    # Display each result
    for i, result in enumerate(results):
        with st.container():
            # Document title and score
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"### {i+1}. {result['filename']}")
            with col2:
                st.markdown(f"Score: {result['score']:.2f}")
            
            # Metadata display
            if result.get('metadata'):
                # Format metadata for display
                metadata_str = ", ".join([f"{k}: {v}" for k, v in result['metadata'].items()])
                st.caption(f"Metadata: {metadata_str}")
            
            # Snippets with highlighted matches
            if result.get('snippets'):
                for snippet in result['snippets']:
                    st.markdown(snippet)
            
            st.divider()

def format_metadata(metadata: Dict) -> str:
    """
    Format metadata for display
    
    Args:
        metadata: Dictionary of metadata
        
    Returns:
        Formatted metadata string
    """
    if not metadata:
        return "No metadata available"
    
    # Format each key-value pair
    formatted = []
    for key, value in metadata.items():
        # Clean up key name
        clean_key = key.replace('_', ' ').title()
        formatted.append(f"{clean_key}: {value}")
    
    return ", ".join(formatted)
