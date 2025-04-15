# Audio Transcription with OpenAI Whisper

A Python project that uses OpenAI's Whisper model to transcribe audio files.

## Setup

1. Clone this repository
2. Install the required dependencies:
```
pip install -r requirements.txt
```
3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```
4. Place your audio files in the `audio_files/` directory

## Usage

### Transcription

You can place your audio files in the `audio_files/` directory and then simply refer to them by filename:

```
python transcribe.py filename.mp3
```

Or provide a full path to an audio file anywhere on your system:

```
python transcribe.py /path/to/your/audio/file.mp3
```

You can also specify an output file for the transcription:

```
python transcribe.py filename.mp3 -o transcription.txt
```

To use a different audio files directory:

```
python transcribe.py filename.mp3 -d your_audio_directory
```

### Audio Format Conversion

This project includes a tool to convert various audio formats (WMA, DSS) to MP3:

#### Convert a single file:

```
python wma.py your_file.wma
python wma.py your_file.dss
```

#### Convert a single file with custom output path:

```
python wma.py your_file.wma -o output.mp3
```

#### Convert all supported files in a directory:

```
python wma.py your_directory/
```

#### Convert all supported files in a directory with a custom output directory:

```
python wma.py your_directory/ -o output_directory/
```

#### Convert all files including in subdirectories:

```
python wma.py your_directory/ -r
```

#### Specify a custom bitrate for the MP3 output:

```
python wma.py your_file.wma -b 320k
```

#### Convert only specific file types:

```
python wma.py your_directory/ -t wma,dss,wav
```

## Interactive Usage

Run the interactive sample script:

```
python sample_usage.py
```

## Features

- Transcribes audio files using OpenAI's Whisper model
- Automatically converts audio to the required MP3 format using pydub
- Supports saving transcriptions to a text file
- Environment variables for secure API key storage
- Dedicated `audio_files/` directory for organizing your audio files
- Audio format conversion utility (WMA, DSS to MP3)

## Supported File Formats

The transcription tool can handle various audio formats including:
- MP3
- WAV
- FLAC
- OGG
- WMA (will be automatically converted to MP3)
- DSS (will be automatically converted to MP3)
- and more (supported by pydub/ffmpeg) 