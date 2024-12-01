import sys
import openai
from pathlib import Path
import PyPDF2
from dataclasses import dataclass
from pdf_translator.args_parser import ArgsParser, ParsedArgs


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


def translate_text(text: str, settings: ParsedArgs) -> str | None:
    """Translate text to Chinese using GPT API."""

    def _preprocess_chunk(chunk: str) -> str:
        return chunk.replace("\n", "")

    if not text:
        return None

    if not settings.api_key:
        print("Error: OpenAI API key not configured!")
        print("Please set it via:")
        print("1. Environment variable OPENAI_API_KEY")
        print("2. .env file with OPENAI_API_KEY=your-key")
        print("3. Command line argument --api-key")
        return None

    # Initialize the client
    client = openai.OpenAI(api_key=settings.api_key)

    chunks: list[str] = [
        text[i : i + settings.chunk_size]
        for i in range(0, len(text), settings.chunk_size)
    ]

    translations: list[str] = []

    try:
        # Send chunks one by one and collect translations
        for i, chunk in enumerate(chunks, 1):
            chunk = _preprocess_chunk(chunk)
            print(f"Sending chunk {i}/{len(chunks)} to OpenAI...", repr(chunk))
            response = client.chat.completions.create(
                model=settings.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional translator.
                    Please translate the following text to English while maintaining the original structure and formatting.
                    Make sure to preserve any technical terms or proper nouns appropriately.""",
                    },
                    {
                        "role": "user",
                        "content": f"Here's part {i} of the content to translate:\n\n{chunk}",
                    },
                ],
            )

            translation: str = response.choices[0].message.content
            print(f"Received translation from OpenAI: {translation}")
            translations.append(translation)
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
    # Get settings from environment and CLI
    parser = ArgsParser(env_prefix="PDFT_")
    parsed_args = parser.parse_args()

    # Set default output path if not specified
    output_path = (
        parsed_args.output or f"translated_{parsed_args.pdf_path.rstrip('.pdf')}.txt"
    )

    # Read PDF content
    print(f"Reading PDF: {parsed_args.pdf_path}")
    pdf_content: str | None = read_pdf(parsed_args.pdf_path)

    if not pdf_content:
        print("Failed to read PDF content!")
        sys.exit(1)

    # Translate content
    print("\nStarting translation...")
    print(f"Using model: {parsed_args.model}")
    print(f"Chunk size: {parsed_args.chunk_size} characters")
    translated_content: str | None = translate_text(pdf_content, parsed_args)

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
