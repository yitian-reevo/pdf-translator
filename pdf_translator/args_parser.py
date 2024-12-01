from dataclasses import dataclass
from typing import Any
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class ParsedArgs:
    """Data class to hold parsed arguments"""

    api_key: str
    model: str
    chunk_size: int
    pdf_path: str
    output: str | None


class ArgsParser:
    """Common arguments parser that supports both environment variables and CLI arguments"""

    def __init__(self, env_prefix: str = "") -> None:
        """
        Initialize the parser
        Args:
            env_prefix: Prefix for environment variables (e.g., "PDFT_" for PDF_TRANSLATOR)
        """
        self.env_prefix = env_prefix
        self._parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all supported arguments"""
        parser = argparse.ArgumentParser(description="PDF Translator Settings")

        parser.add_argument(
            "--api-key",
            help="OpenAI API Key",
        )
        parser.add_argument(
            "--pdf-path",
            help="Path to the PDF file",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            help="Translation chunk size",
            default=500,
        )
        parser.add_argument(
            "--model",
            help="OpenAI model to use",
            default="gpt-3.5-turbo",
        )
        parser.add_argument(
            "--env-file",
            type=Path,
            help="Path to environment file",
            default=Path(".env"),
        )
        parser.add_argument(
            "--output",
            "-o",
            help="Output file path (default: translated_<input>.txt)",
        )

        return parser

    def _get_env_value(self, key: str, default: Any = None) -> Any:
        """Get value from environment variables"""
        env_key = f"{self.env_prefix}{key.upper()}"
        return os.getenv(env_key, default)

    def _load_env_file(self, env_path: Path) -> None:
        """Load environment variables from specified env file"""
        if env_path.exists():
            load_dotenv(env_path)

    def parse_args(self) -> ParsedArgs:
        """
        Parse arguments from both environment variables and command line
        Priority: CLI args > Environment variables > Default values
        """
        # Parse CLI arguments first to get env file path
        cli_args, _ = self._parser.parse_known_args()

        # Load env file if specified
        self._load_env_file(cli_args.env_file)

        # API Key: Try CLI, then env var (with and without prefix)
        parsed_api_key = cli_args.api_key or self._get_env_value("api_key")

        # Chunk size: Try CLI, then env var, then default
        parsed_chunk_size = (
            cli_args.chunk_size
            if cli_args.chunk_size != 2000
            else int(self._get_env_value("chunk_size", 2000))
        )

        # Model: Try CLI, then env var, then default
        parsed_model = (
            cli_args.model
            if cli_args.model != "gpt-3.5-turbo"
            else self._get_env_value("model", "gpt-3.5-turbo")
        )

        # PDF Path: Try CLI, then env var, then default
        parsed_pdf_path = cli_args.pdf_path or self._get_env_value("pdf_path")

        # Output: Try CLI, then env var, then default
        parsed_output = cli_args.output or self._get_env_value("output")

        if not parsed_api_key:
            self._parser.error("API key is required")

        if not parsed_pdf_path:
            self._parser.error("PDF path is required")
        elif not parsed_pdf_path.endswith(".pdf"):
            self._parser.error("target file specified by --pdf-path must be a pdf file")

        return ParsedArgs(
            api_key=parsed_api_key,
            model=parsed_model,
            chunk_size=parsed_chunk_size,
            pdf_path=parsed_pdf_path,
            output=parsed_output,
        )
