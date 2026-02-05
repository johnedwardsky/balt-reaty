import os
import re

base_dir = "/Users/johnsky/Documents/balthomes.ru"
files = ['index.html', 'en.html', 'de.html', 'zh.html']

# Уменьшил opacity с 0.9 до 0.6 для лучшей видимости фото
new_style = """
        .quiz-section {
            background-image: linear-gradient(rgba(13, 46, 97, 0.6), rgba(13, 46, 97, 0.6)), url('images/hero-main/photo_3.jpg');
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
        
    pattern = r'(\.quiz-section\s*\{[^}]+\})'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, new_style.strip(), content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Обновлен {filename} (сделан светлее)")
    else:
        print(f"⚠️ Стиль не найден в {filename}")

print("🎉 Готово")
