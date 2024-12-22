import fitz
from .image_processing import enhance_image

def process_pdf(pdf_path):
    """Processes a PDF file to extract images."""
    images = []
    doc = fitz.open(pdf_path)
    for page in doc:
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            enhanced_image = enhance_image(image_data)
            images.append(enhanced_image)
    doc.close()
    return images