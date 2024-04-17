import os
import re
import argparse
from PyPDF2 import PdfReader
from . import TableProcessor as Tp


def extract_content(file_path):
    pdf_reader = PdfReader(file_path)
    pdf_text_content = ''
    tp = Tp.TableProcessor()
    for page in pdf_reader.pages:
        pdf_text_content += page.extract_text(visitor_text=tp.extract_text_visitor_callback)

    return tp


def extract_info(content):
    pattern_date = re.compile(r'\b[A-Z][a-z]{2} \d{2}, \d{4}\b')
    pattern_unpaid = re.compile(r'(?i)unpaid\n(\d{2}/\d{2}/\d{4})\s(.+?)\s(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)')
    dates = pattern_date.findall(content)
    amounts_due = pattern_unpaid.findall(content)
    return {'dates': dates, 'amounts_due': amounts_due}


# Define a function to extract specific transactions from text content
def extract_specific_transactions(content):
    pattern_transaction = re.compile(r'(?i)(Management Fee.+|Rent Income.+)')
    transactions = pattern_transaction.findall(content)
    return {'transactions': transactions}


def main(args):
    """
    Extracts the transaction data from a directory of PDFs and optionally outputs to a CSV file.
    """
    dir_path = args.input_directory
    output_csv = args.output_csv

    if output_csv is not None and os.path.exists(output_csv):
        raise ValueError(f"Output file {output_csv} already exists")

    # Get all pdf file paths
    pdf_files = []
    for file in os.listdir(dir_path):
        if file.endswith('.pdf') and file.startswith('statement_'):
            pdf_files.append(os.path.join(dir_path, file))

    # APPARENTLY files are not necessarily sorted in the order we want, thus we sort them
    pdf_files.sort()

    # Extract information
    table_processor = None
    for file in pdf_files:
        if table_processor is None:
            table_processor = extract_content(file)
        else:
            table_processor.concat(extract_content(file))
    if output_csv is None:
        print(table_processor.to_csv(None))
    else:
        table_processor.to_csv(output_csv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process PDFs in a directory and optionally output CSV file')
    parser.add_argument('input_directory', help='Path to the directory containing PDFs')
    parser.add_argument('--output-csv', dest='output_csv', help='Path to the output CSV file (optional)')

    args = parser.parse_args()
    main(args)
