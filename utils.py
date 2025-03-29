import streamlit as st
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import re

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
    Display search results in a structured format with enhanced visualization
    
    Args:
        results: List of search result dictionaries
    """
    if not results:
        st.info("No matching documents found.")
        return
    
    # Summary section
    st.subheader("📊 Results Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        # Create a bar chart of result scores
        if len(results) > 1:
            fig, ax = plt.subplots(figsize=(10, 5))
            filenames = [f"{result['filename'][:15]}..." if len(result['filename']) > 15 else result['filename'] for result in results]
            scores = [result['score'] for result in results]
            
            bars = ax.barh(filenames, scores, color='#FF4B4B')
            ax.set_xlabel('Relevance Score')
            ax.set_title('Document Relevance')
            
            # Add values on bars
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width if width > 0 else 0
                ax.text(label_x_pos + 0.01, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                        va='center', color='black', fontsize=9)
                
            plt.tight_layout()
            st.pyplot(fig)
    
    with col2:
        # Document types summary
        doc_types = {}
        for result in results:
            ext = get_file_extension(result['filename'])
            if ext in doc_types:
                doc_types[ext] += 1
            else:
                doc_types[ext] = 1
        
        if doc_types:
            st.markdown("### Document Types")
            for doc_type, count in doc_types.items():
                icon = "📄"
                if doc_type == "pdf":
                    icon = "📕"
                elif doc_type == "docx":
                    icon = "📘"
                elif doc_type == "txt":
                    icon = "📝"
                
                st.markdown(f"{icon} **{doc_type.upper()}**: {count} document(s)")
    
    # Display each result with enhanced styling
    st.markdown("---")
    st.subheader("📑 Detailed Results")
    
    for i, result in enumerate(results):
        with st.container():
            # Create a card-like container with border
            st.markdown(f"""
            <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
            </div>
            """, unsafe_allow_html=True)
            
            # Document title and score with colored badge
            score = result['score']
            score_color = "#09AB3B" if score > 0.8 else "#FFA500" if score > 0.5 else "#FF4B4B"
            
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"### {i+1}. {result['filename']}")
            with col2:
                st.markdown(f"""
                <div style="background-color:{score_color}; color:white; padding:2px 8px; 
                border-radius:10px; text-align:center; font-weight:bold; width:80px;">
                {score:.2f}
                </div>
                """, unsafe_allow_html=True)
            
            # Metadata display with enhanced formatting
            if result.get('metadata'):
                st.markdown("#### Document Information")
                metadata = result.get('metadata', {})
                
                # Formatted metadata section
                cols = st.columns(3)
                meta_items = list(metadata.items())
                
                for j, (key, value) in enumerate(meta_items):
                    # Clean up key name
                    clean_key = key.replace('_', ' ').title()
                    with cols[j % 3]:
                        st.markdown(f"**{clean_key}**: {value}")
            
            # Snippets with enhanced highlighting
            if result.get('snippets'):
                st.markdown("#### Matching Content")
                
                for snippet in result['snippets']:
                    # Replace standard markdown bold with highlighted text
                    snippet = re.sub(r'\*\*(.*?)\*\*', r'<mark style="background-color:#FFFF00; padding:0px 2px">\1</mark>', snippet)
                    st.markdown(f'<div style="border-left:3px solid #FF4B4B; padding-left:10px;">{snippet}</div>', unsafe_allow_html=True)
            
            # Optional: Add a "View Full Document" button (placeholder for future functionality)
            if st.button(f"View Full Document: {result['filename']}", key=f"view_doc_{i}"):
                st.info(f"Viewing functionality for {result['filename']} will be implemented in a future update.")
            
            st.markdown("---")

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
