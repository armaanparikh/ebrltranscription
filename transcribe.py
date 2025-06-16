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

BASE_PATH = "/Users/armaanparikh/Documents/EBRL/RC"

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

def list_available_audio_files(directory):
    """List all .mp3 and .wav files in the specified directory and return the list, excluding files that start with ~."""
    files = [file for file in os.listdir(directory) if (file.endswith('.mp3') or file.endswith('.wav')) and not file.startswith('~')]
    print("\nAvailable audio files in the directory:")
    for idx, file in enumerate(files, 1):
        print(f"  {idx}. {file}")
    return files

def get_valid_audio_file_path(directory, prompt, files=None):
    """Get a valid .mp3 or .wav file path from user input, allowing selection by number."""
    if files is None:
        files = list_available_audio_files(directory)
    while True:
        selection = input(prompt).strip()
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(files):
                return os.path.join(directory, files[idx])
            else:
                print("Invalid number. Please select a valid file number from the list above.")
        else:
            # Fallback: allow entering filename as before
            filename = selection
            if not (filename.endswith('.mp3') or filename.endswith('.wav')):
                filename += '.mp3'  # default to .mp3
            full_path = os.path.join(directory, filename)
            if os.path.exists(full_path):
                return full_path
            else:
                print(f"File not found: {filename}")
                print("Please choose from the available files listed above.")

def get_participant_directory():
    """Prompt for participant name and return the full directory path."""
    while True:
        participant = input("\nEnter participant name: ").strip()
        if not participant:
            print("Participant name cannot be empty!")
            continue
        participant_dir = os.path.join(BASE_PATH, participant)
        if os.path.exists(participant_dir):
            return participant_dir
        else:
            print(f"Directory not found for participant: {participant}")
            print("Please check the participant name and try again.")

def transcribe_audio(file_path, audio_dir=None):
    """Transcribe audio file using OpenAI's Whisper model"""
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Error: OPENAI_API_KEY not set in .env file")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    # Initialize OpenAI client
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
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using OpenAI's Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe a specific file
  python transcribe.py my_audio.mp3
  
  # Transcribe a file and save output to a text file
  python transcribe.py my_audio.mp3 -o output.txt
  
  # Use a different audio directory
  python transcribe.py my_audio.mp3 -d custom_audio_dir
  
  # List available files and transcribe interactively
  python transcribe.py
        """
    )
    parser.add_argument("file_path", nargs="?", help="Path to the audio file to transcribe")
    parser.add_argument("-o", "--output", help="Output text file path (optional)")
    parser.add_argument("-d", "--dir", help=f"Audio files directory (default: {AUDIO_DIR})", default=AUDIO_DIR)
    
    args = parser.parse_args()
    
    # Get the audio directory
    audio_dir = args.dir
    
    # If no file path provided, prompt for participant and show available files
    if not args.file_path:
        participant_dir = get_participant_directory()
        audio_dir = participant_dir  # override audio_dir to participant's directory
        if not os.path.exists(audio_dir):
            print(f"Error: Audio directory {audio_dir} does not exist!")
            sys.exit(1)
        available_files = list_available_audio_files(audio_dir)
        # Fallback: check /Audio subdirectory if no files found
        if not available_files:
            audio_subdir = os.path.join(audio_dir, 'Audio')
            if os.path.exists(audio_subdir):
                available_files = list_available_audio_files(audio_subdir)
                audio_dir = audio_subdir
        if not available_files:
            print(f"No audio files found in {audio_dir}")
            sys.exit(1)
        print("\nEnter the number for the file you want to transcribe (or press Ctrl+C to exit):")
        file_path = get_valid_audio_file_path(audio_dir, "> ", available_files)
    else:
        file_path = args.file_path
    
    # Resolve file path
    file_path = resolve_file_path(file_path, audio_dir)
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        print(f"Checked in current directory and {os.path.abspath(audio_dir)}")
        sys.exit(1)
    
    # Transcribe the audio
    transcription = transcribe_audio(file_path, audio_dir)
    
    if transcription:
        # Print the transcription before asking to save
        print("\nTranscription:")
        print("--------------")
        print(transcription)
        # Ask user if they want to save the transcription as a .txt file in this directory
        save_choice = input("\nDo you want to save the transcription as a .txt file in this directory? (y/n): ").strip().lower()
        if save_choice == 'y':
            # Always use the participant directory name (parent of /Audio if in /Audio)
            audio_dir = os.path.dirname(file_path)
            if os.path.basename(audio_dir) == 'Audio':
                participant_dir = os.path.dirname(audio_dir)
            else:
                participant_dir = audio_dir
            participant_name = os.path.basename(participant_dir)
            # Save in /Transcription if audio was in /Audio, else in participant dir
            transcription_dir = os.path.join(participant_dir, 'Transcription') if os.path.basename(audio_dir) == 'Audio' else participant_dir
            if not os.path.exists(transcription_dir):
                os.makedirs(transcription_dir)
            txt_path = os.path.join(transcription_dir, f"{participant_name}_gi_p1_transcription_whisper.txt")
            with open(txt_path, "w") as f:
                f.write(transcription)
            print(f"Transcription saved to {txt_path}")
    else:
        print("Transcription failed.")

if __name__ == "__main__":
    main() 