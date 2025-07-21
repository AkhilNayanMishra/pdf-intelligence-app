import argparse
import json
import os
import datetime
from pdf_extractor import PDFExtractor
from persona_analyzer import PersonaAnalyzer

def run_round_1a(args):
    """Handles the logic for Round 1A: Extracting outlines from PDFs."""
    all_results = []
    for pdf_file in args.pdf_files:
        if not os.path.exists(pdf_file):
            print(f"Warning: The file '{pdf_file}' was not found. Skipping.")
            continue

        print(f"Processing for Round 1A: '{os.path.basename(pdf_file)}'...")
        try:
            extractor = PDFExtractor(pdf_file)
            title, headings = extractor.extract_structure()
            
            output_data = {
                "source_file": os.path.basename(pdf_file),
                "title": title,
                "outline": headings
            }
            all_results.append(output_data)

            if not args.output:
                # Print readable summary if not writing to a file
                print("-" * 40)
                print(f"Title: {title}")
                print("Outline:")
                if headings:
                    for h in headings:
                        print(f"  - [{h['level']}] {h['text']} (Page: {h['page']})")
                else:
                    print("  No headings found.")
                print("-" * 40 + "\n")

        except Exception as e:
            print(f"An error occurred while processing {pdf_file}: {e}")

    if args.output and all_results:
        # Save results to a file
        save_output(args.output, all_results)

def run_round_1b(args):
    """Handles the logic for Round 1B: Persona-driven analysis."""
    if not args.output:
        print("Error: An output file must be specified for Round 1B analysis using the -o flag.")
        return

    print("Starting Round 1B: Persona-Driven Document Intelligence...")
    
    # Step 1: Extract outlines from all documents
    document_outlines = []
    print("Extracting outlines from all provided documents...")
    for pdf_file in args.pdf_files:
        if not os.path.exists(pdf_file):
            print(f"Warning: File '{pdf_file}' not found. Skipping.")
            continue
        try:
            print(f"  - Processing '{os.path.basename(pdf_file)}'")
            extractor = PDFExtractor(pdf_file)
            title, headings = extractor.extract_structure()
            document_outlines.append({
                "source_file": os.path.basename(pdf_file),
                "title": title,
                "outline": headings
            })
        except Exception as e:
            print(f"    Error extracting outline: {e}")

    if not document_outlines:
        print("Could not extract any outlines. Aborting analysis.")
        return

    # Step 2: Analyze the outlines with the PersonaAnalyzer
    print(f"\nAnalyzing {len(document_outlines)} documents for persona: '{args.persona}'...")
    try:
        analyzer = PersonaAnalyzer(args.persona, args.job)
        # CORRECTED: Unpack the two lists returned by the analyzer
        extracted_sections, subsection_analysis = analyzer.analyze_documents(document_outlines)

        # Step 3: Structure the final output as per Round 1B requirements
        final_output = {
            "metadata": {
                "input_documents": [os.path.basename(f) for f in args.pdf_files],
                "persona": args.persona,
                "job_to_be_done": args.job,
                "processing_timestamp": datetime.datetime.now().isoformat()
            },
            # Use the correct variables for the output
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }

        # Save the final JSON output
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=4)
        
        print(f"\nSuccessfully completed Round 1B analysis. Results saved to '{args.output}'.")

    except Exception as e:
        print(f"An error occurred during persona analysis: {e}")

def save_output(output_path, results):
    """Saves the output to a file, either as JSON or plain text."""
    try:
        if output_path.lower().endswith('.json'):
            with open(output_path, 'w', encoding='utf-8') as f:
                output = results[0] if len(results) == 1 else results
                json.dump(output, f, indent=4)
            print(f"\nSuccessfully saved JSON data to '{output_path}'.")
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write("-" * 40 + "\n")
                    f.write(f"Results for: {result['source_file']}\n")
                    f.write(f"Title: {result['title']}\n")
                    f.write("Outline:\n")
                    if result['outline']:
                        for h in result['outline']:
                            f.write(f"  - [{h['level']}] {h['text']} (Page: {h['page']})\n")
                    else:
                        f.write("  No headings found.\n")
                    f.write("-" * 40 + "\n\n")
            print(f"\nSuccessfully saved summary to '{output_path}'.")
    except Exception as e:
        print(f"An error occurred while writing to output file: {e}")

def main():
    """Main function to parse arguments and delegate to the correct round handler."""
    parser = argparse.ArgumentParser(
        description="A tool for PDF structural and persona-based analysis."
    )
    parser.add_argument("pdf_files", nargs='+', type=str, help="Path(s) to the input PDF file(s).")
    parser.add_argument("-o", "--output", type=str, help="Path to the output file.")
    
    # Add arguments for Round 1B
    parser.add_argument("--persona", type=str, help="Persona description for Round 1B analysis.")
    parser.add_argument("--job", type=str, help="Job-to-be-done description for Round 1B analysis.")

    args = parser.parse_args()

    # Decide which round to run based on the provided arguments
    if args.persona and args.job:
        run_round_1b(args)
    else:
        run_round_1a(args)

if __name__ == "__main__":
    main()
