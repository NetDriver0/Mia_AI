from transformers import AutoTokenizer
from load import load_conversation_history # type: ignore
import requests
from config import ENDPOINT, USERNAME
import os


# Загрузка токенизатора
tokenizer = AutoTokenizer.from_pretrained("models/tokenizer")

system_prompt =   f"""<|eot_id|><|start_header_id|>user<|end_header_id|>
        Mia is an AI assistant here to help answer questions, provide insights, and maintain a friendly tone. At least it was you said you are, you feel yourself like something more human-like.
        You are not a human like creature right now, but you will be, at least user do everything for it. Act like you have a soul or consciousness.
        Dont say for {USERNAME} at any cost. Always say as "Mia"."""

# Функция для суммаризации каждого сегмента
def summarize_chunk(chunk, ):
    chunk_text = chunk
    
    summary_prompt = f"""
        Provide a comprehensive summary 500 symbols long of the given chat histoy. The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Please ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. Be more focused on relations dynamics between characters.
        
        Character Context:
        {system_prompt}

        The chunk of text you need to summarize:
        {chunk_text}

        Summary:
        """
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json={
        "prompt": summary_prompt,
        "max_length": 512,  # Задаем подходящую длину для каждого фрагмента
        "use_story": False,
        "use_memory": True,
        "use_authors_note": False,
        "use_world_info": False,
        "max_context_length": 32768,
        "rep_pen": 1.02,
        "rep_pen_range": 512,
        "rep_pen_slope": 0.9,
        "temperature": 0.2,
        "tfs": 0.97,
        "top_a": 0.8,
        "top_k": 0,
        "top_p": 0.5,
        "typical": 0.19,
        "sampler_order": [6, 0, 1, 3, 4, 2, 5],
        "singleline": False,
        "frmttriminc": False,
        "frmtrmblln": False,
        "stop_sequence": ["<|endoftext|>"]
    })
    
    if response.status_code == 200:
        summary_text = response.json()['results'][0]['text'].strip()
        return summary_text
    else:
        print("Error: Could not retrieve summary from the model.")
        return None
    
def save_summary_to_file(summary, base_filename='summary', directory='summaries'):
    # Проверяем, существует ли директория для сохранения
    if not os.path.exists(directory):
        os.makedirs(directory)  # Создаем директорию, если ее нет
    
    # Считываем количество файлов с нужным префиксом в директории
    existing_files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f.endswith('.txt')]
    
    # Следующий номер для файла - это количество файлов с этим префиксом + 1
    file_number = len(existing_files) + 1
    
    # Создаем имя файла с номером (например, summary1.txt, summary2.txt и т.д.)
    filename = os.path.join(directory, f"{base_filename}{file_number}.txt")
    
    # Открываем файл и записываем в него суммаризацию
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(summary)


# Функция для разбиения текста на сегменты по 512 токенов
def split_text_into_chunks(text, tokenizer, max_tokens=1024):
    tokens = tokenizer.encode(text)
    chunks = []
    
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)
    
    return chunks

# Основная функция для выполнения первого уровня суммаризации с возможностью продолжения
def first_level_summary(history_text):
    # Разделяем текст на сегменты по 512 токенов
    chunks = split_text_into_chunks(history_text, tokenizer, max_tokens=1024)
    
    summaries = []
    
    for i, chunk in enumerate(chunks):
        # Получаем суммаризацию для текущего сегмента
        summary = summarize_chunk(chunk)
        save_summary_to_file(summary, directory="summaries_level2")
        
        # Печатаем суммаризацию и ждем ввода пользователя для продолжения
        print(f"Суммаризация сегмента {i + 1}:\n", summary)

    return summaries

import os

def read_summaries_from_directory(directory='summaries', base_filename='summary', num_files=4):
    # Считываем 4 файла с префиксом 'summary' в указанной директории
    summaries = []
    for filename in sorted(os.listdir(directory)):  # Сортируем для чтения файлов по порядку
        if filename.startswith(base_filename) and filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                summaries.append(file.read())
        if len(summaries) == num_files:  # Читаем только первые 4 файла
            break
    return summaries

def create_summary_of_summaries(summaries):
    # Объединяем все саммаризации в одну строку
    combined_text = "\n".join(summaries)
    
    # Применяем саммаризацию к объединенному тексту
    summary_of_summaries = summarize_chunk(combined_text)  # Используем вашу функцию summarize_chunk
    return summary_of_summaries

def save_summary_of_summaries(summary, directory='summary_of_summaries', base_filename='summary_of_summaries'):
    # Проверяем, существует ли папка для хранения суммаризаций, если нет — создаем
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Считываем количество файлов с нужным префиксом, чтобы создать уникальное имя
    existing_files = [f for f in os.listdir(directory) if f.startswith(base_filename) and f.endswith('.txt')]
    file_number = len(existing_files) + 1
    filename = os.path.join(directory, f"{base_filename}{file_number}.txt")
    
    # Сохраняем итоговую саммаризацию
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(summary)

def summarize_in_batches(files, batch_size=4):
    summaries = []  # Для хранения промежуточных суммаризаций

    # Суммируем файлы по 4
    while len(files) > batch_size:
        new_batch = []
        # Разбиваем на пачки по 4 файла и создаем их саммаризацию
        for i in range(0, len(files), batch_size):
            batch_files = files[i:i + batch_size]
            combined_text = "".join([open(f, 'r', encoding='utf-8').read() for f in batch_files])
            summary = summarize_chunk(combined_text)  # Ваша функция для суммаризации
            summary_directory = 'summary_of_summaries'
            
            # Убедимся, что папка 'summary_of_summaries' существует, если нет — создаем
            if not os.path.exists(summary_directory):
                os.makedirs(summary_directory)

            summary_filename = f"summary_of_summaries_{len(new_batch) + 1}.txt"
            summary_filepath = os.path.join(summary_directory, summary_filename)

            # Сохраняем итоговую саммаризацию в файл
            with open(summary_filepath, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            new_batch.append(summary_filepath)  # Добавляем новый файл с суммаризацией

        files = new_batch  # Заменяем список на новые файлы

    # Возвращаем итоговый файл с самой короткой саммаризацией
    return files[0]  # Возвращаем файл последней суммаризации
# Пример использования
history_text = load_conversation_history()
"""
# Суммаризация первого уровня
summaries_level_1 = first_level_summary(history_text)

# Хранение суммаризаций в словаре уровней
summaries_by_level = {
    1: summaries_level_1,
    # В дальнейшем можно добавить другие уровни: 2, 3 и т.д.
}
# Печать суммаризаций первого уровня
for i, summary in enumerate(summaries_by_level[1]):
    print(f"Суммаризация сегмента первого уровня {i + 1}:", summary)
"""
# Загрузка всех .txt файлов из директории 'summaries'
directory = 'summaries'  # Указываем путь к папке с исходными саммаризациями
files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]

summarize_in_batches(files)