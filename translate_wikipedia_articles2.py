import json
import time
import re
import random
import os

# ========================

from googletrans import Translator


def restart_tor_service():
    print("Restarting tor service...")
    os.system('sudo systemctl restart tor')
    time.sleep(30)  # Sleep to ensure the service restarts


counter = 0


def translate_text(text, src_language='en', dest_language='fr'):
    global counter
    translator = Translator()
    print('Processing ...')

    # Split the text into smaller chunks because Google Translate has a limit on the text length
    chunk_size = 5000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    reset_tor = False
    translated_chunks = []
    for idx, chunk in enumerate(chunks, start=1):
        counter = counter + 1
        if idx % 8 == 5:
            time.sleep(30)

        if counter == 100:
            restart_tor_service()
            counter = 0

        try:
            translated_chunk = translator.translate(chunk, src=src_language, dest=dest_language, reset_tor=reset_tor)
        except:
            print("RequestException wait and change tor pool ....")
            restart_tor_service()
            counter = 0
            translated_chunk = translator.translate(chunk, src=src_language, dest=dest_language, reset_tor=reset_tor)

        print("chunk number: ", idx)
        print(translated_chunk.text[0:100])
        time.sleep(random.uniform(22, 34))
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
    time.sleep(random.uniform(10, 30))
    print("Translating article to Spanish: ")
    translated_text_es = translate_text(article, src_language='en', dest_language='es')
    time.sleep(random.uniform(20, 30))
    print("Translating article to Arabic: ")
    translated_text_ar = translate_text(article, src_language='en', dest_language='ar')
    time.sleep(random.uniform(15, 35))
    print("Translating article to Farsi: ")
    translated_text_fa = translate_text(article, src_language='en', dest_language='fa')
    time.sleep(random.uniform(20, 30))
    print("Translating article to Russian: ")
    translated_text_ru = translate_text(article, src_language='en', dest_language='ru')
    # time.sleep(110)
    # print("Translating article to hindi: ")
    # translated_text_hi = translate_text(article, src_language='en', dest_language='hi')

    # translated_text_fr = ''
    # translated_text_es = ''
    # translated_text_ar = ''
    # translated_text_fa = ''
    # translated_text_ru = ''
    translated_text_hi = ''

    article_object = create_article_object(article_id, title, summary, article, translated_text_fr,
                                           translated_text_es,
                                           translated_text_ar, translated_text_fa, translated_text_ru,
                                           translated_text_hi)
    translated_articles_data.append(article_object)


def save_as_json(articles_array, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(articles_array, json_file, ensure_ascii=False, indent=4)


def load_translated_jsons(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            last = data.pop()
            return last['article_id']
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return 0
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {file_path}.")
        return 0
    except UnicodeDecodeError as e:
        print(f"Encoding error: {e}")
        return 0


def main():
    global translated_articles_data

    categories = ["Religion"]
    for category in categories:
        file_path_read = f'articles/random_wikipedia_{category}_articles_without_translate.json'
        file_path_write = f'random_wikipedia_{category}_articles_without_translate.json'
        objects_array = read_json_file(file_path_read)
        last_index = load_translated_jsons("Translated_" + file_path_write) + 1

        pattern = r"^(.*?)(\bSee also\b|\bReferences\b|\bExternal links\b)"
        counter_try = 0
        for article_id, article in enumerate(objects_array, start=1):
            try:
                if article['id'] < last_index:
                    continue

                print("++++++ title :", article['id'], ". ", article['title'], ' ++++++')
                match = re.search(pattern, article['content']['EN'], re.DOTALL | re.IGNORECASE)
                if match:
                    result = match.group(1)
                    print("ready to translate:  ")
                    time.sleep(random.uniform(15, 24))
                    translate_article(article['id'], article['title'], article['summary'], result.strip())
                    time.sleep(random.uniform(12, 32))

                    print("Article No.\"", article['id'], "\"added to \"", category, "\" file")
                    save_as_json(translated_articles_data, "Translated_" + file_path_write)

                    if article['id'] % 8 == 7:
                        print('sleep for 30s ... ')
                        time.sleep(random.uniform(20, 40))
                else:
                    print("No match found id =", article_id)
            except:
                print('try catch error')
                counter_try = counter_try + 1
                if counter_try == 2:
                    counter_try = 0
                    last_index = last_index + 1

        save_as_json(translated_articles_data, "Translated_" + file_path_write)
        translated_articles_data = []


if __name__ == "__main__":
    main()
