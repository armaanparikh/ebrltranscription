import docx
from difflib import SequenceMatcher
import sys
import os
import string
import re
import unicodedata

# Define the base path for document comparison
BASE_PATH = "/Users/armaanparikh/Documents/EBRL/RC"

def normalize_word(word):
    """Remove all Unicode punctuation and lowercase the word."""
    word = unicodedata.normalize('NFKC', word)
    word = ''.join(ch for ch in word if not unicodedata.category(ch).startswith('P'))
    return word.lower()

def get_participant_directory():
    """Get participant name and return the full directory path."""
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

def read_docx(file_path):
    """Read a .docx file and return its text content."""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return ' '.join(full_text)
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        sys.exit(1)

def compare_texts(text1, text2):
    """Compare two texts and return similarity metrics."""
    # Split texts into words and normalize them (for positional comparison)
    words1 = [normalize_word(word) for word in text1.split()]
    words2 = [normalize_word(word) for word in text2.split()]
    
    # Number of matches: number of words in the LCS (used as numerator for word order similarity)
    matcher = SequenceMatcher(None, words1, words2)
    num_matches = sum(triple.size for triple in matcher.get_matching_blocks()[:-1])  # Exclude dummy block
    total_words = max(len(words1), len(words2))
    
    # Number of different words: all non-matching words, including extras at the end, divided by 2
    different_words = ((len(words1) + len(words2)) - 2 * num_matches) / 2
    
    # Sequence similarity using normalized text
    normalized_text1 = ' '.join(words1)
    normalized_text2 = ' '.join(words2)
    sequence_similarity = SequenceMatcher(None, normalized_text1, normalized_text2).ratio()
    
    # Word order similarity using normalized words
    word_order_similarity = matcher.ratio()
    
    return {
        'total_words': total_words,
        'num_matches': num_matches,
        'different_words': different_words,
        'sequence_similarity': sequence_similarity,
        'word_order_similarity': word_order_similarity
    }

def list_available_files(directory):
    """List all .docx and .txt files in the specified directory and return the list, excluding files that start with ~."""
    files = [file for file in os.listdir(directory) if (file.endswith('.docx') or file.endswith('.txt')) and not file.startswith('~')]
    print("\nAvailable .docx/.txt files in the directory:")
    for idx, file in enumerate(files, 1):
        print(f"  {idx}. {file}")
    return files

def get_valid_file_path(directory, prompt, files=None):
    """Get a valid file path from user input, allowing selection by number."""
    if files is None:
        files = list_available_files(directory)
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
            if not filename.endswith('.docx'):
                filename += '.docx'
            full_path = os.path.join(directory, filename)
            if os.path.exists(full_path):
                return full_path
            else:
                print(f"File not found: {filename}")
                print("Please choose from the available files listed above.")

def read_file(file_path):
    """Read a .docx or .txt file and return its text content."""
    if file_path.endswith('.docx'):
        return read_docx(file_path)
    elif file_path.endswith('.txt'):
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            sys.exit(1)
    else:
        print(f"Unsupported file type: {file_path}")
        sys.exit(1)

def clean_text(text):
    """Remove all occurrences of 'inaudible' (case-insensitive, with or without punctuation) from the text."""
    return re.sub(r'\binaudible\b[.,;:!?"\'\-]*', '', text, flags=re.IGNORECASE)

def contraction_map():
    # Map expanded forms to contractions (normalized, no punctuation)
    return {
        'they are': 'theyre',
        'we are': 'were',
        'you are': 'youre',
        'i am': 'im',
        'do not': 'dont',
        'does not': 'doesnt',
        'did not': 'didnt',
        'is not': 'isnt',
        'are not': 'arent',
        'was not': 'wasnt',
        'were not': 'werent',
        'have not': 'havent',
        'has not': 'hasnt',
        'had not': 'hadnt',
        'will not': 'wont',
        'would not': 'wouldnt',
        'should not': 'shouldnt',
        'could not': 'couldnt',
        'cannot': 'cant',
        'can not': 'cant',
        'it is': 'its',
        'it will': 'itll',
        'that is': 'thats',
        'there is': 'theres',
        'what is': 'whats',
        'who is': 'whos',
        'let us': 'lets',
        'i will': 'ill',
        'you will': 'youll',
        'he will': 'hell',
        'she will': 'shell',
        'we will': 'well',
        'they will': 'theyll',
        'i have': 'ive',
        'you have': 'youve',
        'we have': 'weve',
        'they have': 'theyve',
        'should have': 'shouldve',
        'would have': 'wouldve',
        'could have': 'couldve',
        'might have': 'mightve',
        'must have': 'mustve',
        'i would': 'id',
        'you would': 'youd',
        'he would': 'hed',
        'she would': 'shed',
        'we would': 'wed',
        'they would': 'theyd',
        'i had': 'id',
        'you had': 'youd',
        'he had': 'hed',
        'she had': 'shed',
        'we had': 'wed',
        'they had': 'theyd',
        # General English contractions
        "aren't": "arent",
        "can't": "cant",
        "couldn't": "couldnt",
        "didn't": "didnt",
        "doesn't": "doesnt",
        "don't": "dont",
        "hadn't": "hadnt",
        "hasn't": "hasnt",
        "haven't": "havent",
        "he'd": "hed",
        "he'll": "hell",
        "he's": "hes",
        "i'd": "id",
        "i'll": "ill",
        "i'm": "im",
        "i've": "ive",
        "isn't": "isnt",
        "it'd": "itd",
        "it'll": "itll",
        "it's": "its",
        "let's": "lets",
        "mightn't": "mightnt",
        "mustn't": "mustnt",
        "shan't": "shant",
        "she'd": "shed",
        "she'll": "shell",
        "she's": "shes",
        "shouldn't": "shouldnt",
        "that's": "thats",
        "there's": "theres",
        "they'd": "theyd",
        "they'll": "theyll",
        "they're": "theyre",
        "they've": "theyve",
        "we'd": "wed",
        "we're": "were",
        "we've": "weve",
        "weren't": "werent",
        "what'll": "whatll",
        "what're": "whatre",
        "what's": "whats",
        "what've": "whatve",
        "where's": "wheres",
        "who'd": "whod",
        "who'll": "wholl",
        "who're": "whore",
        "who's": "whos",
        "who've": "whove",
        "won't": "wont",
        "wouldn't": "wouldnt",
        "you'd": "youd",
        "you'll": "youll",
        "you're": "youre",
        "you've": "youve",
    }

