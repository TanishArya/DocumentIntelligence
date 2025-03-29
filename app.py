import streamlit as st
import os
import tempfile
from document_processor import process_document
from search_engine import create_index, search_documents
from utils import get_file_extension, display_results

# Set page configuration
st.set_page_config(
    page_title="Document Query System",
    page_icon="📑",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = {}  # {doc_id: {content, filename, metadata}}
if 'index' not in st.session_state:
    st.session_state.index = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# App title and description
st.title("Document Query System")
st.markdown("""
Upload your documents and search through them effortlessly.
Supported formats: PDF, DOCX, TXT
""")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose files", 
        type=["pdf", "txt", "docx"], 
        accept_multiple_files=True
    )
    
    if st.button("Process Documents", type="primary", use_container_width=True):
        if uploaded_files:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process each uploaded file
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save to temp file to process
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{get_file_extension(uploaded_file.name)}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_path = tmp_file.name
                
                try:
                    # Process the document and store in session state
                    doc_id = str(hash(uploaded_file.name + str(os.path.getsize(temp_file_path))))
                    content, metadata = process_document(temp_file_path, uploaded_file.name)
                    
                    if content:
                        st.session_state.documents[doc_id] = {
                            "content": content,
                            "filename": uploaded_file.name,
                            "metadata": metadata
                        }
                    else:
                        st.sidebar.error(f"Could not extract text from {uploaded_file.name}")
                        
                except Exception as e:
                    st.sidebar.error(f"Error processing {uploaded_file.name}: {str(e)}")
                
                finally:
                    # Clean up temp file
                    os.unlink(temp_file_path)
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Create or update search index
            if st.session_state.documents:
                status_text.text("Building search index...")
                st.session_state.index = create_index(st.session_state.documents)
                status_text.text("Ready to search!")
            
            # Hide progress after completion
            progress_bar.empty()
            
        else:
            st.warning("Please upload at least one document")
    
    # Display document stats
    if st.session_state.documents:
        st.success(f"{len(st.session_state.documents)} documents processed")
        
        if st.button("Clear All Documents", type="secondary", use_container_width=True):
            st.session_state.documents = {}
            st.session_state.index = None
            st.session_state.search_results = []
            st.rerun()

# Main content area
if st.session_state.documents:
    st.header("Search Your Documents")
    
    # Search query input
    query = st.text_input("Enter your search query", key="search_query")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        search_btn = st.button("Search", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.button("Clear", type="secondary", use_container_width=True)
    
    # Search functionality
    if search_btn and query:
        if st.session_state.index:
            with st.spinner("Searching..."):
                st.session_state.search_results = search_documents(
                    query, 
                    st.session_state.index, 
                    st.session_state.documents
                )
        else:
            st.error("Search index not created. Please process documents first.")
    
    # Clear search results
    if clear_btn:
        st.session_state.search_results = []
        st.rerun()
    
    # Display search results
    if st.session_state.search_results:
        st.subheader(f"Search Results for: '{query}'")
        display_results(st.session_state.search_results)
    
    # Display document list when no search is performed
    elif not query:
        st.subheader("Available Documents")
        for doc_id, doc in st.session_state.documents.items():
            with st.expander(f"📄 {doc['filename']}"):
                st.text(f"Document size: {len(doc['content'])} characters")
                
                # Display the first 500 characters of content as preview
                preview = doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content']
                st.text_area("Preview:", value=preview, height=150, disabled=True)
                
                if 'metadata' in doc and doc['metadata']:
                    st.write("Metadata:", doc['metadata'])
else:
    # Show instructions when no documents are uploaded
    st.info("Please upload documents using the sidebar to get started.")
    
    # Example usage instructions
    with st.expander("How to use this application", expanded=True):
        st.markdown("""
        ### Getting Started
        1. **Upload Documents** - Use the sidebar to upload PDF, DOCX, or TXT files
        2. **Process Documents** - Click 'Process Documents' to extract and index content
        3. **Search** - Enter keywords in the search bar to find relevant content
        4. **View Results** - Browse through search results with highlighted matches
        
        ### Supported Features
        - Multiple document formats (PDF, DOCX, TXT)
        - Full-text search capabilities
        - Document preview and metadata extraction
        - Relevance-based result ranking
        """)
