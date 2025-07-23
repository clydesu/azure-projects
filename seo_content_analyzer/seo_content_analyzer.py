import re
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import textstat
from collections import Counter

load_dotenv()

def create_text_analytics_client():
    endpoint = os.environ.get("AZURE_LANGUAGE_ENDPOINT")
    key = os.environ.get("AZURE_LANGUAGE_KEY")
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def clean_key_phrases(raw_phrases, content):
    # Lowercase, strip, remove very long/verbose, group by frequency
    cleaned = [p.lower().strip() for p in raw_phrases if 2 <= len(p) <= 60]
    # Remove phrases that are only one word or too generic
    cleaned = [p for p in cleaned if len(p.split()) > 1 and p not in {"final chance", "everything", "each day", "each 24 hour"}]
    phrase_counts = Counter(cleaned)
    # Extra boost for phrases in the first 300 chars (intro) or in headings
    intro = content[:min(300, len(content))].lower()
    headings = re.findall(r'^\s*#+\s+(.+)', content, re.MULTILINE)
    for phrase in phrase_counts:
        if phrase in intro:
            phrase_counts[phrase] += 2  # boost for early appearance
        if any(phrase in h.lower() for h in headings):
            phrase_counts[phrase] += 2  # boost for heading appearance
    # Remove overlapping/verbose phrases (keep shortest unique)
    common_phrases = [
        phrase for phrase, count in phrase_counts.most_common(65)
        if count > 1 or len(phrase.split()) > 1
    ]
    final_phrases = []
    for phrase in common_phrases:
        if not any(phrase != other and phrase in other for other in common_phrases):
            final_phrases.append(phrase)
    # Only return top 8 for display
    return final_phrases[:8]

def filter_entities(raw_entities):
    # Normalize entities and filter by type and confidence
    good_types = {"Organization", "Person", "Location", "Event", "Product", "Skill"}
    normalized = []
    for e in raw_entities:
        text = e['text']
        # Normalize and filter out generic or low-confidence entities
        if e.get('category') in good_types and float(e.get('confidenceScore', 0)) >= 0.8:
            # Exclude numbers, dates, and generic terms
            if not re.fullmatch(r'\d+|each day|each 24 hour|everything|final chance', text.lower()):
                normalized.append(text)
    # Only return top 8 unique entities
    return list(dict.fromkeys(normalized))[:8]

def get_seo_insights(content):
    client = create_text_analytics_client()
    # 1. Key Phrase Extraction (Azure uses NER, key phrase extraction, TF-IDF style weighting)
    key_phrases_raw = client.extract_key_phrases([content])[0].key_phrases
    key_phrases = clean_key_phrases(key_phrases_raw, content)

    # 2. Sentiment Analysis
    sentiment_result = client.analyze_sentiment([content])[0]
    sentiment = sentiment_result.sentiment
    sentiment_scores = sentiment_result.confidence_scores

    # 3. Entity Recognition (Azure does NER + normalization)
    entities_raw = [
        {
            "text": e.text,
            "category": e.category,
            "confidenceScore": e.confidence_score
        }
        for e in client.recognize_entities([content])[0].entities
    ]
    entities = filter_entities(entities_raw)

    # 4. Readability & Grade Level
    readability = int(round(textstat.flesch_reading_ease(content)))  # Ensure whole number
    grade_level = textstat.text_standard(content)

    # 5. Content Structure Feedback
    headings = len(re.findall(r'^\s*#+\s+\w+', content, re.MULTILINE))  # Markdown headings
    bullet_points = len(re.findall(r'^\s*[-*+]\s+\w+', content, re.MULTILINE))
    short_paragraphs = sum(1 for p in content.split('\n\n') if len(p.split()) < 40)
    structure_feedback = {
        "headings": headings,
        "bullet_points": bullet_points,
        "short_paragraphs": short_paragraphs
    }

    # Additional: Tone Consistency (simple check: are all sentences same sentiment?)
    sentences = re.split(r'(?<=[.!?])\s+', content)
    sentence_sentiments = [client.analyze_sentiment([s])[0].sentiment for s in sentences if s.strip()]
    tone_consistent = len(set(sentence_sentiments)) == 1 if sentence_sentiments else True

    # Additional: Clarity Suggestions (long sentences > 25 words)
    long_sentences = [s for s in sentences if len(s.split()) > 25]

    # Additional: Content Gaps (suggest if key phrases/entities are missing from intro/conclusion)
    intro = content[:min(300, len(content))]
    conclusion = content[-min(300, len(content)):]
    missing_in_intro = [kp for kp in key_phrases if kp not in intro]
    missing_in_conclusion = [kp for kp in key_phrases if kp not in conclusion]

    # Additional: Call-to-Action Detection
    cta_phrases = ["contact us", "learn more", "sign up", "get started", "buy now", "read more", "subscribe"]
    cta_found = any(phrase in content.lower() for phrase in cta_phrases)

    # Note: Plagiarism/originality check would require a third-party API, not included here.

    return {
        "key_phrases": key_phrases,
        "sentiment": sentiment,
        "sentiment_scores": {
            "positive": sentiment_scores.positive,
            "neutral": sentiment_scores.neutral,
            "negative": sentiment_scores.negative
        },
        "entities": entities,
        "readability": readability,
        "grade_level": grade_level,
        "structure_feedback": structure_feedback,
        "tone_consistent": tone_consistent,
        "long_sentences": long_sentences,
        "missing_key_phrases_intro": missing_in_intro,
        "missing_key_phrases_conclusion": missing_in_conclusion,
        "call_to_action_found": cta_found
    }