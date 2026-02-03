#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import shutil
import glob
import re

# === 1. КОПИРОВАНИЕ ФОТОГРАФИЙ (Safe Copy) ===
def sync_images():
    # Путь к эталону на рабочем столе (ТОЛЬКО ЧТЕНИЕ)
    desktop_path = "/Users/johnsky/Desktop/Balthomes/images/object-10915771"
    
    # Путь в проекте (ID 4 - это тот самый дом)
    project_path = "images/object-4"
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    
    print(f"🔄 Копируем фото из {desktop_path}...")
    
    # Находим все jpg файлы
    photos = glob.glob(os.path.join(desktop_path, "photo_*.jpg"))
    for photo in photos:
        filename = os.path.basename(photo)
        dest = os.path.join(project_path, filename)
        shutil.copy2(photo, dest)
        
    print(f"✅ Скопировано {len(photos)} фото для Объекта 4")

# === 2. ГЕНЕРАЦИЯ СТРАНИЦ ===
def generate_all():
    # Читаем данные
    with open('data.json', 'r', encoding='utf-8') as f:
        properties = json.load(f)

    # Читаем шаблон
    with open('templates/full-object-template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    for prop in properties:
        obj_id = prop['id']
        
        # 1. Читаем реальное количество фото в папке
        img_dir = f"images/object-{obj_id}"
        if os.path.exists(img_dir):
            photos = [f for f in os.listdir(img_dir) if f.startswith('photo_') and f.endswith('.jpg')]
            photo_count = len(photos)
        else:
            photo_count = 0
            
        print(f"Объект {obj_id}: найдено {photo_count} фото")

        # Если фото нет, используем заглушку, но логику цикла оставляем (просто count=0)
        
        for lang in ['ru', 'en', 'de', 'zh']:
            content = template
            
            # --- БАЗОВЫЕ ЗАМЕНЫ ---
            def get_text(field):
                if field in prop:
                    if isinstance(prop[field], dict):
                        return prop[field].get(lang, prop[field].get('ru', ''))
                    return str(prop[field])
                return ''

            title = get_text('title')
            # 1. Заголовки
            content = content.replace('Дом в Зеленоградске 300 м² | BaltHomes — Элитная недвижимость', f'{title} | BaltHomes')
            content = content.replace('Современный дом в Зеленоградске', title)
            
            # 2. Цена и Локация
            content = content.replace('27 500 000 ₽', get_text('price'))
            content = content.replace('г. Зеленоградск, 2-й Задонский переулок, 4', get_text('location'))
            content = content.replace('Зеленоградск, Район Малиновка', get_text('location'))
            content = content.replace('Дом в Малиновке', title) # Хлебные крошки
            
            # 3. Характеристики (Specs)
            content = content.replace('>300 м²</div>', f'>{get_text("stats").split("|")[0].strip()}</div>')
            content = content.replace('>8.5 сот.</div>', f'>{get_text("stats").split("|")[-1].strip()}</div>')
            
            # 4. Описание
            desc = get_text('description')
            desc_html = desc.replace('\n', '</p><p>').replace('\\n', '</p><p>')
            new_desc_html = f'<div class="description"><h3>О доме</h3><p>{desc_html}</p></div>'
            description_pattern = r'<div class="description">\s*<h3>О доме</h3>.*?</div>'
            content = re.sub(description_pattern, new_desc_html, content, flags=re.DOTALL)

            
            # 5. Преимущества
            feat_list = prop.get('features', [])
            features_html = '<div class="description"><h3>Преимущества</h3><div class="features-list">'
            for f in feat_list:
                features_html += f'<div class="feature-item"><i class="fas fa-check"></i> {f}</div>'
            features_html += '</div></div>'
            
            features_pattern = r'<div class="description">\s*<h3>Преимущества</h3>.*?</div>\s*</div>'
            content = re.sub(features_pattern, features_html + '\n            </div>', content, flags=re.DOTALL)

            # 6. Форма (Название объекта)
            content = content.replace('value="Дом в Зеленоградске (ID 10915771)"', f'value="{title} (ID {obj_id})"')

            # --- ССЫЛКИ И ЯЗЫКИ ---
            for l in ['ru', 'en', 'de', 'zh']:
                old_id = "10915771"
                old_link = f'object-{old_id}.html' if l == 'ru' else f'object-{old_id}-{l}.html'
                new_link = f'object-{obj_id}.html' if l == 'ru' else f'object-{obj_id}-{l}.html'
                # Активный класс
                active_cls = ' class="active"' if l == lang else ''
                # Сначала меняем ссылки с классом active
                content = content.replace(f'<a href="{old_link}" class="active">', f'<a href="{new_link}"{active_cls}>')
                content = content.replace(f'href="{old_link}"', f'href="{new_link}"')


            # --- ГАЛЕРЕЯ (HTML ПРЕВЬЮ - ПЕРВЫЕ 5) ---
            # Здесь мы генерируем HTML блок для первых 5 фото
            # Важно: используем реальные пути `images/object-{id}/photo_N.jpg`
            
            gallery_html = f'<div class="gallery-grid" onclick="openGallery(0)">\n'
            
            # Главное фото
            main_img = f"images/object-{obj_id}/photo_1.jpg" if photo_count > 0 else "images/placeholder.jpg"
            gallery_html += f'''            <div class="gallery-item gallery-main">
                <img src="{main_img}" alt="{title}">
                <div class="gallery-overlay"><i class="far fa-image"></i> {photo_count} фото</div>
            </div>\n'''
            
            # Остальные 4 (или меньше)
            for i in range(2, min(6, photo_count + 1)):
                img_path = f"images/object-{obj_id}/photo_{i}.jpg"
                gallery_html += f'''            <div class="gallery-item">
                <img src="{img_path}" alt="фото {i}">
            </div>\n'''
            
            gallery_html += '        </div>'
            
            # Заменяем блок галереи в шаблоне (ищем по классу gallery-grid)
            content = re.sub(
                r'<div class="gallery-grid".*?</div>', 
                gallery_html, 
                content, 
                flags=re.DOTALL
            )
            
            # --- JS ЦИКЛ (САМОЕ ВАЖНОЕ) ---
            # Генерируем красивый JS цикл вместо массива строк
            
            js_loop = f'''
        const allPhotos = [];
        const photoCount = {photo_count};
        const folder = "images/object-{obj_id}/";
        
        for (let i = 1; i <= photoCount; i++) {{
            allPhotos.push(folder + `photo_${{i}}.jpg`);
        }}
            '''
            
            # Заменяем старый JS блок с массивом
            # Ищем от const allPhotos до закрывающей скобки цикла
            content = re.sub(
                r'const allPhotos = \[.*?\];\.jpg`\);', # Паттерн для поиска старого "хвоста"
                js_loop.strip(),
                content,
                flags=re.DOTALL
            )
            
            # Если регулярка выше не сработала (из-за моего прошлого фикса), ищем более общий паттерн
            # "const allPhotos = ... (любой код) ... thumbContainer"
            content = re.sub(
                r'const allPhotos = .*?const thumbContainer',
                f'{js_loop.strip()}\n\n        let currentImgIdx = 0;\n        const thumbContainer',
                content,
                flags=re.DOTALL
            )
            
            # Обновляем счетчик
            content = content.replace('id="modalCounter">1 / 3</div>', f'id="modalCounter">1 / {photo_count}</div>')
            
            # Сохраняем файл
            suffix = '' if lang == 'ru' else f'-{lang}'
            filename = f"object-{obj_id}{suffix}.html"
            with open(filename, 'w', encoding='utf-8') as out:
                out.write(content)

    print("✅ Генерация завершена")

    # === 3. ОЧИСТКА УДАЛЕННЫХ СТРАНИЦ ===
    # Собираем все ID, которые у нас есть
    current_ids = [p['id'] for p in properties]
    
    # Ищем все файлы object-*.html в папке
    all_files = glob.glob("object-*.html")
    
    for f in all_files:
        # Пытаемся извлечь ID из имени файла
        # Форматы: object-1.html, object-1-en.html
        match = re.match(r'object-(\d+)(-[a-z]{2})?\.html', f)
        if match:
            obj_id = int(match.group(1))
            if obj_id not in current_ids:
                print(f"🗑 Удаляем старый файл: {f}")
                os.remove(f)

if __name__ == "__main__":
    sync_images()
    generate_all()