def map_expanded_to_contraction(text):
    """Replace expanded forms with contractions in the text (normalized, no punctuation)."""
    mapping = contraction_map()
    # Normalize text for matching (remove punctuation, lowercase)
    def normalize_for_map(s):
        s = unicodedata.normalize('NFKC', s)
        s = ''.join(ch for ch in s if not unicodedata.category(ch).startswith('P'))
        return s.lower()
    text_norm = normalize_for_map(text)
    for expanded, contraction in mapping.items():
        expanded_norm = normalize_for_map(expanded)
        text_norm = text_norm.replace(expanded_norm, contraction)
    return text_norm

def split_compound_words(text):
    """Split relevant compound words into separated forms for better matching (case-insensitive, word boundaries)."""
    compounds = {
        # Amphibian/toad-related
        'coldblooded': 'cold blooded',
        'warmblooded': 'warm blooded',
        'toadstool': 'toad stool',
        'bullfrog': 'bull frog',
        'tadpole': 'tad pole',
        'treefrog': 'tree frog',
        'springpeeper': 'spring peeper',
        'woodfrog': 'wood frog',
        'spadefoot': 'spade foot',
        'newtlike': 'newt like',
        'frogspawn': 'frog spawn',
        'pondweed': 'pond weed',
        'nighttime': 'night time',
        'seethrough': 'see through',
        'waterhole': 'water hole',
        'rainforest': 'rain forest',
        'sunbaked': 'sun baked',
        'backbone': 'back bone',
        'eggsac': 'egg sac',
        'overwinter': 'over winter',
        'underwater': 'under water',
        'daylight': 'day light',
        'earthworm': 'earth worm',
        'insectlike': 'insect like',
        'mouthpart': 'mouth part',
        'tailfin': 'tail fin',
        'webbedfeet': 'webbed feet',
        'webbedfoot': 'webbed foot',
        # General English compound words
        'notebook': 'note book',
        'blackboard': 'black board',
        'classroom': 'class room',
        'sunflower': 'sun flower',
        'football': 'foot ball',
        'basketball': 'basket ball',
        'baseball': 'base ball',
        'playground': 'play ground',
        'schoolyard': 'school yard',
        'lunchbox': 'lunch box',
        'toothbrush': 'tooth brush',
        'hairbrush': 'hair brush',
        'bedroom': 'bed room',
        'bathroom': 'bath room',
        'livingroom': 'living room',
        'diningroom': 'dining room',
        'bookshelf': 'book shelf',
        'bookshelves': 'book shelves',
        'snowman': 'snow man',
        'raincoat': 'rain coat',
        'fireman': 'fire man',
        'policeman': 'police man',
        'mailbox': 'mail box',
        'sandbox': 'sand box',
        'doghouse': 'dog house',
        'catfish': 'cat fish',
        'goldfish': 'gold fish',
        'starfish': 'star fish',
        'cupcake': 'cup cake',
        'birthdaycake': 'birthday cake',
        'pancake': 'pan cake',
        'cheesecake': 'cheese cake',
        'popcorn': 'pop corn',
        'peanutbutter': 'peanut butter',
        'strawberry': 'straw berry',
        'blueberry': 'blue berry',
        'raspberry': 'rasp berry',
        'blackberry': 'black berry',
        'greenhouse': 'green house',
        'lighthouse': 'light house',
        'wheelchair': 'wheel chair',
        'newspaper': 'news paper',
        'airport': 'air port',
        'rainbow': 'rain bow',
        'moonlight': 'moon light',
        'sunlight': 'sun light',
        'starlight': 'star light',
        'daydream': 'day dream',
        'nightmare': 'night mare',
        'overcoat': 'over coat',
        'underdog': 'under dog',
        'overhead': 'over head',
        'underfoot': 'under foot',
        'upstairs': 'up stairs',
        'downstairs': 'down stairs',
        'outdoors': 'out doors',
        'indoors': 'in doors',
        'outfield': 'out field',
        'infield': 'in field',
        'outlaw': 'out law',
        'inlet': 'in let',
        'outlet': 'out let',
        'upset': 'up set',
        'downpour': 'down pour',
        'outcome': 'out come',
        'income': 'in come',
        'outbreak': 'out break',
        'input': 'in put',
        'output': 'out put',
        'outlook': 'out look',
        'insight': 'in sight',
        'oversight': 'over sight',
        'oversee': 'over see',
        'overdo': 'over do',
        'undo': 'un do',
        'redo': 're do',
        'preview': 'pre view',
        'review': 're view',
        'replay': 're play',
        'retake': 're take',
        'rebuild': 're build',
        'recycle': 're cycle',
        'recharge': 're charge',
        'rearrange': 're arrange',
        'reappear': 're appear',
        'reapply': 're apply',
        'reconnect': 're connect',
        'reconsider': 're consider',
        'reconstruct': 're construct',
        'recount': 're count',
        'recover': 're cover',
        'recreate': 're create',
        'redefine': 're define',
        'rediscover': 're discover',
        'reenter': 're enter',
        'refill': 're fill',
        'refocus': 're focus',
        'refresh': 're fresh',
        'regain': 're gain',
        'regrow': 're grow',
        'rehash': 're hash',
        'reheat': 're heat',
        'rejoin': 're join',
        'relive': 're live',
        'remake': 're make',
        'rematch': 're match',
        'remove': 're move',
        'rename': 're name',
        'renew': 're new',
        'reopen': 're open',
        'replace': 're place',
        'replay': 're play',
        'report': 're port',
        'resend': 're send',
        'reset': 're set',
        'resign': 're sign',
        'resist': 're sist',
        'resolve': 're solve',
        'resort': 're sort',
        'resource': 're source',
        'respect': 're spect',
        'respond': 're spond',
        'restart': 're start',
        'restore': 're store',
        'restrict': 're strict',
        'result': 're sult',
        'resume': 're sume',
        'retake': 're take',
        'retell': 're tell',
        'retire': 're tire',
        'return': 're turn',
        'reuse': 're use',
        'reveal': 're veal',
        'revenge': 're venge',
        'reverse': 're verse',
        'review': 're view',
        'revise': 're vise',
        'revisit': 're visit',
        'revoke': 're voke',
        'reward': 're ward',
        'rewind': 're wind',
        'rewrite': 're write',
    }
    for compound, split in compounds.items():
        text = re.sub(rf'\b{compound}\b', split, text, flags=re.IGNORECASE)
    return text

