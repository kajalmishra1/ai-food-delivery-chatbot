"""
Food Delivery FAQs Chatbot
---------------------------
"""

import json
import random
import re
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

INTENTS_FILE = Path(__file__).parent / "intents.json"

# Minimum cosine similarity score (0 to 1) required to accept a match.
# If the best match scores below this, the bot returns the fallback
# response instead of risking a wrong answer.
# Tune this: lower = bot answers more often but risks more mismatches.
#            higher = bot is more cautious, falls back more often.
CONFIDENCE_THRESHOLD = 0.30

FALLBACK_TAG = "fallback"


# ----------------------------------------------------------------------
# Text preprocessing
# ----------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Lowercase and strip punctuation so minor formatting differences
    (capitalization, '?', '!', etc.) don't affect matching."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)      # collapse multiple spaces
    return text


# Small stopword list used for the word-overlap safety check (separate
# from sklearn's built-in English stopword list used inside the vectorizer).
# Includes contraction artifacts (e.g. "what's" -> "whats" after punctuation
# stripping) so they aren't mistaken for meaningful/distinctive words.
_STOPWORDS = {
    "i", "a", "an", "the", "is", "are", "am", "my", "me", "to", "of",
    "for", "do", "does", "did", "in", "on", "at", "it", "this", "that",
    "and", "or", "but", "with", "you", "your", "please", "can", "will",
    "have", "has", "had", "be", "been", "was", "were", "what", "how",
    "when", "where", "why", "who",
    # contraction remnants after stripping the apostrophe
    "whats", "hows", "wheres", "whens", "whys", "whos",
    "cant", "dont", "doesnt", "didnt", "wont", "isnt", "arent",
    "im", "ive", "ill", "id", "youre", "youve", "youll",
}


def significant_words(text: str) -> set:
    """Returns the set of meaningful (non-stopword) words in a cleaned
    string. Used to double-check that a TF-IDF match is backed by real
    shared vocabulary, not just vector-space coincidence."""
    return {w for w in text.split() if w not in _STOPWORDS}


# ----------------------------------------------------------------------
# Chatbot class
# ----------------------------------------------------------------------

