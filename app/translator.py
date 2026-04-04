import re
import html
from typing import Optional
from deep_translator import GoogleTranslator

def parse_srt(content: str) -> list[tuple[str, str, str]]:
    """
    Parse SRT subtitle file content.
    Returns list of (index, timecode, text) tuples.
    """
    blocks = re.split(r'\n\n+', content.strip())
    subtitles = []

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            index = lines[0].strip()
            timecode = lines[1].strip()
            text = '\n'.join(lines[2:])
            subtitles.append((index, timecode, text))

    return subtitles

def format_srt(subtitles: list[tuple[str, str, str]]) -> str:
    """Convert subtitles back to SRT format."""
    output = []
    for index, timecode, text in subtitles:
        output.append(f"{index}\n{timecode}\n{text}\n")
    return '\n'.join(output)

def clean_text_for_translation(text: str) -> str:
    """Clean text before translation, preserving structure."""
    # Remove HTML tags but keep text
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    text = html.unescape(text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def translate_srt(subtitle_path: str, target_lang: str = 'zh-CN') -> str:
    """
    Translate SRT subtitles to target language with improved quality.
    Returns path to translated subtitle file.
    """
    # Read original subtitle
    with open(subtitle_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse subtitles
    subtitles = parse_srt(content)

    if not subtitles:
        raise ValueError("No subtitles found in file")

    # Initialize translator
    translator = GoogleTranslator(source='en', target='zh-CN')

    translated_subtitles = []
    for index, timecode, text in subtitles:
        # Clean and prepare text
        original_text = text
        text = clean_text_for_translation(text)

        if not text:
            translated_subtitles.append((index, timecode, original_text))
            continue

        try:
            # Translate directly - Google Translate handles the translation
            translated = translator.translate(text)

            # If translation fails or returns empty, keep original
            if not translated:
                translated = original_text

            translated_subtitles.append((index, timecode, translated))
        except Exception as e:
            # On error, keep original text
            translated_subtitles.append((index, timecode, original_text))

    # Generate translated file path
    base, ext = subtitle_path.rsplit('.', 1)
    lang_code = target_lang if target_lang else 'zh-CN'
    translated_path = f"{base}.{lang_code}.{ext}"

    # Write translated subtitles
    with open(translated_path, 'w', encoding='utf-8') as f:
        f.write(format_srt(translated_subtitles))

    return translated_path

def detect_and_translate(subtitle_path: str) -> Optional[str]:
    """
    Detect subtitle language and translate if English.
    Returns path to translated file or original if not English.
    """
    # Simple language detection: check for common English words
    with open(subtitle_path, 'r', encoding='utf-8') as f:
        sample = f.read(5000)

    # Check if it looks like English
    english_indicators = ['the', 'is', 'are', 'and', 'to', 'of', 'a', 'in', 'that', 'it']
    sample_lower = sample.lower()
    english_count = sum(1 for word in english_indicators if word in sample_lower)

    # If many English indicators, likely English
    if english_count >= 3:
        return translate_srt(subtitle_path, 'zh-CN')

    return None  # Don't translate if not detected as English