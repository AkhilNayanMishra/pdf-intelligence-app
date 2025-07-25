# PDF Intelligence Application

## Overview
The PDF Intelligence Application is designed to extract outlines from PDF documents and perform persona-driven document intelligence analysis. It leverages advanced PDF parsing techniques and natural language processing to provide insights based on the content of the documents.

## Project Structure
```
pdf-intelligence-app
├── src
│   ├── main.py               # Entry point of the application
│   ├── pdf_extractor.py      # PDF extraction logic
│   ├── persona_analyzer.py   # Persona analysis logic
│   └── utils.py              # Utility functions
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore file
└── README.md                  # Project documentation
```

## Setup Instructions
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd pdf-intelligence-app
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Build the Docker image:**
   If you prefer to run the application in a Docker container, build the image using:
   ```
   docker build -t pdf-intelligence-app .
   ```

## Usage
To run the application, execute the following command:
```
python src/main.py
```
Make sure to provide the necessary PDF file paths and any required parameters as specified in the code.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) for PDF parsing.
- [pdfminer.six](https://pdfminersix.readthedocs.io/en/latest/) for PDF text extraction.
- [scikit-learn](https://scikit-learn.org/stable/) for cosine similarity calculations.