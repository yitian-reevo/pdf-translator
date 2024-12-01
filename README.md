> Note: This project, including all code and documentation, is generated through AI pair-programming. While functional, some design decisions might reflect this experimental approach.

# PDF Translator

A command-line tool that translates PDF documents using OpenAI's GPT models. The tool extracts text from PDF files, splits it into chunks and translates chunks one by one.

## Features

- PDF text extraction
- Translation using OpenAI's GPT models (default: gpt-3.5-turbo)
- Configurable chunk size for handling large documents
- Support for environment variables and command-line arguments
- Flexible output file naming

## Prerequisites

- Python 3.8+
- Poetry for dependency management
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-translator.git
cd pdf-translator
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Configuration

The tool supports multiple ways to configure settings (in order of precedence):

1. Command-line arguments
2. Environment variables (with PDFT_ prefix)
3. `.env` file

### Required Configuration

- OpenAI API Key (one of the following):
  ```bash
  # Via command line
  --api-key YOUR_API_KEY

  # Via environment variable
  PDFT_API_KEY=YOUR_API_KEY

  # Via .env file
  PDFT_API_KEY=YOUR_API_KEY
  ```

### Optional Configuration

- Chunk size (default: 500 characters)
  ```bash
  # Via command line
  --chunk-size 1000

  # Via environment
  PDFT_CHUNK_SIZE=1000
  ```

- Model (default: gpt-3.5-turbo)
  ```bash
  # Via command line
  --model gpt-4

  # Via environment
  PDFT_MODEL=gpt-4
  ```

- Environment file path
  ```bash
  # Via command line
  --env-file /path/to/.env
  ```

## Usage

Basic usage:

```bash
python -m pdf_translator --pdf-path input.pdf
```

With custom output file:

```bash
python -m pdf_translator --pdf-path input.pdf -o output.txt
```

Using environment variables:

```bash
export PDFT_API_KEY=YOUR_API_KEY
python -m pdf_translator --pdf-path input.pdf
```

Full example with all options:

```bash
python -m pdf_translator \
    --api-key YOUR_API_KEY \
    --chunk-size 1000 \
    --model gpt-4 \
    --env-file custom.env \
    --pdf-path input.pdf \
    -o translated_output.txt
```

## Output

The translated text will be saved to:
- If output path is specified: Uses the specified path
- If not specified: `translated_<input_filename>.txt`

## Error Handling

The tool provides clear error messages for:
- Missing API key
- Invalid PDF file path
- PDF reading errors
- Translation failures
- Output file writing errors

## Known Limitations

1. The tool currently only supports text extraction from PDFs that have selectable text
2. Very large PDFs might take a long time to process due to API rate limits
3. The quality of translation depends on the OpenAI model used

## Contributing

Feel free to open issues or submit pull requests for:
- Bug fixes
- New features
- Documentation improvements
- Translation quality improvements

## License

This project is licensed under the MIT License.
