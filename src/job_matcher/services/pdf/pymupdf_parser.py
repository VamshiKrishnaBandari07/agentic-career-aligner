import io

import fitz

from job_matcher.core.exceptions import PDFParseError
from job_matcher.core.models.document import ParsedDocument
from job_matcher.services.pdf.text_cleaner import clean_pdf_text


class PyMuPDFParser:
    def parse(self, file_bytes: bytes, filename: str) -> ParsedDocument:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as exc:
            raise PDFParseError(f"Could not open PDF '{filename}': {exc}") from exc

        try:
            parts: list[str] = []
            for page in doc:
                parts.append(page.get_text("text"))
            raw_text = "\n".join(parts)
            page_count = len(doc)
        except Exception as exc:
            raise PDFParseError(f"Failed to read PDF '{filename}': {exc}") from exc
        finally:
            doc.close()

        text = clean_pdf_text(raw_text)
        if not text:
            raise PDFParseError(f"No extractable text found in '{filename}'")

        return ParsedDocument(
            filename=filename,
            text=text,
            page_count=page_count,
            char_count=len(text),
        )

    @staticmethod
    def create_sample_pdf(title: str, body: str) -> bytes:
        """Build a minimal PDF in memory (used by tests)."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), f"{title}\n\n{body}", fontsize=11)
        buffer = io.BytesIO()
        doc.save(buffer)
        doc.close()
        return buffer.getvalue()
