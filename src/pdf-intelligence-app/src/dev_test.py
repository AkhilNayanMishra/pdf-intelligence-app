# dev_test.py (Temporary testing script)
from pdf_extractor import PDFExtractor

pdf_files = [
    r"C:\Users\mishr\OneDrive\Desktop\Adobe\pdf-intelligence-app\input\E0CCG5S239.pdf",
    r"C:\Users\mishr\OneDrive\Desktop\Adobe\pdf-intelligence-app\input\E0CCG5S312.pdf",
    r"C:\Users\mishr\OneDrive\Desktop\Adobe\pdf-intelligence-app\input\E0H1CM114.pdf",
    r"C:\Users\mishr\OneDrive\Desktop\Adobe\pdf-intelligence-app\input\STEMPathwaysFlyer.pdf",
    r"C:\Users\mishr\OneDrive\Desktop\Adobe\pdf-intelligence-app\input\TOPJUMP-PARTY-INVITATION-20161003-V01.pdf"
    


]

for pdf_path in pdf_files:
    print(f"\n🔍 Processing: {os.path.basename(pdf_path)}")
    extractor = PDFExtractor(pdf_path)
    title, headings = extractor.extract_title_and_headings()

    print("Title:\n", title)
    print("Headings:")
    for h in headings:
        print(h)
