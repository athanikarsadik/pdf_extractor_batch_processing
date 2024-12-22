# pdf_extractor/utils/excel_utils.py
import os
import pandas as pd
from openpyxl.styles import PatternFill
from .language_utils import transliterate_if_needed

def save_to_excel(filename, extracted_data, input_filename):
    """Saves extracted data to an Excel file."""
    try:
        data = {
            'File Name': [],
            'International Application No.': [],
            'e-mail (II-10)': [],
            'e-mail (IV-1-5)': [],
            'Name': [],
            'Transliteration of Name': [],
            'Name of Signatory': [],
            'Transliteration of Name of Signatory': []
        }

        lines = extracted_data.splitlines()
        extracted_info = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                cleaned_key = key.strip().lstrip('-').strip()
                extracted_info[cleaned_key] = value.strip().replace("[", "").replace("]", "")

        name = extracted_info.get('Name', 'NA')
        signatory = extracted_info.get('Name of Signatory', 'NA')
        name_transliterated = transliterate_if_needed(name)
        signatory_transliterated = transliterate_if_needed(signatory)

        row_data = {
            'File Name': input_filename,
            'International Application No.': extracted_info.get('International Application No.', 'NA'),
            'e-mail (II-10)': extracted_info.get('Email1', 'NA'),
            'e-mail (IV-1-5)': extracted_info.get('Email2', 'NA'),
            'Name': name,
            'Transliteration of Name': name_transliterated,
            'Name of Signatory': signatory,
            'Transliteration of Name of Signatory': signatory_transliterated
        }

        for key in data.keys():
            data[key].append(row_data[key] if row_data.get(key) else 'NA')

        df = pd.DataFrame(data)

        if os.path.exists(filename):
            existing_df = pd.read_excel(filename, sheet_name='Extracted Data')
            df = pd.concat([existing_df, df], ignore_index=True)

        with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, sheet_name='Extracted Data', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Extracted Data']

            yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

            for row in range(2, len(df) + 2):
                if worksheet[f'B{row}'].value in [None, '']:
                    worksheet[f'B{row}'].value = 'NA'
                if worksheet[f'B{row}'].value == 'NA':
                    worksheet[f'B{row}'].fill = yellow_fill
                
                if worksheet[f'E{row}'].value in [None, '']:
                    worksheet[f'E{row}'].value = 'NA'
                if worksheet[f'E{row}'].value == 'NA':
                    worksheet[f'E{row}'].fill = yellow_fill

                email1 = worksheet[f'C{row}'].value
                email2 = worksheet[f'D{row}'].value

                if email1 in [None, ''] and email2 in [None, '']:
                    worksheet[f'C{row}'].value = 'NA'
                    worksheet[f'D{row}'].value = 'NA'
                    worksheet[f'C{row}'].fill = yellow_fill
                    worksheet[f'D{row}'].fill = yellow_fill

            workbook.save(filename)

        return filename
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        return None