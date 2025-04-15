from transcribe import transcribe_audio, resolve_file_path, AUDIO_DIR
import os

def main():
    """
    Sample script showing how to use the transcription functionality
    from another Python script.
    """
    # Example: Transcribe an audio file
    print(f"You can place audio files in the '{AUDIO_DIR}/' directory for easy access.")
    audio_file = input("Enter the path to your audio file: ")
    
    # Resolve the file path
    resolved_path = resolve_file_path(audio_file, AUDIO_DIR)
    
    if not os.path.exists(resolved_path):
        print(f"Error: File {audio_file} not found")
        print(f"Checked in current directory and {os.path.abspath(AUDIO_DIR)}")
        return
    
    print(f"Found audio file at: {resolved_path}")
    print("Starting transcription...")
    transcription = transcribe_audio(resolved_path, AUDIO_DIR)
    
    if transcription:
        print("\nTranscription Result:")
        print("--------------------")
        print(transcription)
        
        # Optionally save to a file
        save_option = input("\nDo you want to save this transcription to a file? (y/n): ")
        if save_option.lower() == 'y':
            output_file = input("Enter output file name (or press Enter for default): ")
            if not output_file:
                output_file = os.path.splitext(os.path.basename(resolved_path))[0] + "_transcription.txt"
            
            with open(output_file, 'w') as f:
                f.write(transcription)
            print(f"Transcription saved to {output_file}")

if __name__ == "__main__":
    main() 