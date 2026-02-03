import os
import re

base_dir = "/Users/johnsky/.gemini/antigravity/scratch/kaliningrad-real-estate"
files = ['index.html', 'en.html', 'de.html', 'zh.html']

# Ищем и обновляем шаблоны тоже, чтобы при новой генерации не сбилось
templates_dir = os.path.join(base_dir, 'templates')
if os.path.exists(templates_dir):
    files.append('templates/full-object-template.html')

for filename in files:
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Меняем v=ЛюбоеЧисло на v=3
    new_content = re.sub(r'favicon\.svg\?v=\d+', 'favicon.svg?v=3', content)
    
    # Если вдруг нет версии вообще
    if 'favicon.svg"' in new_content:
         new_content = new_content.replace('favicon.svg"', 'favicon.svg?v=3"')
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Обновлен favicon в {filename}")
    else:
        print(f"ℹ️ Без изменений: {filename}")
