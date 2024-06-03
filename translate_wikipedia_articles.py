import json
import time
import re

# ========================

from googletrans import Translator


def translate_text(text, src_language='en', dest_language='fr'):
    translator = Translator()
    print('Processing ...')

    # Split the text into smaller chunks because Google Translate has a limit on the text length
    chunk_size = 5000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    reset_tor = False
    translated_chunks = []
    for idx, chunk in enumerate(chunks, start=1):
        if idx % 8 == 5:
            time.sleep(40)
        # if idx % 50 == 2:
        #     reset_tor = True

        translated_chunk = translator.translate(chunk, src=src_language, dest=dest_language, reset_tor=reset_tor)
        print("chunk number: ", idx)
        print(translated_chunk.text[0:100])
        time.sleep(10)
        translated_chunks.append(translated_chunk.text)
        # reset_tor = False

    # Join the translated chunks back into a single text
    translated_text = ' '.join(translated_chunks)

    return translated_text


# ========================

def read_json_file(file_path):
    try:
        # Open the JSON file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load the content of the file into a Python list
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {file_path}.")
        return []
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}")
        return []


def create_article_object(article_id, title, summary, translated_text_en, translated_text_fr, translated_text_es,
                          translated_text_ar, translated_text_fa, translated_text_ru, translated_text_hi):
    return {"article_id": article_id, "title": title,
            "summary": summary,
            "content": {
                "EN": translated_text_en,
                "FR": translated_text_fr,
                "ES": translated_text_es,
                "AR": translated_text_ar,
                "FA": translated_text_fa,
                "RU": translated_text_ru,
                "HI": translated_text_hi
            }}


translated_articles_data = []


def translate_article(article_id, title, summary, article):
    print("\n Translating article to French: ")
    translated_text_fr = translate_text(article, src_language='en', dest_language='fr')
    time.sleep(80)
    print("Translating article to Spanish: ")
    translated_text_es = translate_text(article, src_language='en', dest_language='es')
    time.sleep(90)
    print("Translating article to Arabic: ")
    translated_text_ar = translate_text(article, src_language='en', dest_language='ar')
    time.sleep(140)
    print("Translating article to Farsi: ")
    translated_text_fa = translate_text(article, src_language='en', dest_language='fa')
    time.sleep(120)
    print("Translating article to Russian: ")
    translated_text_ru = translate_text(article, src_language='en', dest_language='ru')
    time.sleep(150)
    print("Translating article to hindi: ")
    translated_text_hi = translate_text(article, src_language='en', dest_language='hi')

    # translated_text_fr = ''
    # translated_text_es = ''
    # translated_text_ar = ''
    # translated_text_fa = ''
    # translated_text_ru = ''
    # translated_text_hi = ''

    article_object = create_article_object(article_id, title, summary, article, translated_text_fr,
                                           translated_text_es,
                                           translated_text_ar, translated_text_fa, translated_text_ru,
                                           translated_text_hi)
    translated_articles_data.append(article_object)


def save_as_json(articles_array, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(articles_array, json_file, ensure_ascii=False, indent=4)


def main():
    global translated_articles_data

    categories = ["Culture", "Reference", "Religion", "People", "Society", "Geography", "History", "Technology"]
    for category in categories:
        file_path = f'articles/random_wikipedia_{category}_articles_without_translate.json'
        objects_array = read_json_file(file_path)

        pattern = r"^(.*?)(\bSee also\b|\bReferences\b|\bExternal links\b)"

        for article_id, article in enumerate(objects_array, start=1):
            print("++++++ title :", article['id'], ". ", article['title'], ' ++++++')
            match = re.search(pattern, article['content']['EN'], re.DOTALL | re.IGNORECASE)
            if match:
                result = match.group(1)
                print("ready to translate:  ")
                time.sleep(30)
                translate_article(article['id'], article['title'], article['summary'], result.strip())
                time.sleep(120)

                if article['id'] % 3 == 2:
                    print('write json and sleep')
                    save_as_json(translated_articles_data, "Translated_" + file_path)
                    time.sleep(180)
            else:
                print("No match found id =", article_id)
        save_as_json(translated_articles_data, "Translated_" + file_path)
        translated_articles_data = []


if __name__ == "__main__":
    main()
