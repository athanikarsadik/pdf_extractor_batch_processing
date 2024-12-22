# pdf_extractor/app/data_extraction.py
import openai
from utils.image_processing import encode_image
from utils.pdf_processing import process_pdf
from utils.language_utils import get_language_mapping, detect_language

def extract_text_from_images(images, total_input_tokens, total_output_tokens):
    """Extracts text from images using the OpenAI API."""
    extracted_texts = []
    image_url = f"data:image/jpeg;base64,{encode_image(images[1])}"

    format_detection_prompt = (
        "You are an expert in extracting structured data from images. Analyze the provided first image only and determine its format—whether it contains a table or box-type layout.\n"
        "- Identify if the image contains a **table-type** format or a **box-type** format."
        "- If you find the text '(Original in Electronic Form)' or its equivalent in the local language in the first few lines of the image, consider it as table-type. Otherwise, classify it as box-type."
    )
    response = openai.ChatCompletion.create(
        model='gpt-4o',
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": format_detection_prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ],
        }],
        max_tokens=10,
    )
    total_input_tokens += response['usage']['total_tokens']
    total_output_tokens += response['usage']['completion_tokens']

    format_detection = response['choices'][0]['message']['content'].strip()

    if "box-type" in format_detection.lower():
        extraction_prompt = ('''
                For documents containing structured box-type information, extract only the specified fields as follows:

                1. **Field Extraction**:
                   - **International Application No.**:
                     - Locate the field labeled **"International Application No."** in the **first image of the document**.
                     - Extract the number that starts with **"PCT/"** and ensure the full number is included in the output.

                   - **Box No. II (Email)**:
                     - Identify **Box No. II**, and extract the email located under the **"Email Authorization"** subsection.
                     - Stop extracting once the next **Box No.** heading appears.

                   - **Box No. IV (Email)**:
                     - Locate the email under the **"Email Authorization"** subsection in **Box No. IV**.
                     - Capture the email text between **Box No. IV** and the subsequent **Box No.** heading.

                   - **Box No. X (Name and Signature)**:
                     - Identify **Box No. X**, and extract all relevant textual details (e.g., names or signatures).
                     - Specifically, locate and capture text enclosed within **forward slashes (`/ /`)**, ensuring the extracted content corresponds to a name or signature.
                     - Stop extracting at the next **Box No.** heading.

                2. **Output**:
                   - Return the extracted data only if the field is present in the document. If a field is missing, omit it from the output without generating placeholders or assumptions.

                3. **Format**:
                   - Output the extracted fields in the following format:
                     ```
                     International Application No.: [Extracted Application Number]
                     Email from Box No. II: [Extracted Email]
                     Email from Box No. IV: [Extracted Email]
                     Name from Box No. X: [Extracted Name or Signature]
                     Name of Signatory from Box No. X: [Extracted Name of Signatory]
                     ```

                4. **Guidelines**:
                   - Remove extraneous characters or text unrelated to the specified fields.
                   - Avoid creating or inferring content for fields that are not present in the document.
                   - If a specific **Box No.** or its content is not detected, leave it out of the final output.

                5. **Assumptions**:
                   - Extraction will strictly adhere to the fields mentioned above and their descriptions.
                   - Do not include additional comments, notes, or inferred information in the output.

                Focus on accurately extracting the specified information from each **Box No.** without deviation or inference beyond the described criteria.
        ''')
    else:
        extraction_prompt = (
            "You are an expert in extracting structured data from images. Analyze the images and extract the specified fields into a table format. Only return output if the fields are found.\n\n"

            "1. Individual Field Extraction:\n"
            "- Extract these fields if available:\n"
            "-----------------------------------------------------------------\n"
            "| Raw Number | Field                          | Value                      |\n"
            "-----------------------------------------------------------------\n"
            "| 0-1        | International Application No. | [Extracted Application No. (Starts with 'PCT/')] |\n"
            "| II-10      | Email                          | [Extracted email from Section II-10]            |\n"
            "| IV-1-5     | Email                          | [Extracted email from Section IV-1-5]           |\n"
            "-----------------------------------------------------------------\n\n"

            "Special Requirements:\n"
            "- For 'International Application No.': This number **always starts with 'PCT/'** and is located in the **first image of the PDF** and has text International Application No. before it . Capture only the complete application number that follows 'PCT/'.\n"
            "- For 'Email': Extract emails located in a **table format** at sections **IV-1-5** and **II-10**.\n"
            "- Below each email field, extract any text indicating 'Email Authentication' or similar verification statements as it appears directly below the email.\n\n"

            "2. Structured Table Extraction:\n"
            "- Extract this structured table only if present:\n"
            "--------------------------------------------------------------------\n"
            "| Raw Number | Field                                               | Value                          |\n"
            "--------------------------------------------------------------------\n"
            "| X-1        | Signature of applicant, agent, or representative    | [Extracted Signature]          |\n"
            "| X-1-1      | Name                                                | [Extracted Name]               |\n"
            "| X-1-2      | Name of signatory                                   | [Extracted Name of Signatory]  |\n"
            "| X-1-3      | Capacity (if not obvious)                           | [Extracted Capacity]           |\n"
            "--------------------------------------------------------------------\n\n"

            "Instructions:\n"
            "- **Only return tables if they exist; otherwise, generate no output.**\n"
            "- **No assumptions**: If a field is missing, do not assume values or create placeholders.\n"
            "Extract require text from the provided images without any additional commentary."
        )

    for image_data in images:
        image_url = f"data:image/jpeg;base64,{encode_image(image_data)}"
        response = openai.ChatCompletion.create(
            model='gpt-4o',
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": extraction_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ],
            }],
            max_tokens=150,
        )
        total_input_tokens += response['usage']['total_tokens']
        total_output_tokens += response['usage']['completion_tokens']
        extracted_text = response['choices'][0]['message']['content']
        extracted_texts.append(extracted_text.strip())

    final_extracted_texts = [text for text in extracted_texts if text.strip()]
    return "\n".join(final_extracted_texts), total_input_tokens, total_output_tokens

