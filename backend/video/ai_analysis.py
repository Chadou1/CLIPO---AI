from typing import Dict, List
import re
from collections import Counter

def calculate_viral_score_heuristic(transcript_segment: str, context: Dict = None) -> float:
    """
    Calculate viral score using heuristic analysis (100% FREE - no API needed)
    Analyzes text patterns, keywords, and engagement indicators
    """
    
    score = 50.0  # Base score
    text_lower = transcript_segment.lower()
    
    # 1. Hook keywords detection (+20 points max)
    hook_keywords = [
        'imagine', 'what if', 'did you know', 'you won\'t believe',
        'shocking', 'secret', 'never', 'always', 'warning',
        'breaking', 'urgent', 'exclusive', 'revealed', 'exposed',
        'hack', 'trick', 'tip', 'mistake', 'avoid', 'must',
        'incredible', 'amazing', 'unbelievable', 'insane'
    ]
    
    hook_count = sum(1 for keyword in hook_keywords if keyword in text_lower)
    score += min(hook_count * 5, 20)
    
    # 2. Question marks (engagement) (+10 points max)
    question_count = text_lower.count('?')
    score += min(question_count * 5, 10)
    
    # 3. Exclamation marks (energy) (+10 points max)
    exclamation_count = text_lower.count('!')
    score += min(exclamation_count * 3, 10)
    
    # 4. Numbers (specificity) (+5 points max)
    number_count = len(re.findall(r'\b\d+\b', text_lower))
    score += min(number_count * 2, 5)
    
    # 5. Call to action words (+10 points max)
    cta_keywords = [
        'watch', 'see', 'look', 'check', 'learn', 'discover',
        'find out', 'click', 'share', 'comment', 'like', 'subscribe'
    ]
    cta_count = sum(1 for keyword in cta_keywords if keyword in text_lower)
    score += min(cta_count * 3, 10)
    
    # 6. Emotional words (+10 points max)
    emotional_keywords = [
        'love', 'hate', 'angry', 'happy', 'sad', 'fear', 'excited',
        'worried', 'shocked', 'surprised', 'crazy', 'wild'
    ]
    emotion_count = sum(1 for keyword in emotional_keywords if keyword in text_lower)
    score += min(emotion_count * 3, 10)
    
    # 7. Length optimization (prefer 15-60 seconds of speech)
    word_count = len(transcript_segment.split())
    if 25 <= word_count <= 150:  # ~15-60 seconds at normal speech rate
        score += 5
    elif word_count < 10 or word_count > 200:
        score -= 10
    
    # 8. First-person perspective (+5 points)
    first_person = ['i ', 'my ', 'me ', 'i\'m', 'i\'ve']
    if any(word in text_lower for word in first_person):
        score += 5
    
    # 9. Story elements (+10 points)
    story_words = ['then', 'suddenly', 'next', 'after', 'before', 'when', 'story', 'time']
    story_count = sum(1 for word in story_words if word in text_lower)
    score += min(story_count * 2, 10)
    
    # 10. Controversy/debate words (+10 points)
    controversy_words = ['vs', 'versus', 'against', 'debate', 'argue', 'fight', 'battle']
    controversy_count = sum(1 for word in controversy_words if word in text_lower)
    score += min(controversy_count * 5, 10)
    
    # Ensure score is between 0 and 100
    return max(0, min(100, score))


def detect_hooks(transcript: List[Dict]) -> List[Dict]:
    """Detect hooks in transcript using pattern matching"""
    
    hooks = []
    for i, segment in enumerate(transcript):
        text = segment['text'].lower()
        
        # Hook patterns
        hook_patterns = [
            r'\b(imagine|what if|did you know)\b',
            r'\b(you won\'t believe|shocking|secret)\b',
            r'\b(never|always|warning)\b',
            r'\b(breaking|urgent|exclusive)\b',
            r'^(so|okay|alright|listen)',  # Start patterns
        ]
        
        has_hook = any(re.search(pattern, text) for pattern in hook_patterns)
        
        # Question detection
        if '?' in text:
            has_hook = True
        
        # Start of sentence with strong opener
        if i == 0 or (i < 3):
            has_hook = True
        
        if has_hook:
            hooks.append({
                'segment_index': i,
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'],
                'type': 'hook'
            })
    
    return hooks


def suggest_emojis(text: str) -> List[str]:
    """Suggest emojis based on text content using keyword matching"""
    
    emoji_map = {
        # Emotions
        'happy': '😊', 'sad': '😢', 'love': '❤️', 'angry': '😠',
        'surprised': '😲', 'shocked': '😱', 'excited': '🎉',
        'funny': '😂', 'laugh': '😂', 'lol': '😂',
        
        # Actions
        'fire': '🔥', 'money': '💰', 'cash': '💵', 'rich': '💎',
        'winner': '🏆', 'champion': '👑', 'king': '👑', 'queen': '👑',
        
        # Objects
        'car': '🚗', 'phone': '📱', 'computer': '💻', 'camera': '📷',
        'food': '🍕', 'pizza': '🍕', 'coffee': '☕',
        
        # Symbols
        'star': '⭐', 'heart': '❤️', 'check': '✅', 'warning': '⚠️',
        'question': '❓', 'idea': '💡', 'rocket': '🚀',
        
        # Common phrases
        'amazing': '🤩', 'incredible': '😍', 'perfect': '👌',
        'good': '👍', 'bad': '👎', 'yes': '✅', 'no': '❌'
    }
    
    text_lower = text.lower()
    emojis = []
    
    for keyword, emoji in emoji_map.items():
        if keyword in text_lower and emoji not in emojis:
            emojis.append(emoji)
            if len(emojis) >= 3:
                break
    
    # Default emojis if none found
    if not emojis:
        emojis = ['💯', '🔥', '✨']
    
    return emojis[:3]


def shorten_subtitle(text: str, max_words: int = 6) -> str:
    """Shorten subtitle text while maintaining meaning"""
    
    words = text.split()
    if len(words) <= max_words:
        return text
    
    # Remove filler words
    filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'literally']
    filtered_words = [w for w in words if w.lower() not in filler_words]
    
    if len(filtered_words) <= max_words:
        return ' '.join(filtered_words)
    
    # Take first max_words
    return ' '.join(filtered_words[:max_words]) + '...'
