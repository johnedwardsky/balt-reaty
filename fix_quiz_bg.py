import os
import re

base_dir = "/Users/johnsky/.gemini/antigravity/scratch/kaliningrad-real-estate"
files = ['index.html', 'en.html', 'de.html', 'zh.html']

# Новый стиль: используем локальную картинку (например photo_3.jpg) и убираем fixed
new_style = """
        .quiz-section {
            background-image: linear-gradient(rgba(13, 46, 97, 0.9), rgba(13, 46, 97, 0.9)), url('images/hero-main/photo_3.jpg');
            background-size: cover;
            background-position: center;
            color: var(--white);
            text-align: center;
        }"""

for filename in files:
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Ищем блок стилей .quiz-section
    pattern = r'(\.quiz-section\s*\{[^}]+\})'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, new_style.strip(), content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Обновлен {filename}")
    else:
        print(f"⚠️ Стиль не найден в {filename}")

print("🎉 Готово")
