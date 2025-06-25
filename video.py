#!/usr/bin/env python3
"""
Video to MP3 Converter and Transcriber
Extracts audio from MP4 files and transcribes them using OpenAI's Whisper model.
Optimized for speed and performance.
"""

import os
import sys
import glob
import time
import concurrent.futures
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
import subprocess

# Load environment variables from .env file
load_dotenv()

# Define the base path for participant directories
BASE_PATH = "/Users/armaanparikh/Documents/EBRL/RC"

# Optimization settings
MAX_WORKERS = 3  # Number of parallel transcription workers
CHUNK_DURATION_MS = 300000  # 5 minutes per chunk (reduced from 10 for faster processing)
AUDIO_BITRATE = "128k"  # Reduced bitrate for faster processing
AUDIO_SAMPLE_RATE = "22050"  # Reduced sample rate for faster processing

def print_header():
    """Print a header for the application"""
    print(" /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\")
    print("/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\")
    print("\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /")
    print(" \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/")
    print("")
    print("  EEEEE  BBBBB  RRRRR  L")
    print("  E      B   B  R   R  L")
    print("  EEEE   BBBB   RRRR   L")
    print("  E      B   B  R R    L")
    print("  EEEEE  BBBBB  R  R   LLLLL")
    print("")
    print(" /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\")
    print("/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\")
    print("\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /\\  /")
    print(" \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/  \\/")
    print("")
    print("=" * 60)
    print("    Video to MP3 Converter and Transcriber (Optimized)")
    print("=" * 60)

def print_success(message):
    """Print a success message"""
    print(f"✓ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ  {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"⚠  {message}")

def print_error(message):
    """Print an error message"""
    print(f"✗ {message}")

def print_progress(message):
    """Print a progress message"""
    print(f"→ {message}")

def print_separator():
    """Print a decorative separator"""
    print("=" * 60)

def print_mini_separator():
    """Print a mini decorative separator"""
    print("-" * 40)

def get_participant_name():
    """
    Prompt user for participant name and return the full directory path
    
    Returns:
        str: Full path to the participant directory
    """
    while True:
        print(f"\nEnter participant name: ", end="")
        participant_name = input().strip()
        if not participant_name:
            print_error("Participant name cannot be empty. Please try again.")
            continue
        
        # Construct the full path
        participant_path = os.path.join(BASE_PATH, participant_name)
        
        # Check if directory exists
        if not os.path.exists(participant_path):
            print_error(f"Directory not found: {participant_path}")
            print_info("Please check the participant name and try again.")
            continue
        
        print_success(f"Found participant directory: {participant_name}")
        return participant_path

def list_video_files(directory):
    """
    List all MP4 files in the directory
    
    Args:
        directory (str): Directory to search for video files
    
    Returns:
        list: List of video file paths
    """
    video_files = []
    
    # Find all MP4 files (case insensitive)
    mp4_files = glob.glob(os.path.join(directory, "*.mp4"))
    mp4_files.extend(glob.glob(os.path.join(directory, "*.MP4")))
    
    video_files = mp4_files
    return sorted(video_files)

def display_video_files(video_files):
    """
    Display numbered list of video files
    
    Args:
        video_files (list): List of video file paths
    """
    if not video_files:
        print_warning("No MP4 files found in this directory.")
        return
    
    print(f"\nFound {len(video_files)} video file(s):")
    print_mini_separator()
    
    for i, file_path in enumerate(video_files, 1):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        
        print(f"{i:2d}. [MP4] {filename} ({file_size:.1f} MB)")
    
    print_mini_separator()

def get_user_selection(video_files, max_selections=10):
    """
    Get user selection for files to process
    
    Args:
        video_files (list): List of video file paths
        max_selections (int): Maximum number of files user can select
    
    Returns:
        list: List of selected file paths
    """
    if not video_files:
        return []
    
    selected_files = []
    
    print(f"\nSelect up to {max_selections} files to process:")
    print("   Enter numbers separated by spaces, or 'all' for all files")
    print("   Note: MP4 files will be converted to MP3 and then transcribed.")
    
    while True:
        try:
            print(f"\nEnter selection: ", end="")
            user_input = input().strip()
            
            if user_input.lower() == 'all':
                # Select all MP4 files
                selected_files = video_files
                print_success(f"Selected all {len(selected_files)} video files!")
                break
            
            # Parse user input
            selections = user_input.split()
            selected_indices = []
            
            for selection in selections:
                index = int(selection)
                if 1 <= index <= len(video_files):
                    selected_indices.append(index - 1)  # Convert to 0-based index
                else:
                    print_error(f"Invalid selection: {selection}. Please enter numbers between 1 and {len(video_files)}.")
                    selected_indices = []
                    break
            
            if selected_indices:
                if len(selected_indices) > max_selections:
                    print_error(f"Too many selections. Please select no more than {max_selections} files.")
                    continue
                
                selected_files = [video_files[i] for i in selected_indices]
                print_success(f"Selected {len(selected_files)} file(s)!")
                break
                
        except ValueError:
            print_error("Invalid input. Please enter numbers separated by spaces, or 'all'.")
        except KeyboardInterrupt:
            print(f"\nOperation cancelled by user.")
            sys.exit(0)
    
    return selected_files

def extract_audio_from_video(video_file, output_file=None):
    """
    Extract audio from MP4 file using ffmpeg with optimized settings
    
    Args:
        video_file (str): Path to the input MP4 file
        output_file (str): Path to the output MP3 file (optional)
    
    Returns:
        str: Path to the extracted MP3 file, or None if extraction failed
    """
    try:
        if not output_file:
            # Create output filename (same name but with .mp3 extension)
            output_file = os.path.splitext(video_file)[0] + '.mp3'
        
        # Check if output file already exists
        if os.path.exists(output_file):
            print_warning(f"{os.path.basename(output_file)} already exists. Skipping extraction.")
            return output_file
        
        filename = os.path.basename(video_file)
        print(f"\nExtracting audio from: {filename}")
        
        # Use ffmpeg with optimized settings for faster processing
        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-vn',  # No video
            '-acodec', 'mp3',  # Audio codec
            '-ab', AUDIO_BITRATE,  # Optimized bitrate
            '-ar', AUDIO_SAMPLE_RATE,  # Optimized sample rate
            '-ac', '1',  # Mono audio (faster processing)
            '-y',  # Overwrite output file
            output_file
        ]
        
        print_progress("Extracting audio with optimized settings...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success(f"Audio extracted: {os.path.basename(output_file)}")
            return output_file
        else:
            print_error(f"FFmpeg error: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print_error("FFmpeg not found. Please install FFmpeg to extract audio from video files.")
        return None
    except Exception as e:
        print_error(f"Error extracting audio: {str(e)}")
        return None

def split_audio_file(audio_file, chunk_duration_ms=CHUNK_DURATION_MS):
    """
    Split a large audio file into smaller chunks with optimized settings
    
    Args:
        audio_file (str): Path to the audio file to split
        chunk_duration_ms (int): Duration of each chunk in milliseconds
    
    Returns:
        list: List of paths to the chunk files
    """
    try:
        print_progress("Splitting large audio file into optimized chunks...")
        
        # Load the audio file
        audio = AudioSegment.from_file(audio_file)
        
        # Convert to mono for faster processing
        audio = audio.set_channels(1)
        
        # Calculate number of chunks needed
        total_duration = len(audio)
        num_chunks = (total_duration + chunk_duration_ms - 1) // chunk_duration_ms
        
        chunk_files = []
        base_name = os.path.splitext(audio_file)[0]
        
        for i in range(num_chunks):
            start_time = i * chunk_duration_ms
            end_time = min((i + 1) * chunk_duration_ms, total_duration)
            
            # Extract chunk
            chunk = audio[start_time:end_time]
            
            # Create chunk filename
            chunk_filename = f"{base_name}_chunk_{i+1:03d}.mp3"
            
            # Export chunk with optimized settings
            chunk.export(chunk_filename, format="mp3", bitrate=AUDIO_BITRATE, parameters=["-ar", AUDIO_SAMPLE_RATE])
            chunk_files.append(chunk_filename)
            
            print_progress(f"Created optimized chunk {i+1}/{num_chunks}: {os.path.basename(chunk_filename)}")
        
        return chunk_files
        
    except Exception as e:
        print_error(f"Error splitting audio file: {str(e)}")
        return []

def transcribe_chunk(chunk_file, chunk_index, total_chunks):
    """
    Transcribe a single audio chunk
    
    Args:
        chunk_file (str): Path to the audio chunk file
        chunk_index (int): Index of the chunk being processed
        total_chunks (int): Total number of chunks
    
    Returns:
        tuple: (chunk_index, transcription_text) or (chunk_index, None) if failed
    """
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return (chunk_index, None)
    
    # Initialize OpenAI client
    client = OpenAI()
    
    try:
        print_progress(f"Transcribing chunk {chunk_index}/{total_chunks}...")
        
        with open(chunk_file, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        print_success(f"Chunk {chunk_index} transcribed successfully")
        return (chunk_index, transcript.text)
        
    except Exception as e:
        print_error(f"Error transcribing chunk {chunk_index}: {str(e)}")
        return (chunk_index, None)

def transcribe_audio_chunks_parallel(chunk_files):
    """
    Transcribe multiple audio chunks in parallel for faster processing
    
    Args:
        chunk_files (list): List of paths to audio chunk files
    
    Returns:
        str: Combined transcription text, or None if transcription failed
    """
    if not chunk_files:
        return None
    
    transcriptions = [None] * len(chunk_files)
    
    # Use ThreadPoolExecutor for parallel transcription
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all transcription tasks
        future_to_chunk = {
            executor.submit(transcribe_chunk, chunk_file, i+1, len(chunk_files)): i 
            for i, chunk_file in enumerate(chunk_files)
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk_index, transcription = future.result()
            if transcription is not None:
                transcriptions[chunk_index-1] = transcription
            else:
                return None  # If any chunk fails, return None
    
    # Combine all transcriptions in order
    combined_transcription = " ".join(transcriptions)
    return combined_transcription

def cleanup_chunk_files(chunk_files):
    """
    Clean up temporary chunk files
    
    Args:
        chunk_files (list): List of paths to chunk files to delete
    """
    try:
        for chunk_file in chunk_files:
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
                print_progress(f"Cleaned up: {os.path.basename(chunk_file)}")
    except Exception as e:
        print_warning(f"Error cleaning up chunk files: {str(e)}")

def transcribe_audio(file_path):
    """
    Transcribe audio file using OpenAI's Whisper model
    Handles large files by splitting into chunks if necessary
    Optimized for speed with parallel processing
    
    Args:
        file_path (str): Path to the audio file to transcribe
    
    Returns:
        str: Transcribed text, or None if transcription failed
    """
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print_error("OPENAI_API_KEY not set in .env file")
        print_info("Please set your OpenAI API key in the .env file")
        return None
    
    # Check file size (25MB = 26,214,400 bytes)
    file_size = os.path.getsize(file_path)
    max_size = 26214400  # 25MB in bytes
    
    if file_size > max_size:
        print_warning(f"File size ({file_size / (1024*1024):.1f} MB) exceeds 25MB limit")
        print_info("Splitting file into optimized chunks for parallel transcription...")
        
        # Split the audio file into chunks
        chunk_files = split_audio_file(file_path)
        if not chunk_files:
            return None
        
        # Transcribe chunks in parallel
        transcription = transcribe_audio_chunks_parallel(chunk_files)
        
        # Clean up chunk files
        cleanup_chunk_files(chunk_files)
        
        return transcription
    else:
        # File is small enough, transcribe normally
        print_progress("Transcribing audio...")
        
        # Initialize OpenAI client
        client = OpenAI()
        
        try:
            with open(file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            return transcript.text
        except Exception as e:
            print_error(f"Error during transcription: {str(e)}")
            return None

def save_transcription(transcription, original_video_file, participant_dir):
    """
    Save transcription to a text file
    
    Args:
        transcription (str): The transcribed text
        original_video_file (str): Path to the original video file
        participant_dir (str): Participant directory path
    
    Returns:
        str: Path to the saved transcription file
    """
    try:
        # Create Transcription directory if it doesn't exist
        transcription_dir = os.path.join(participant_dir, 'Transcription')
        if not os.path.exists(transcription_dir):
            os.makedirs(transcription_dir)
        
        # Generate filename based on original video file
        video_filename = os.path.splitext(os.path.basename(original_video_file))[0]
        participant_name = os.path.basename(participant_dir)
        
        # Create output filename
        output_filename = f"{participant_name}_{video_filename}_transcription_whisper.txt"
        output_path = os.path.join(transcription_dir, output_filename)
        
        # Save transcription
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcription)
        
        print_success(f"Transcription saved: {output_filename}")
        return output_path
        
    except Exception as e:
        print_error(f"Error saving transcription: {str(e)}")
        return None

def main():
    """
    Main function to handle the interactive video processing
    """
    print_header()
    
    try:
        # Get participant directory
        participant_dir = get_participant_name()
        print_info(f"Working directory: {participant_dir}")
        
        # List video files
        video_files = list_video_files(participant_dir)
        display_video_files(video_files)
        
        if not video_files:
            print_warning("No MP4 files found. Exiting.")
            return
        
        # Get user selection
        selected_files = get_user_selection(video_files, max_selections=10)
        
        if not selected_files:
            print_info("No files selected for processing.")
            return
        
        print_separator()
        print(f"Starting optimized processing of {len(selected_files)} file(s)...")
        print_info(f"Optimization settings: {AUDIO_BITRATE} bitrate, {AUDIO_SAMPLE_RATE}Hz sample rate, {MAX_WORKERS} parallel workers")
        print_separator()
        
        # Process selected files
        processed_files = []
        failed_files = []
        
        for i, video_file in enumerate(selected_files, 1):
            print(f"\nProcessing file {i}/{len(selected_files)}: {os.path.basename(video_file)}")
            print_mini_separator()
            
            # Step 1: Extract audio from video
            audio_file = extract_audio_from_video(video_file)
            if not audio_file:
                failed_files.append(video_file)
                continue
            
            # Step 2: Transcribe audio
            transcription = transcribe_audio(audio_file)
            if not transcription:
                failed_files.append(video_file)
                continue
            
            # Step 3: Display transcription
            print(f"\nTranscription:")
            print("-" * 40)
            print(transcription)
            print("-" * 40)
            
            # Step 4: Save transcription
            save_transcription(transcription, video_file, participant_dir)
            
            processed_files.append(video_file)
        
        # Print summary
        print_separator()
        print("PROCESSING SUMMARY")
        print_separator()
        
        print_success(f"Successfully processed: {len(processed_files)} file(s)")
        if failed_files:
            print_error(f"Failed processing: {len(failed_files)} file(s)")
        
        if processed_files:
            print(f"\nProcessed files:")
            for file in processed_files:
                print(f"  ✓ {os.path.basename(file)}")
        
        if failed_files:
            print(f"\nFailed files:")
            for file in failed_files:
                print(f"  ✗ {os.path.basename(file)}")
        
        print_separator()
        print("Optimized video processing completed!")
        
    except KeyboardInterrupt:
        print(f"\nOperation cancelled by user.")
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 