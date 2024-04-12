import os
import re
import PyPDF2


def extract_content(pdf_path):
    pdf_file_obj = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    page_obj = pdf_reader.getPage(0)
    return page_obj.extractText()


def extract_specific_transactions(content):
    pattern_transaction = re.compile(r'(?i)(Management Fee.+|Rent Income.+)')
    transactions = pattern_transaction.findall(content)
    return {'transactions': transactions}


folder_path = '/private/var/folders/_m/tczf4hnn1r193l420v0z6z_m0000gn/Cleanup At Startup'

# Get all pdf file paths
pdf_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.pdf')]

all_transactions = []

for file in pdf_files:
    text_content = extract_content(file)
    transactions_info = extract_specific_transactions(text_content)
    print(f'Pdf file: {file}\nTransactions: {transactions_info["transactions"]}\n')
    all_transactions.append(transactions_info['transactions'])

print('All transactions:', all_transactions)
