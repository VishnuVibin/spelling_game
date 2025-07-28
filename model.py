import re
import json
import os
import random
import together

# Option 1: set in code
together.api_key = "tgp_v1_1CNqrh5Ne89fBCTCLr5_BOTTn2dD3G46guPqsrJ85F8"

MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

CACHE_FILE = "cache.json"
cache = {}

def load_cache():
    global cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            try:
                cache = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {CACHE_FILE} is corrupted or empty. Starting with empty cache.")
                cache = {}
    else:
        print(f"No cache file found at {CACHE_FILE}. Starting with empty cache.")
        cache = {}

def save_cache():
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=4)

# Load cache when the module is imported
load_cache()

def call_llama(prompt, expect_suffix_objects=False):
    response = together.Complete.create(
        model=MODEL_NAME,
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
        top_p=0.9
    )
    raw_answer = response['choices'][0]['text']
    print("=== Raw model answer ===")
    print(raw_answer)

    try:
        if expect_suffix_objects:
            data = json.loads(raw_answer)
            suffix_objs = data.get('suffixes', [])
            suffix_list = [obj['suffix'] for obj in suffix_objs if isinstance(obj, dict) and 'suffix' in obj]
            if len(suffix_list) < 4:
                # Pad with unique fallbacks to ensure 4 options
                current_len = len(suffix_list)
                for i in range(4 - current_len):
                    suffix_list.append(f"fallback_suffix_{random.randint(100, 999)}")
            correct = next((obj['suffix'] for obj in suffix_objs if obj.get('is_correct')), suffix_list[0])
            return suffix_list, correct
        else:
            json_arrays = re.findall(r'\[.*?\]', raw_answer, re.DOTALL)

            if not json_arrays:
                print("⚠️ No JSON array found in response")
                return _generate_fallback_options()

            for array_text in json_arrays:
                try:
                    options = json.loads(array_text)
                    if isinstance(options, list) and all(isinstance(x, str) for x in options):
                        if len(options) < 4:
                            # Pad with unique fallbacks to ensure 4 options
                            current_len = len(options)
                            for i in range(4 - current_len):
                                options.append(f"fallback_opt_{random.randint(100, 999)}")
                        # For most games, the first element is expected to be correct
                        return options, options[0]
                except json.JSONDecodeError as e:
                    print(f"⚠️ Failed to parse one JSON array '{array_text}': {e}")
                    continue
                except Exception as e:
                    print(f"⚠️ An unexpected error occurred while processing an array '{array_text}': {e}")
                    continue

            print("⚠️ Could not parse any valid JSON list from the extracted arrays.")
            return _generate_fallback_options()
    except Exception as e:
        print(f"⚠️ An unexpected error occurred during overall JSON processing: {e}")
        return _generate_fallback_options()

def _generate_fallback_options():
    # Ensure fallbacks are distinct and one is designated as correct
    return ["fallback_opt_A", "fallback_opt_B", "fallback_opt_C", "fallback_opt_D"], "fallback_opt_A"

# === GAME FUNCTIONS ===