def main():
    # Check if base path exists
    if not os.path.exists(BASE_PATH):
        print(f"Error: Base path {BASE_PATH} does not exist!")
        sys.exit(1)

    print("\n=== Document Comparison Tool ===")
    print("Note: Comparisons ignore capitalization and punctuation")
    
    # Get participant directory
    participant_dir = get_participant_directory()
    print(f"\nWorking directory: {participant_dir}")
    
    # List available files
    available_files = list_available_files(participant_dir)
    # Fallback: check /Transcription subdirectory if no files found
    if not available_files:
        transcription_subdir = os.path.join(participant_dir, 'Transcription')
        if os.path.exists(transcription_subdir):
            available_files = list_available_files(transcription_subdir)
            participant_dir = transcription_subdir
    if not available_files:
        print("No .docx files found in the participant's directory!")
        sys.exit(1)
    
    # Get file paths from user using numbered selection
    file1 = get_valid_file_path(participant_dir, "\nEnter the number for the first .docx file: ", available_files)
    file2 = get_valid_file_path(participant_dir, "Enter the number for the second .docx file: ", available_files)
    
    # Read documents
    print("\nReading documents...")
    text1 = clean_text(read_file(file1))
    text2 = clean_text(read_file(file2))
    # Map expanded forms to contractions for analysis
    text1 = map_expanded_to_contraction(text1)
    text2 = map_expanded_to_contraction(text2)
    # Split compound words for better matching
    text1 = split_compound_words(text1)
    text2 = split_compound_words(text2)
    
    # Compare texts
    print("\nAnalyzing documents...")
    results = compare_texts(text1, text2)
    
    # Print results
    print("\n=== Comparison Results ===")
    print(f"Total words in longer document: {results['total_words']}")
    print(f"Number of matches: {results['num_matches']}")
    print(f"Number of different words: {results['different_words']}")
    print(f"Word order similarity: {results['word_order_similarity'] * 100:.2f}%")

if __name__ == "__main__":
    main() 