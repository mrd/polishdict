#!/usr/bin/env python3
"""
Polish Dictionary Web Application
A Flask-based web interface for the Polish dictionary
"""

from flask import Flask, render_template, request, jsonify
import polishdict
from polishdict.api import PolishDictionaryAPI

app = Flask(__name__)


def check_and_follow_lemma(api, word_data, original_word, declension_mode):
    """Check if word_data contains a lemma reference and fetch it if needed"""
    if not declension_mode:
        return word_data

    polish_data = word_data.get('polish_wiktionary')
    english_data = word_data.get('english_wiktionary')

    # Try to find a lemma from either source
    lemma = None
    if polish_data and polish_data.get('lemma'):
        lemma = polish_data['lemma']
    elif english_data and english_data.get('lemma'):
        lemma = english_data['lemma']

    # If we have a lemma and no declension tables, look up the lemma
    has_declension = (polish_data and polish_data.get('declension')) or \
                   (english_data and english_data.get('declension'))

    if lemma and not has_declension:
        # Fetch the lemma
        lemma_data = api.fetch_word(lemma)
        lemma_data['display_word'] = f"{lemma} (from form: {word_data.get('word', original_word)})"
        return lemma_data

    return word_data


@app.route('/')
def index():
    """Main page with search form"""
    return render_template('index.html')


@app.route('/lookup', methods=['POST'])
def lookup():
    """Handle word lookup requests"""
    data = request.get_json()
    word = data.get('word', '').strip()
    show_declension = data.get('show_declension', False)

    if not word:
        return jsonify({'error': 'No word provided'}), 400

    try:
        api = PolishDictionaryAPI(verbose=False)
        word_data = api.fetch_word(word)

        # Check for lemma and follow if in declension mode
        word_data = check_and_follow_lemma(api, word_data, word, show_declension)

        # Check if we got any results
        has_results = False
        if word_data.get('polish_wiktionary') and word_data['polish_wiktionary'].get('definitions'):
            has_results = True
        if word_data.get('english_wiktionary') and word_data['english_wiktionary'].get('definitions'):
            has_results = True

        # Try fuzzy search if no results
        if not has_results and any(c in word.lower() for c in 'acelnosyz'):
            from polishdict.cli import generate_polish_variants
            variants = generate_polish_variants(word)

            for variant in variants[:5]:  # Try first 5 variants
                variant_data = api.fetch_word(variant)

                variant_has_results = False
                if variant_data.get('polish_wiktionary') and variant_data['polish_wiktionary'].get('definitions'):
                    variant_has_results = True
                if variant_data.get('english_wiktionary') and variant_data['english_wiktionary'].get('definitions'):
                    variant_has_results = True

                if variant_has_results:
                    word_data = variant_data
                    word_data['word'] = f"{variant} (from {word})"
                    word_data = check_and_follow_lemma(api, word_data, variant, show_declension)
                    break

        return jsonify({
            'success': True,
            'word_data': word_data,
            'show_declension': show_declension
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