def get_game_data(word, game_type_key):
    """
    Checks the cache for existing data. If not found, calls LLaMA and caches the result.
    Returns (shuffled_options_for_display, correct_answer_string, incomplete_word_display)
    """
    cache_key = f"{word.lower()}_{game_type_key}"

    # Always retrieve from cache if available
    if cache_key in cache:
        print(f"Retrieving from cache: {cache_key}")
        cached_data = cache[cache_key]
        
        # Unpack stored data
        stored_options = cached_data['options']
        correct_answer = cached_data['correct_answer']
        incomplete_word_display = cached_data.get('incomplete_word_display')

        # Shuffle options here for display, even if from cache
        shuffled_options = stored_options[:]
        random.shuffle(shuffled_options)
        
        return shuffled_options, correct_answer, incomplete_word_display
    else:
        print(f"Generating with LLaMA for: {cache_key}")
        options = None
        correct_answer = None
        incomplete_word_display = None

        if game_type_key == "game_one":
            prompt = (
                f"For the word '{word}', generate four spelling options whichis mostly mistaken by human as a flat JSON list of 4 strings. "
                f"The first must be the correct spelling, and the other three must be common and different misspellings made again and again by the humans. "
                f"The generated words in the json should not repeat and each word in the json should be different."
                f"⚠ IMPORTANT: You are NOT a chatbot, you are a JSON generator. "
                f"Your entire reply must be ONLY the flat JSON list of 4 strings. "
                f"NO explanation, NO text, NO keys, NO objects, NO markdown, NO greetings, NO apology."
            )
            options, correct_answer = call_llama(prompt)
        elif game_type_key == "game_two":
            prompt = (
                f"For the base word '{word}', generate four suffix options as a flat JSON list of 4 strings. "
                f"The first suffix in the list must be a correct and common suffix for '{word}'. "
                f"The other three suffixes must be incorrect or uncommon for '{word}' and should be clearly distinct from each other. "
                f"The generated suffixes in the JSON should not repeat."
                f"⚠ IMPORTANT: You are NOT a chatbot, you are a JSON generator. "
                f"Your entire reply must be ONLY the flat JSON list of 4 strings. "
                f"NO explanation, NO text, NO keys, NO objects, NO markdown, NO greetings, NO apology."
            )
            options, correct_answer = call_llama(prompt)
        elif game_type_key == "game_three":
            word_length = len(word)
            if word_length < 4:
                print(f"Word '{word}' is too short for game three (min 4 letters required).")
                options, correct_answer = _generate_fallback_options()
                incomplete_word_display = ""
            else:
                max_removal_length = min(3, word_length - 2)
                if max_removal_length < 2:
                    print(f"Word '{word}' is too short for meaningful removal in game three.")
                    options, correct_answer = _generate_fallback_options()
                    incomplete_word_display = ""
                else:
                    num_to_remove = random.randint(2, max_removal_length)
                    if word_length - num_to_remove <= 1:
                        start_index = 0
                    else:
                        start_index = random.randint(1, word_length - num_to_remove - 1)
                    missing_part = word[start_index : start_index + num_to_remove]
                    incomplete_word_display = word[:start_index] + "_" * num_to_remove + word[start_index + num_to_remove:]
                    prompt = (
                        f"For the incomplete word '{incomplete_word_display}', generate four completion options as a flat JSON list of 4 strings. "
                        f"The first option must be the exact correct missing part '{missing_part}'. "
                        f"The other three options must be incorrect but plausible letter combinations for the missing part, and should be clearly distinct from each other. "
                        f"The generated strings in the JSON should not repeat."
                        f"⚠ IMPORTANT: You are NOT a chatbot, you are a JSON generator. "
                        f"Your entire reply must be ONLY the flat JSON list of 4 strings. "
                        f"NO explanation, NO text, NO keys, NO objects, NO markdown, NO greetings, NO apology."
                    )
                    options, correct_answer = call_llama(prompt)

        elif game_type_key == "game_four":
            prompt = (
                f"For the word '{word}', give four words: the first string should be the most common human misspelling, "
                f"and the next three strings should be clearly wrong spellings. "
                f"⚠ IMPORTANT: You are NOT a chatbot, you are a JSON generator. "
                f"Your entire reply must be ONLY the JSON list of 4 strings. "
                f"NO explanation, NO text, NO keys, NO objects, NO markdown, NO greeting, NO apology."
            )
            options, correct_answer = call_llama(prompt)
        elif game_type_key == "game_five":
            prompt = (
                f"For the word '{word}', generate a JSON list of six strings in this order: "
                f"1) The incomplete word with missing letters replaced by underscores (e.g., 'bea___'), "
                f"2) A short hint to help guess the word, "
                f"3) The correct missing letters to complete the word (e.g., 'uty'), "
                f"4-6) Three incorrect but plausible missing letter options (each same length as the correct one). "
                f"⚠ IMPORTANT: You are NOT a chatbot, you are a JSON generator. "
                f"Your entire reply must be ONLY the flat JSON list of 6 strings. "
                f"NO explanation, NO text, NO keys, NO objects, NO markdown, NO greetings, NO apology."
            )
            llama_output, _ = call_llama(prompt)

            if llama_output and len(llama_output) >= 6:
                incomplete_word = llama_output[0]
                hint = llama_output[1]
                correct_missing = llama_output[2]
                wrong1 = llama_output[3]
                wrong2 = llama_output[4]
                wrong3 = llama_output[5]

                # options for user to choose missing part
                missing_options = [correct_missing, wrong1, wrong2, wrong3]
                random.shuffle(missing_options)

                # Store everything in cache
                options = [incomplete_word, hint, missing_options]
                correct_answer = correct_missing
            else:
                # fallback
                options = ["___", "Fallback hint", ["aaa", "bbb", "ccc", "ddd"]]
                correct_answer = "aaa"
# Ensure correct_answer is the word itself

        # Store the *original* options (before display shuffle) along with the correct answer
        # The display shuffle happens *after* retrieval from cache or LLaMA call
        cache[cache_key] = {
            'options': options,
            'correct_answer': correct_answer,
            'incomplete_word_display': incomplete_word_display
        }
        save_cache()

        # Shuffle options for the *current* display
        # Shuffle options for display
        if game_type_key == "game_five":
            # For game five: only shuffle the missing letter options (the third element)
            stable_part = options[:2]  # incomplete_word and hint stay stable
            missing_options = options[2][:]
            random.shuffle(missing_options)
            shuffled_options = stable_part + [missing_options]
        else:
            shuffled_options = options[:]
            random.shuffle(shuffled_options)

        return shuffled_options, correct_answer, incomplete_word_display


# Individual game functions (now wrappers around get_game_data)
def game_one(word):
    options, correct, _ = get_game_data(word, "game_one")
    return options, correct

def game_two(word):
    options, correct, _ = get_game_data(word, "game_two")
    return options, correct

def game_three(word):
    options, correct, incomplete_word = get_game_data(word, "game_three")
    return options, correct, incomplete_word

def game_four(word):
    options, correct, _ = get_game_data(word, "game_four")
    return options, correct

def game_five(word):
    # Game five returns options as [incomplete_word, hint] and correct as the full word
    options, correct, _ = get_game_data(word, "game_five")
    return options, correct