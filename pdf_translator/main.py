from settings import settings
import sys
import openai
import argparse
from pathlib import Path
import PyPDF2
from typing import Any
from dataclasses import dataclass


@dataclass
class TranslationMessage:
    role: str
    content: str


def read_pdf(file_path: str | Path) -> str | None:
    """Read text content from a PDF file."""
    text_content: list[str] = []

    try:
        with open(file_path, "rb") as file:
            # Create PDF reader object
            pdf_reader: PyPDF2.PdfReader = PyPDF2.PdfReader(file)

            # Extract text from each page
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())

        return "\n".join(text_content)
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return None


def translate_text(text: str, chunk_size: int | None = None) -> str | None:
    """Translate text to Chinese using GPT API."""
    if not text:
        return None

    if not settings.is_configured:
        print("Error: OpenAI API key not configured!")
        print("Please set it via:")
        print("1. Environment variable OPENAI_API_KEY")
        print("2. .env file with OPENAI_API_KEY=your-key")
        print("3. Command line argument --api-key")
        return None

    openai.api_key = settings.api_key
    chunk_size = chunk_size or settings.chunk_size
    chunks: list[str] = [
        text[i : i + chunk_size] for i in range(0, len(text), chunk_size)
    ]

    # Initialize conversation with system message
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": """You are a professional translator.
        I will provide you with multiple parts of a PDF document.
        Please translate each part to Chinese while maintaining the original structure and formatting.
        Make sure to preserve any technical terms or proper nouns appropriately.
        I will send you the content part by part, and you should translate each part.""",
        },
    ]

    translations: list[str] = []

    try:
        # Send chunks one by one and collect translations
        for i, chunk in enumerate(chunks, 1):
            messages.append(
                {
                    "role": "user",
                    "content": f"Here's part {i} of the PDF content to translate:\n\n{chunk}",
                },
            )

            response: Any = openai.ChatCompletion.create(
                model=settings.model,
                messages=messages,
            )

            translation: str = response.choices[0].message.content
            translations.append(translation)

            # Add assistant's response to maintain conversation context
            messages.append(
                {
                    "role": "assistant",
                    "content": translation,
                },
            )

            print(f"Translated chunk {i}/{len(chunks)}")

        return "\n".join(translations)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return None


def save_translation(translated_text: str, output_path: str | Path) -> bool:
    """Save translated text to a file."""
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(translated_text)
        return True
    except Exception as e:
        print(f"Error saving translation: {str(e)}")
        return False


def main() -> None:
    # Check if API key is configured
    if not settings.is_configured:
        print("Error: OpenAI API key not configured!")
        sys.exit(1)

    # Parse command line arguments
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Translate PDF to Chinese",
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: input_translated.txt)",
    )
    args: argparse.Namespace = parser.parse_args()

    # Validate PDF path
    pdf_path: Path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    # Set output path
    output_path: Path = (
        Path(args.output)
        if args.output
        else pdf_path.with_stem(f"{pdf_path.stem}_translated").with_suffix(".txt")
    )

    # Read PDF content
    print(f"Reading PDF: {pdf_path}")
    pdf_content: str | None = read_pdf(pdf_path)

    if not pdf_content:
        print("Failed to read PDF content!")
        sys.exit(1)

    # Translate content
    print("\nStarting translation...")
    print(f"Using model: {settings.model}")
    print(f"Chunk size: {settings.chunk_size} characters")
    translated_content: str | None = translate_text(pdf_content)

    if not translated_content:
        print("Translation failed!")
        sys.exit(1)

    # Save translation
    print("\nSaving translation...")
    if save_translation(translated_content, output_path):
        print(f"Translation successfully saved to: {output_path}")
    else:
        print("Failed to save translation!")
        sys.exit(1)


if __name__ == "__main__":
    main()