class FAQChatbot:
    def __init__(self, intents_path: Path = INTENTS_FILE,
                 threshold: float = CONFIDENCE_THRESHOLD):
        self.threshold = threshold
        self.intents = self._load_intents(intents_path)

        # Flatten into parallel lists: each pattern paired with its tag.
        self.patterns = []
        self.pattern_tags = []
        self.tag_to_responses = {}

        for intent in self.intents:
            tag = intent["tag"]
            self.tag_to_responses[tag] = intent.get("responses", [])

            if tag == FALLBACK_TAG:
                # fallback has no patterns to match against; skip vectorizing it
                continue

            for pattern in intent.get("patterns", []):
                cleaned = clean_text(pattern)
                if cleaned:  # skip empty strings
                    self.patterns.append(cleaned)
                    self.pattern_tags.append(tag)

        if not self.patterns:
            raise ValueError(
                "No patterns found in intents.json. Cannot build chatbot."
            )

        # Pre-compute the significant-word set for every pattern, used
        # for the word-overlap safety check in get_response().
        self.pattern_word_sets = [significant_words(p) for p in self.patterns]

        # Raw (pre-stopword-removal) word counts, used as a tiebreaker
        # when two patterns have identical scores AND identical
        # significant-word overlap (e.g. "order delivery problem" vs
        # "my order delivery has a problem" both reduce to the same 3
        # significant words once "my/has/a" are stripped as stopwords).
        # Comparing raw length preserves the sentence-structure
        # information that stopword removal otherwise destroys.
        self.pattern_raw_lengths = [len(p.split()) for p in self.patterns]

        # Fit TF-IDF on all known patterns.
        # ngram_range=(1, 2) captures both single words and two-word
        # phrases (e.g. "track order"), which helps short queries match well.
        # stop_words="english" removes filler words (what/is/the/my/etc.)
        # so unrelated questions don't falsely score high just because they
        # share common words with a real pattern (e.g. "what is the weather"
        # vs "what is the cost of delivery" both contain "what is the").
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.pattern_vectors = self.vectorizer.fit_transform(self.patterns)

        if FALLBACK_TAG not in self.tag_to_responses:
            # Safety net in case fallback tag is ever removed from JSON.
            self.tag_to_responses[FALLBACK_TAG] = [
                "Sorry, I didn't understand that. Could you rephrase?"
            ]

    @staticmethod
    def _load_intents(path: Path):
        if not path.exists():
            print(f"ERROR: Could not find intents file at: {path}")
            sys.exit(1)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: intents.json is not valid JSON: {e}")
            sys.exit(1)

        intents = data.get("intents")
        if not intents:
            print("ERROR: intents.json has no 'intents' key or it is empty.")
            sys.exit(1)
        return intents

    def get_response(self, user_input: str):
        """
        Returns (response_text, matched_tag, confidence_score).
        matched_tag will be 'fallback' if no confident match was found.

        Matching logic, in priority order:
        1. Cosine similarity score must be >= self.threshold.
        2. The input must share at least one real (non-stopword) word
           with the matched pattern (2+ words for weaker score matches,
           or 1 word only if score is very high). This rules out
           vector-space coincidences with no real shared vocabulary.
        3. Among qualifying candidates, prefer (in order): higher score,
           then MORE shared significant words (a pattern sharing 2 words
           is a stronger match than one sharing only 1, even at equal
           cosine score), then closest raw sentence length to the input
           (breaks remaining ties between equally-supported patterns).
        """
        cleaned_input = clean_text(user_input)
        input_words = significant_words(cleaned_input)

        if not cleaned_input:
            return (
                random.choice(self.tag_to_responses[FALLBACK_TAG]),
                FALLBACK_TAG,
                0.0,
            )

        input_vector = self.vectorizer.transform([cleaned_input])
        similarities = cosine_similarity(input_vector, self.pattern_vectors)[0]

        # Consider a wider pool of candidates (not just the single top match)
        # because ties at the same cosine score are common when only one
        # short, distinctive word overlaps (e.g. "order" alone can tie
        # across track_order, reorder, and wrong_item patterns).
        top_n = min(20, len(similarities))
        top_indices = similarities.argsort()[::-1][:top_n]

        input_raw_length = len(cleaned_input.split())
        candidates = []  # (score, shared_word_count, -length_diff, idx)
        for idx in top_indices:
            score = similarities[idx]
            if score < self.threshold:
                break  # scores sorted descending; nothing further qualifies

            shared_words = input_words & self.pattern_word_sets[idx]

            # Require either:
            #  - 2+ shared significant words (strong, reliable overlap), or
            #  - exactly 1 shared word but a very high score (>= 0.85),
            #    to avoid weak matches like "how's it going" coincidentally
            #    sharing one generic word (e.g. "going") with an unrelated
            #    pattern like "payment not going through".
            if len(shared_words) >= 2 or (len(shared_words) == 1 and score >= 0.85):
                length_diff = abs(self.pattern_raw_lengths[idx] - input_raw_length)
                candidates.append(
                    (score, len(shared_words), -length_diff, idx)
                )

        if not candidates:
            best_score = float(similarities[top_indices[0]]) if top_n else 0.0
            return (
                random.choice(self.tag_to_responses[FALLBACK_TAG]),
                FALLBACK_TAG,
                best_score,
            )

        # Sort by score desc, then shared-word-count desc (more shared
        # words beats fewer, even at equal score), then closest raw
        # sentence-length match (since -length_diff is negated, sorting
        # descending naturally picks the smallest length difference).
        candidates.sort(key=lambda c: (c[0], c[1], c[2]), reverse=True)
        best_score, _, _, best_idx = candidates[0]
        tag = self.pattern_tags[best_idx]
        response = random.choice(self.tag_to_responses[tag])
        return response, tag, float(best_score)


# ----------------------------------------------------------------------
# CLI loop for quick testing
# ----------------------------------------------------------------------

def main():
    bot = FAQChatbot()

    # Set DEBUG = True while testing to see the matched tag + confidence
    # score for every reply. This is the easiest way to tune the
    # threshold and spot mismatches. Set to False before sharing the bot.
    DEBUG = True

    print("Food Delivery FAQ Chatbot (type 'quit' or 'exit' to stop)")
    print("-" * 55)

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break

        if user_input.lower() in ("quit", "exit", "bye"):
            print("Bot: Goodbye! Have a great day. 👋")
            break

        if not user_input:
            continue

        response, tag, score = bot.get_response(user_input)

        if DEBUG:
            print(f"Bot: {response}   [tag: {tag} | confidence: {score:.2f}]")
        else:
            print(f"Bot: {response}")


if __name__ == "__main__":
    main()
