import openai
import logging
import json
from sklearn.metrics.pairwise import cosine_similarity

def analyze_email(text):
    prompt = f"""Analyze this email and return JSON with:
    - Primary intent (sales, support, billing, other)
    - Priority (high, medium, low)
    - Key entities (names, dates, amounts)
    - Multiple requests (list of individual requests)
    - Summary
    - Sentiment (positive, neutral, negative)

    Email: {text[:3000]}"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return json.loads(response.choices[0].message['content'])
    except Exception as e:
        logging.error(f"Error analyzing email: {e}")
        return {
            "primary_intent": "unknown",
            "priority": "medium",
            "summary": "No summary available.",
            "sentiment": "neutral",
            "key_entities": [],
            "multiple_requests": []
        }

def detect_duplicate(content, processed_hashes, similarity_threshold):
    try:
        embedding = openai.Embedding.create(
            input=content,
            model="text-embedding-ada-002"
        )['data'][0]['embedding']

        for existing in processed_hashes:
            if cosine_similarity([embedding], [existing])[0][0] > similarity_threshold:
                return True
        processed_hashes.add(tuple(embedding))
        return False
    except Exception as e:
        logging.error(f"Error in duplicate detection: {e}")
        return False
