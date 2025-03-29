import streamlit as st
import os
import tempfile
import matplotlib.pyplot as plt
from document_processor import process_document
from search_engine import create_index, search_documents
from utils import get_file_extension, display_results
from ai_text_generator import SimpleTextGenerator

# Set page configuration
st.set_page_config(
    page_title="Document Query System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #262730;
    }
    .stButton>button {
        font-weight: bold;
    }
    .css-1wrcr25 {
        background-color: #FF4B4B !important;
    }
    .css-ocqkz7 {
        background-color: #f4f4f4 !important;
    }
    .stSidebar .block-container {
        padding-top: 2rem;
    }
    .stMarkdown a {
        color: #0068C9 !important;
    }
    /* Card-like elements */
    .document-card {
        border-radius: 5px;
        border: 1px solid #eee;
        padding: 20px;
        margin-bottom: 10px;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize text generator
text_generator = SimpleTextGenerator()

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = {}  # {doc_id: {content, filename, metadata}}
if 'index' not in st.session_state:
    st.session_state.index = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'view_document' not in st.session_state:
    st.session_state.view_document = None
if 'document_analyses' not in st.session_state:
    st.session_state.document_analyses = {}  # {doc_id: analysis_results}
if 'document_insights' not in st.session_state:
    st.session_state.document_insights = None

# App header with logo and title
col1, col2 = st.columns([1, 5])
with col1:
    st.image("generated-icon.png", width=125)
with col2:
    st.title("AI-Powered Document Query System")
    st.markdown("""
    <p style="font-size: 1.2em; margin-top: -10px;">
        Upload, analyze, and search your documents with AI-powered summarization and Q&A capabilities.
        <span style="background-color: #f0f2f6; border-radius: 4px; padding: 2px 6px; margin-left: 5px; font-size: 0.9em;">
            Supports PDF, DOCX, TXT
        </span>
    </p>
    """, unsafe_allow_html=True)

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
                        
                        # Generate AI analysis for the document
                        with st.spinner(f"Analyzing {uploaded_file.name} with AI..."):
                            analysis = text_generator.analyze_document(content, metadata)
                            st.session_state.document_analyses[doc_id] = analysis
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
                
                # Generate cross-document insights if multiple documents
                if len(st.session_state.documents) > 1:
                    status_text.text("Generating AI insights across documents...")
                    st.session_state.document_insights = text_generator.generate_insights(
                        st.session_state.documents
                    )
                
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
        
        # Calculate document statistics for visualization
        doc_sizes = {}
        doc_types = {}
        
        for doc_id, doc in st.session_state.documents.items():
            # Get document size
            doc_size = len(doc['content'])
            doc_sizes[doc['filename']] = doc_size
            
            # Get document type
            doc_type = get_file_extension(doc['filename'])
            if doc_type in doc_types:
                doc_types[doc_type] += 1
            else:
                doc_types[doc_type] = 1
        
        # Display document stats visualization
        if len(st.session_state.documents) > 1:
            st.markdown("### Document Collection Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Document count by type
                if doc_types:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    
                    # Choose colors for each document type
                    colors = {'pdf': '#FF4B4B', 'docx': '#0068C9', 'txt': '#09AB3B'}
                    
                    # Use type-specific colors or a default gray
                    type_colors = [colors.get(t, '#CCCCCC') for t in doc_types.keys()]
                    
                    ax.bar(doc_types.keys(), doc_types.values(), color=type_colors)
                    
                    ax.set_xlabel('Document Type')
                    ax.set_ylabel('Count')
                    ax.set_title('Document Types in Collection')
                    
                    # Add count labels on top of bars
                    for i, (doc_type, count) in enumerate(doc_types.items()):
                        ax.text(i, count + 0.1, str(count), ha='center')
                    
                    st.pyplot(fig)
            
            with col2:
                # Document sizes comparison (top 5 by size)
                if len(doc_sizes) > 1:
                    # Get top 5 largest documents
                    sorted_sizes = sorted(doc_sizes.items(), key=lambda x: x[1], reverse=True)[:5]
                    
                    # Create shortened names and sizes
                    names = [name[:15] + '...' if len(name) > 15 else name for name, _ in sorted_sizes]
                    sizes = [size / 1000 for _, size in sorted_sizes]  # Convert to KB for readability
                    
                    fig, ax = plt.subplots(figsize=(6, 4))
                    bars = ax.barh(names, sizes, color='#FF4B4B')
                    
                    ax.set_xlabel('Size (KB)')
                    ax.set_title('Document Sizes (Top 5)')
                    
                    # Add size labels
                    for bar in bars:
                        width = bar.get_width()
                        label_x_pos = width + 0.5
                        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.1f} KB', 
                                va='center', fontsize=9)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
            
            # Display cross-document AI insights
            if st.session_state.document_insights:
                st.markdown("### AI-Powered Cross-Document Insights")
                insights = st.session_state.document_insights
                
                with st.container():
                    st.markdown("""
                    <div style="background-color:white; border:1px solid #eee; border-radius:8px; padding:20px; 
                    margin-bottom:20px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Common themes
                    if 'common_themes' in insights and insights['common_themes']:
                        st.markdown("#### Common Themes Across Documents")
                        theme_html = ""
                        for theme in insights['common_themes']:
                            theme_html += f'<span style="background-color:#FF4B4B; color:white; padding:5px 10px; border-radius:15px; margin-right:8px; display:inline-block; margin-bottom:8px; font-weight:500;">{theme}</span>'
                        
                        st.markdown(f"""
                        <div style="margin-bottom:20px;">
                            {theme_html}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Recommendations
                    if 'recommendations' in insights and insights['recommendations']:
                        st.markdown("#### AI Recommendations")
                        for i, rec in enumerate(insights['recommendations']):
                            st.markdown(f"""
                            <div style="background-color:#f8f9fa; border-radius:5px; padding:10px; 
                            border-left:4px solid #09AB3B; margin-bottom:10px;">
                                {i+1}. {rec}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Connections between documents
                    if 'connections' in insights and insights['connections']:
                        st.markdown("#### Document Connections")
                        for conn in insights['connections']:
                            st.markdown(f"""
                            <div style="background-color:#f8f9fa; border-radius:5px; padding:10px; 
                            border-left:4px solid #0068C9; margin-bottom:10px;">
                                {conn}
                            </div>
                            """, unsafe_allow_html=True)
        
        # Display document cards
        st.markdown("### Document Details")
        
        for doc_id, doc in st.session_state.documents.items():
            with st.container():
                # Create an enhanced document card
                st.markdown("""
                <div class="document-card">
                </div>
                """, unsafe_allow_html=True)
                
                # Document title and metadata
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Document icon based on type
                    file_ext = get_file_extension(doc['filename'])
                    icon = "📄"
                    if file_ext == "pdf":
                        icon = "📕"
                    elif file_ext == "docx":
                        icon = "📘"
                    elif file_ext == "txt":
                        icon = "📝"
                    
                    st.markdown(f"### {icon} {doc['filename']}")
                
                with col2:
                    # Document size badge
                    size_kb = len(doc['content']) / 1000
                    st.markdown(f"""
                    <div style="background-color:#f0f2f6; border-radius:5px; padding:5px; 
                    text-align:center; margin-top:10px;">
                        <span style="font-size:0.8em;">Size: {size_kb:.1f} KB</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create tabs for preview, metadata, and AI analysis
                preview_tab, metadata_tab, ai_tab, qa_tab = st.tabs(["Preview", "Metadata", "AI Analysis", "Ask Questions"])
                
                with preview_tab:
                    # Display a more readable preview
                    preview = doc['content'][:800] + "..." if len(doc['content']) > 800 else doc['content']
                    # Convert newlines to <br> tags before using in the f-string
                    preview_html = preview.replace('\n', '<br>')
                    st.markdown(f"""
                    <div style="background-color:white; border:1px solid #eee; 
                    border-radius:5px; padding:15px; font-family:monospace; 
                    max-height:200px; overflow-y:auto;">
                    {preview_html}
                    </div>
                    """, unsafe_allow_html=True)
                
                with metadata_tab:
                    if 'metadata' in doc and doc['metadata']:
                        # Create a more structured metadata display
                        meta_cols = st.columns(3)
                        meta_items = list(doc['metadata'].items())
                        
                        for i, (key, value) in enumerate(meta_items):
                            # Clean up key name
                            clean_key = key.replace('_', ' ').title()
                            with meta_cols[i % 3]:
                                st.markdown(f"""
                                <div style="margin-bottom:10px;">
                                    <span style="font-size:0.9em; color:gray;">{clean_key}</span><br>
                                    <span style="font-weight:bold;">{value}</span>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No metadata available for this document")
                
                with ai_tab:
                    if doc_id in st.session_state.document_analyses:
                        analysis = st.session_state.document_analyses[doc_id]
                        
                        # Display document type prediction
                        st.markdown("#### Document Type")
                        st.markdown(f"""
                        <div style="background-color:#f8f9fa; border-radius:5px; padding:10px; margin-bottom:15px;">
                            {analysis.get('document_type', 'Unknown document type')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display document summary
                        st.markdown("#### AI-Generated Summary")
                        st.markdown(f"""
                        <div style="background-color:#f8f9fa; border-radius:5px; padding:10px; margin-bottom:15px;">
                            {analysis.get('summary', 'Summary not available')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display key topics
                        if 'key_topics' in analysis and analysis['key_topics']:
                            st.markdown("#### Key Topics")
                            topics_html = ""
                            for topic in analysis['key_topics']:
                                topics_html += f'<span style="background-color:#0068C9; color:white; padding:3px 8px; border-radius:10px; margin-right:5px; display:inline-block; margin-bottom:5px;">{topic}</span>'
                            
                            st.markdown(f"""
                            <div style="margin-bottom:15px;">
                                {topics_html}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Display reading time
                        if 'reading_time' in analysis:
                            st.markdown("#### Estimated Reading Time")
                            st.markdown(f"""
                            <div style="background-color:#f8f9fa; border-radius:5px; padding:10px; margin-bottom:15px;">
                                <span style="font-size:1.2em; font-weight:bold;">⏱️ {analysis['reading_time']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        with st.spinner("Analyzing document..."):
                            # Generate analysis if not already available
                            analysis = text_generator.analyze_document(doc['content'], doc.get('metadata', {}))
                            st.session_state.document_analyses[doc_id] = analysis
                            st.rerun()  # Refresh to show the new analysis
                
                with qa_tab:
                    st.markdown("#### Ask a Question About This Document")
                    
                    # Create a unique key for this document's question input
                    question_key = f"question_{doc_id}"
                    user_question = st.text_input("Enter your question", key=question_key)
                    
                    if st.button("Get Answer", key=f"answer_btn_{doc_id}"):
                        if user_question:
                            with st.spinner("Generating answer..."):
                                answer = text_generator.answer_question(user_question, doc['content'])
                                
                                st.markdown("#### Answer")
                                st.markdown(f"""
                                <div style="background-color:#f8f9fa; border-radius:5px; padding:15px; 
                                border-left:4px solid #0068C9; margin-top:10px;">
                                    {answer}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("Please enter a question first.")
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
        5. **Ask Questions** - Use the Q&A feature to ask questions about your documents
        
        ### Supported Features
        - Multiple document formats (PDF, DOCX, TXT)
        - Full-text search capabilities with relevance-based ranking
        - Document preview and metadata extraction
        - AI-powered document analysis and summarization
        - Natural language Q&A on document content
        - Cross-document insights and theme identification
        """)
