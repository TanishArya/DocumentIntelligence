# AI-Powered Document Query System 📚

The **AI-Powered Document Query System** is a Streamlit-based application that allows users to upload, analyze, and search documents using AI-powered summarization and Q&A capabilities. It supports multiple file formats, including PDF, DOCX, and TXT.

---

## Features

- **Document Upload**: Upload multiple documents in supported formats.
- **Text Extraction**: Extract text and metadata from PDF, DOCX, and TXT files.
- **AI Analysis**: Generate document summaries and insights using a lightweight AI text generator.
- **Search Functionality**: Search across uploaded documents with relevance scoring and snippet highlighting.
- **Customizable UI**: Enhanced user interface with custom CSS for better visualization.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- [Streamlit](https://streamlit.io/)
- Required Python libraries (see `requirements.txt`)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/document-query-system.git
   cd document-query-system

2. install dependencies:
   ```bash
   pip install -r requirements.txt

3. Run the application:
   ```bash
   streamlit run app.py

4. Open your browser and navigate to http://localhost:8501.

## File Structure

.
├── [app.py](http://_vscodecontentref_/0)                     # Main application file
├── [document_processor.py](http://_vscodecontentref_/1)      # Handles text extraction from documents
├── [search_engine.py](http://_vscodecontentref_/2)           # Implements search functionality
├── [ai_text_generator.py](http://_vscodecontentref_/3)       # AI-based text summarization and insights
├── [utils.py](http://_vscodecontentref_/4)                   # Utility functions for file handling and display
├── [requirements.txt](http://_vscodecontentref_/5)           # Python dependencies
└── README.md                  # Project documentation

## Usage

1. Upload Documents:

- Use the sidebar to upload PDF, DOCX, or TXT files.
- Click the "Process Documents" button to extract text and metadata.

2. Search Documents:

- Enter a search query in the search bar.
- View the search results with relevance scores and   highlighted snippets.

3. Analyze Documents:

- AI-generated summaries and insights are displayed for each document.
4. Clear Documents:

- Use the "Clear All Documents" button in the sidebar to reset the session.

## Supported File Formats

- PDF: Extracts text and metadata using PyPDF2.
- DOCX: Extracts text, metadata, and table content using - python-docx.
- TXT: Reads plain text files with encoding support.

## Code Overview

1. app.py

- The main application file that initializes the Streamlit app.
- Handles file uploads, document processing, and search functionality.
- Displays results and insights in the UI.

2. document_processor.py

- Contains functions to process and extract text from PDF, DOCX, and TXT files.
- Includes metadata extraction and text cleaning.

3. search_engine.py

- Implements the search functionality.
- Preprocesses text, creates an inverted index, and ranks documents based on query relevance.
- Extracts and highlights relevant snippets from documents.

4. ai_text_generator.py

- Simulates AI-powered text generation and summarization.
- Provides document summaries, insights, and answers to user queries.

5. utils.py
- Utility functions for file handling and displaying results.
- Includes functions to extract file extensions and format metadata.

## Troubleshooting

1. No Search Results:

- Ensure documents are processed before searching.
- Check the debug logs for query tokens and index creation.

2. Unsupported File Format:

- Only PDF, DOCX, and TXT files are supported.

3. Application Errors:

- Verify that all dependencies are installed.
- Check the terminal for error logs.

## Dependencies

The project uses the following Python libraries:

- streamlit
- PyPDF2
- python-docx
- nltk
- matplotlib


## Acknowledgments

- Streamlit for the web application framework.
- NLTK for natural language processing.
- PyPDF2 and python-docx for document processing.

