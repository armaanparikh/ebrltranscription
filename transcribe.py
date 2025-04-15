import os
import sys
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()

# Define the default audio directory
AUDIO_DIR = "audio_files"

def convert_to_mp3(input_file, output_file=None):
    """Convert audio file to mp3 format if needed"""
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.mp3'
    
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="mp3")
    return output_file

def resolve_file_path(file_path, audio_dir=None):
    """
    Resolve the file path. If it's a relative path that doesn't exist,
    check the audio_files directory.
    """
    if audio_dir is None:
        audio_dir = AUDIO_DIR
        
    if os.path.exists(file_path):
        return file_path
    
    # Check if the file exists in the audio files directory
    audio_dir_path = os.path.join(os.path.dirname(__file__), audio_dir, file_path)
    if os.path.exists(audio_dir_path):
        return audio_dir_path
    
    # If file doesn't exist in either location, return original path
    return file_path

def transcribe_audio(file_path, audio_dir=None):
    """Transcribe audio file using OpenAI's Whisper model"""
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Error: OPENAI_API_KEY not set in .env file")
        sys.exit(1)
    
    # Initialize OpenAI client with API key from environment variable
    # OpenAI client automatically looks for OPENAI_API_KEY in environment variables
    client = OpenAI()
    
    # Resolve file path
    file_path = resolve_file_path(file_path, audio_dir)
    
    # Convert file to mp3 if it's not already
    if not file_path.endswith('.mp3'):
        print(f"Converting {file_path} to mp3 format...")
        file_path = convert_to_mp3(file_path)
    
    print(f"Transcribing {file_path}...")
    
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        return transcript.text
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio files using OpenAI's Whisper")
    parser.add_argument("file_path", help="Path to the audio file to transcribe (will check in audio_files/ if not found)")
    parser.add_argument("-o", "--output", help="Output text file path (optional)")
    parser.add_argument("-d", "--dir", help=f"Audio files directory (default: {AUDIO_DIR})", default=AUDIO_DIR)
    
    args = parser.parse_args()
    
    # Get the audio directory
    audio_dir = args.dir
    
    # Resolve file path
    file_path = resolve_file_path(args.file_path, audio_dir)
    
    if not os.path.exists(file_path):
        print(f"Error: File {args.file_path} not found")
        print(f"Checked in current directory and {os.path.abspath(audio_dir)}")
        sys.exit(1)
    
    # Transcribe the audio
    transcription = transcribe_audio(file_path, audio_dir)
    
    if transcription:
        # Output the transcription
        if args.output:
            with open(args.output, "w") as f:
                f.write(transcription)
            print(f"Transcription saved to {args.output}")
        else:
            print("\nTranscription:")
            print("--------------")
            print(transcription)
    else:
        print("Transcription failed.")

if __name__ == "__main__":
    main() 