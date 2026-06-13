import os
import cv2
import numpy as np
import pytesseract
import fitz  # PyMuPDF
import logging

from src.utils import get_config

logger = logging.getLogger("MedicalApp.OCRService")

# Attempt to auto-locate Tesseract OCR executable on Windows
def auto_configure_tesseract():
    """Tries to find Tesseract in config or common Windows paths."""
    # 1. Check config first
    try:
        config = get_config()
        custom_path = config.get("tesseract_path", "")
        if custom_path and os.path.exists(custom_path):
            pytesseract.pytesseract.tesseract_cmd = custom_path
            logger.info(f"Configured Tesseract path from settings: {custom_path}")
            return True
    except Exception as e:
        logger.warning(f"Failed to check config for Tesseract: {e}")

    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
    ]
    
    # Check if already in PATH
    try:
        pytesseract.get_tesseract_version()
        logger.info("Tesseract is already available in PATH.")
        return True
    except pytesseract.TesseractNotFoundError:
        pass

    # Search common paths
    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            logger.info(f"Auto-configured Tesseract path: {path}")
            return True
            
    logger.warning("Tesseract OCR executable could not be auto-located. "
                   "Please ensure it is installed and added to PATH, or configured.")
    return False

# Initialize configuration
auto_configure_tesseract()

class OCRService:
    """Handles text extraction from PDF and image files using OpenCV and Tesseract OCR."""

    @staticmethod
    def preprocess_image(img: np.ndarray) -> np.ndarray:
        """Applies OpenCV pre-processing to improve OCR accuracy."""
        try:
            # 1. Convert to grayscale if color
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img.copy()

            # 2. Denoise using bilateral filter (keeps edges sharp)
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)

            # 3. Increase contrast/binarize using Otsu's thresholding
            binarized = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            return binarized
        except Exception as e:
            logger.error(f"Error in OpenCV pre-processing: {e}")
            return img  # Return original if pre-processing fails

    @classmethod
    def extract_text_from_image(cls, file_path: str) -> str:
        """Loads an image, processes it with OpenCV, and extracts text via Tesseract OCR."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Image file not found: {file_path}")

            # Read image using OpenCV (supports unicode file paths via np.fromfile)
            img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to load image via OpenCV.")

            processed_img = cls.preprocess_image(img)

            # Run pytesseract OCR
            text = pytesseract.image_to_string(processed_img)
            return text
        except pytesseract.TesseractNotFoundError:
            err_msg = ("Tesseract OCR engine not found. "
                       "Please download and install Tesseract for Windows and restart the application.")
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        except Exception as e:
            logger.error(f"Error performing OCR on image {file_path}: {e}")
            raise e

    @classmethod
    def extract_text_from_pdf(cls, file_path: str) -> str:
        """
        Extracts text from PDF.
        First tries digital text extraction; falls back to rendering page images and performing OCR if empty.
        """
        try:
            doc = fitz.open(file_path)
            extracted_text = ""
            is_scanned = True

            # Step 1: Check for digital text
            for page in doc:
                text = page.get_text()
                if text.strip():
                    extracted_text += f"\n--- Page {page.number + 1} ---\n{text}"
                    is_scanned = False
            
            if not is_scanned:
                logger.info(f"Extracted digital text from PDF: {file_path}")
                doc.close()
                return extracted_text.strip()

            # Step 2: PDF is scanned, convert pages to images and run OCR
            logger.info(f"PDF appears to be scanned. Falling back to OCR for PDF: {file_path}")
            extracted_text = ""
            
            for page in doc:
                # Render page to high-quality image bytes
                pix = page.get_pixmap(dpi=150)
                img_data = pix.tobytes("png")
                
                # Load image from bytes into OpenCV
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                processed_img = cls.preprocess_image(img)
                page_text = pytesseract.image_to_string(processed_img)
                extracted_text += f"\n--- Page {page.number + 1} ---\n{page_text}"

            doc.close()
            return extracted_text.strip()
        except pytesseract.TesseractNotFoundError:
            err_msg = ("Tesseract OCR engine not found. "
                       "Please download and install Tesseract for Windows and restart the application.")
            logger.error(err_msg)
            raise RuntimeError(err_msg)
        except Exception as e:
            logger.error(f"Error performing text extraction on PDF {file_path}: {e}")
            raise e

    @classmethod
    def extract(cls, file_path: str) -> str:
        """Determines the file type and routes to the appropriate extraction method."""
        _, ext = os.path.splitext(file_path.lower())
        if ext == ".pdf":
            return cls.extract_text_from_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff"]:
            return cls.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
