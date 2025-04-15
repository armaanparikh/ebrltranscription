#!/usr/bin/env python3
import os
import sys
import argparse
from pydub import AudioSegment
import glob

def convert_to_mp3(input_file, output_file=None, bitrate="192k"):
    """
    Convert an audio file (WMA, DSS, etc.) to MP3 format
    
    Args:
        input_file (str): Path to the input audio file
        output_file (str, optional): Path to the output MP3 file. If not provided,
                                    it will use the same name with .mp3 extension
        bitrate (str, optional): Bitrate for the output MP3. Default is "192k"
    
    Returns:
        str: Path to the converted MP3 file
    """
    if not output_file:
        # Create output filename with same name but .mp3 extension
        output_file = os.path.splitext(input_file)[0] + '.mp3'
    
    print(f"Converting {input_file} to {output_file}...")
    
    try:
        # Load the audio file
        # For DSS files, we need to use ffmpeg directly through pydub
        file_ext = os.path.splitext(input_file)[1].lower()
        
        audio = AudioSegment.from_file(input_file)
        
        # Export as MP3
        audio.export(output_file, format="mp3", bitrate=bitrate)
        
        print(f"Conversion complete: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return None

def process_directory(input_dir, output_dir=None, bitrate="192k", recursive=False, file_types=None):
    """
    Convert audio files in a directory to MP3
    
    Args:
        input_dir (str): Input directory containing audio files
        output_dir (str, optional): Output directory for MP3 files
        bitrate (str, optional): Bitrate for the output MP3. Default is "192k"
        recursive (bool, optional): Whether to recursively process subdirectories
        file_types (list, optional): List of file extensions to convert. Default is ['.wma', '.dss']
    """
    # Default file types if not specified
    if file_types is None:
        file_types = ['.wma', '.dss']
        
    # Ensure input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Directory {input_dir} not found")
        return
    
    # Create output directory if it doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process each file type
    all_files = []
    for file_type in file_types:
        # Set up pattern for glob
        pattern = f"**/*{file_type}" if recursive else f"*{file_type}"
        
        # Find all matching files
        matching_files = glob.glob(os.path.join(input_dir, pattern), recursive=recursive)
        all_files.extend(matching_files)
    
    if not all_files:
        print(f"No files with extensions {', '.join(file_types)} found in {input_dir}")
        return
    
    print(f"Found {len(all_files)} files to convert")
    
    # Process each file
    for input_file in all_files:
        if output_dir:
            # Get relative path from input_dir to maintain directory structure
            rel_path = os.path.relpath(input_file, input_dir)
            # Change extension to .mp3
            rel_path_mp3 = os.path.splitext(rel_path)[0] + '.mp3'
            # Join with output_dir to get full output path
            output_file = os.path.join(output_dir, rel_path_mp3)
            # Ensure output directory exists (for subdirectories in recursive mode)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        else:
            output_file = None
        
        convert_to_mp3(input_file, output_file, bitrate)

def main():
    parser = argparse.ArgumentParser(description="Convert audio files (WMA, DSS) to MP3 format")
    parser.add_argument("input", help="Input audio file or directory containing audio files")
    parser.add_argument("-o", "--output", help="Output MP3 file or directory (optional)")
    parser.add_argument("-b", "--bitrate", default="192k", help="Output MP3 bitrate (default: 192k)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process subdirectories")
    parser.add_argument("-t", "--types", default="wma,dss", help="Comma-separated list of file extensions to convert (default: wma,dss)")
    
    args = parser.parse_args()
    
    # Parse file types
    file_types = [f".{ext.lower().strip()}" for ext in args.types.split(",")]
    
    # Check if input is a file or directory
    if os.path.isfile(args.input):
        # Check if input file has a supported extension
        ext = os.path.splitext(args.input)[1].lower()
        if ext not in file_types:
            print(f"Error: Input file must have one of these extensions: {', '.join(ext[1:] for ext in file_types)}")
            return
        
        # Convert single file
        convert_to_mp3(args.input, args.output, args.bitrate)
    elif os.path.isdir(args.input):
        # Convert all matching files in directory
        process_directory(args.input, args.output, args.bitrate, args.recursive, file_types)
    else:
        print(f"Error: {args.input} not found")

if __name__ == "__main__":
    main() 