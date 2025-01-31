"""Test for Whisper with Apple Silicon support and device fallback."""

import argparse
import torch

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    # デフォルトパスを簡潔に
    parser.add_argument("--model_path", default="", help="Path to the Whisper model")
    return parser

def main():
    """Run a device check and warn if fallback is used."""
    args = parse_arguments()
    device = "cpu"

    # Apple Silicon向けMPSが利用可能か判定
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        print("Warning: No GPU or MPS available, using CPU.")

    print(f"Using device: {device}")
    # モデルパスの使用やその他テストロジックを追記

if __name__ == "__main__":
    main() 