def extract_text_from_pdf(pdf_path, country_code, total_input_tokens, total_output_tokens):
    """Extracts text from a PDF file, handling multiple languages."""
    try:
        text = ""
        language_mapping = get_language_mapping()
        major_lang, minor_lang = language_mapping.get(country_code, ("eng", "eng"))
        images = process_pdf(pdf_path)
        extracted_text, input_tokens, output_tokens = extract_text_from_images(images, total_input_tokens, total_output_tokens)
        text += extracted_text + "\n"
        detected_language = detect_language(text)
        return text, detected_language, input_tokens, output_tokens
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return "", "eng", 0, 0

def ats_extractor(extracted_text, total_input_tokens, total_output_tokens):
    """Extracts specific fields from the extracted text using OpenAI API."""
    try:
        prompt = '''
        You are an AI expert tasked with extracting specific fields from a extracted text format. 
        The document may contain either a tabular or box layout. 

        Analyze the extracted text and determine which layout is present. Based on the detected layout, extract the relevant fields:

        **For Table-type layout:**
        - If a table-type layout is detected, extract the following fields:
          - International Application No. (0-1) 
          - Email from II-10
          - Email from IV-1-5
          - Name (X-1-1)
          - Name of Signatory (X-1-2)

        **For Box-type layout:**
        - If a box-type layout is detected, extract the following fields: 
          - International Application No. 
          - Email from Box No.II
          - Email from Box No.IV
          - Name from Box No.X (from Box No. X only)
          - Name of Signatory from Box No.X 

        Please analyze the extracted text below and provide the extracted fields in the following format:

        - International Application No. : [Extracted Value]
        - Email1: [Extracted Value or "NA" if not present at mention space]
        - Email2: [Extracted Value or "NA"]
        - Name: [Extracted Value or "NA"]
        - Name of Signatory: [Extracted Value or "NA"]

        '''
        messages = [{"role": "user", "content": prompt + "\n" + extracted_text}]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0,
            max_tokens=300
        )
        final_extracted_info = response['choices'][0]['message']['content'].strip()
        total_input_tokens += response['usage']['total_tokens']
        total_output_tokens += response['usage']['completion_tokens']
        final_extracted_info = final_extracted_info.replace("[", "").replace("]", "")
        return final_extracted_info
    except Exception as e:
        print("Error in ATS extraction:", str(e))
        return None