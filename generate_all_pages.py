#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт генерации многоязычных страниц с автоматическим переводом через Google Translate
"""
import json
import os
import shutil
import glob
import re
from googletrans import Translator
from typing import Dict, Optional
import time

# === ИНИЦИАЛИЗАЦИЯ ПЕРЕВОДЧИКА ===
translator = Translator()

# === ФУНКЦИЯ ПЕРЕВОДА ===
def translate_text(text: str, target_lang: str, source_lang: str = 'ru') -> str:
    """
    Переводит текст через Google Translate (бесплатно)
    
    Args:
        text: Текст для перевода
        target_lang: Целевой язык (en, de, zh)
        source_lang: Исходный язык (по умолчанию ru)
    
    Returns:
        Переведенный текст или исходный текст при ошибке
    """
    if not text or not text.strip():
        return text
    
    # Маппинг языковых кодов для Google Translate
    lang_map = {
        'zh': 'zh-cn',  # Упрощенный китайский
        'en': 'en',
        'de': 'de'
    }
    
    target = lang_map.get(target_lang.lower(), target_lang.lower())
    
    try:
        # Небольшая задержка, чтобы не перегружать API
        time.sleep(0.1)
        
        result = translator.translate(text, src=source_lang, dest=target)
        return result.text
    except Exception as e:
        print(f"⚠️  Ошибка при переводе '{text[:50]}...': {e}")
        return text




def translate_property_data(prop: Dict, force_retranslate: bool = False) -> Dict:
    """
    Переводит данные объекта недвижимости на все языки
    
    Args:
        prop: Словарь с данными объекта
        force_retranslate: Если True, переводит заново даже если перевод уже есть
    
    Returns:
        Обновленный словарь с переводами
    """
    languages = ['en', 'de', 'zh']
    
    # Поля для перевода
    text_fields = ['title', 'description', 'location']
    
    for field in text_fields:
        if field not in prop or not isinstance(prop[field], dict):
            prop[field] = {}
        
        ru_text = prop[field].get('ru', '')
        if not ru_text:
            continue
        
        for lang in languages:
            # Пропускаем, если перевод уже есть и не требуется принудительный перевод
            if not force_retranslate and prop[field].get(lang):
                continue
            
            print(f"  🌐 Переводим {field} на {lang.upper()}...")
            prop[field][lang] = translate_text(ru_text, lang)
    
    # Перевод преимуществ (features)
    if 'features' in prop and isinstance(prop['features'], dict):
        ru_features = prop['features'].get('ru', [])
        for lang in languages:
            if not force_retranslate and prop['features'].get(lang):
                continue
            
            print(f"  🌐 Переводим преимущества на {lang.upper()}...")
            translated_features = []
            for feature in ru_features:
                translated_features.append(translate_text(feature, lang))
            prop['features'][lang] = translated_features
    
    # Перевод характеристик (specs) - только ключи
    if 'specs' in prop and isinstance(prop['specs'], dict):
        ru_specs = prop['specs'].get('ru', {})
        
        # Словарь для перевода ключей характеристик
        spec_translations = {
            'en': {
                'houseArea': 'House Area',
                'landArea': 'Land Area', 
                'floors': 'Floors',
                'rooms': 'Rooms',
                'material': 'Material',
                'area': 'Area',
                'floor': 'Floor',
                'entrance': 'Entrance',
                'balcony': 'Balcony',
                'heating': 'Heating',
                'renovation': 'Renovation'
            },
            'de': {
                'houseArea': 'Hausfläche',
                'landArea': 'Grundstücksfläche',
                'floors': 'Etagen',
                'rooms': 'Zimmer',
                'material': 'Material',
                'area': 'Fläche',
                'floor': 'Etage',
                'entrance': 'Eingang',
                'balcony': 'Balkon',
                'heating': 'Heizung',
                'renovation': 'Renovierung'
            },
            'zh': {
                'houseArea': '房屋面积',
                'landArea': '土地面积',
                'floors': '楼层',
                'rooms': '房间',
                'material': '材料',
                'area': '面积',
                'floor': '楼层',
                'entrance': '入口',
                'balcony': '阳台',
                'heating': '供暖',
                'renovation': '装修'
            }
        }
        
        for lang in languages:
            if not force_retranslate and prop['specs'].get(lang):
                continue
            
            prop['specs'][lang] = {}
            for key, value in ru_specs.items():
                # Значения переводим через API, если это текст
                if value and isinstance(value, str) and not value.replace('.', '').replace(',', '').isdigit():
                    prop['specs'][lang][key] = translate_text(value, lang)
                else:
                    # Числовые значения оставляем как есть
                    prop['specs'][lang][key] = value
    
    return prop


# === 1. КОПИРОВАНИЕ ФОТОГРАФИЙ (Smart Sync) ===
def sync_images():
    # Путь к источникам фото (ТЕПЕРЬ ВНУТРИ ПРОЕКТА)
    # Используем абсолютный путь для надежности, но относительно текущей папки
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_base = os.path.join(base_dir, "source_photos", "object-4")
    source_hero = os.path.join(source_base, "hero")
    
    # Путь назначения (куда копируем для сайта)
    project_path = os.path.join(base_dir, "images", "object-4")
    
    # Создаем папку назначения, если её нет
    if os.path.exists(project_path):
        # Опционально: можно чистить или просто перезаписывать. 
        # Если чистить - раскомментировать: shutil.rmtree(project_path)
        pass
    else:
        os.makedirs(project_path)

    print(f"🔄 Синхронизация фото из {source_base}...")
    
    counter = 1
    
    # 1. Сначала берет фото из папки HERO
    if os.path.exists(source_hero):
        hero_files = sorted(glob.glob(os.path.join(source_hero, "*.[jJ][pP][gG]"))) \
                   + sorted(glob.glob(os.path.join(source_hero, "*.[jJ][pP][eE][gG]")))
                   
        if hero_files:
            print(f"  🌟 Найдено {len(hero_files)} фото в папке HERO")
            for photo in hero_files:
                dest = os.path.join(project_path, f"photo_{counter}.jpg")
                shutil.copy2(photo, dest)
                counter += 1
    
    # 2. Затем берет все остальные фото из основной папки
    if os.path.exists(source_base):
        main_files = sorted(glob.glob(os.path.join(source_base, "*.[jJ][pP][gG]"))) \
                   + sorted(glob.glob(os.path.join(source_base, "*.[jJ][pP][eE][gG]")))
                   
        for photo in main_files:
            if os.path.isdir(photo):
                continue
                
            dest = os.path.join(project_path, f"photo_{counter}.jpg")
            shutil.copy2(photo, dest)
            counter += 1
        
    print(f"✅ Всего скопировано {counter-1} фото для Объекта 4")



# === 2. ГЕНЕРАЦИЯ СТРАНИЦ ===
def generate_all():
    # Читаем данные
    with open('data.json', 'r', encoding='utf-8') as f:
        properties = json.load(f)

    # Переводим все объекты
    print("\n🌍 Начинаем автоматический перевод...")
    for i, prop in enumerate(properties):
        print(f"\n📝 Объект {prop.get('id', i+1)}: {prop.get('title', {}).get('ru', 'Без названия')}")
        properties[i] = translate_property_data(prop)
    
    # Сохраняем обновленные данные с переводами
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(properties, f, indent=4, ensure_ascii=False)
    print("\n✅ Переводы сохранены в data.json")

    # Читаем шаблон
    with open('templates/full-object-template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    print("\n📄 Генерируем HTML страницы...")
    for prop in properties:
        obj_id = prop['id']
        
        # 1. Читаем реальное количество фото в папке
        img_dir = f"images/object-{obj_id}"
        if os.path.exists(img_dir):
            photos = [f for f in os.listdir(img_dir) if f.startswith('photo_') and f.endswith('.jpg')]
            photo_count = len(photos)
        else:
            photo_count = 0
            
        print(f"  Объект {obj_id}: найдено {photo_count} фото")

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
            features = prop.get('features', [])
            if isinstance(features, dict):
                # Если features - словарь с переводами
                feat_list = features.get(lang, features.get('ru', []))
            else:
                # Если features - простой список (старый формат)
                feat_list = features
            
            features_html = '<div class="description"><h3>Преимущества</h3><div class="features-list">'
            for f in feat_list:
                features_html += f'<div class="feature-item"><i class="fas fa-check"></i> {f}</div>'
            features_html += '</div></div>'
            
            
            features_pattern = r'<div class="description">\s*<h3>Преимущества</h3>.*?</div>\s*</div>\s*</div>'
            content = re.sub(features_pattern, features_html, content, flags=re.DOTALL)



            # --- ПЕРЕВОДЫ ШАПКИ И ЗАГОЛОВКОВ ---
            trans = {
                'ru': {
                    'subtitle': '<span>Б</span><span>а</span><span>л</span><span>т</span><span>и</span><span>й</span><span>с</span><span>к</span><span>и</span><span>е</span><span>&nbsp;</span><span>д</span><span>о</span><span>м</span><span>а</span>',
                    'menu': ['Каталог', 'Побережье', 'Подбор', 'Услуги', 'Отзывы'],
                    'headings': ['О доме', 'Преимущества', 'Расположение', 'Контактные данные', 'Записаться на просмотр'],
                    'agent_role': 'Ведущий специалист',
                    'sub_phone': 'Калининград и область',
                    'breadcrumb_home': 'Главная',
                    'home_link': 'index.html'
                },
                'en': {
                    'subtitle': '<span>B</span><span>a</span><span>l</span><span>t</span><span>i</span><span>c</span><span>&nbsp;</span><span>H</span><span>o</span><span>m</span><span>e</span><span>s</span>',
                    'menu': ['Catalog', 'Coastline', 'Selection', 'Services', 'Reviews'],
                    'headings': ['About House', 'Features', 'Location', 'Contact Details', 'Book a Viewing'],
                    'agent_role': 'Leading Specialist',
                    'sub_phone': 'Kaliningrad & Region',
                    'breadcrumb_home': 'Home',
                    'home_link': 'en.html'
                },
                'de': {
                    'subtitle': '<span>B</span><span>a</span><span>l</span><span>t</span><span>i</span><span>s</span><span>c</span><span>h</span><span>e</span><span>&nbsp;</span><span>H</span><span>ä</span><span>u</span><span>s</span><span>e</span><span>r</span>',
                    'menu': ['Katalog', 'Ostseeküste', 'Auswahl', 'Leistungen', 'Bewertungen'],
                    'headings': ['Über das Haus', 'Vorteile', 'Lage', 'Kontaktdaten', 'Besichtigung buchen'],
                    'agent_role': 'Führender Spezialist',
                    'sub_phone': 'Kaliningrad & Region',
                    'breadcrumb_home': 'Startseite',
                    'home_link': 'de.html'
                },
                'zh': {
                    'subtitle': '<span>波</span><span>罗</span><span>的</span><span>海</span><span>之</span><span>家</span>',
                    'menu': ['房产目录', '海岸线', '选房', '服务', '评论'],
                    'headings': ['关于房产', '房产特色', '地理位置', '联系方式', '预约看房'],
                    'agent_role': '首席专家',
                    'sub_phone': '加里宁格勒及地区',
                    'breadcrumb_home': '首页',
                    'home_link': 'zh.html'
                }
            }
            t = trans.get(lang, trans['ru'])

            # Замена подзаголовка логотипа и ссылки на главную
            content = content.replace('<span>Б</span><span>а</span><span>л</span><span>т</span><span>и</span><span>й</span><span>с</span><span>к</span><span>и</span><span>е</span><span>&nbsp;</span><span>д</span><span>о</span><span>м</span><span>а</span>', t['subtitle'])
            content = content.replace('href="index.html"', f'href="{t["home_link"]}"')
            
            # Замена меню и ссылок-якорей
            content = content.replace('href="index.html#catalog"', f'href="{t["home_link"]}#catalog"')
            content = content.replace('href="index.html#categories"', f'href="{t["home_link"]}#categories"')
            content = content.replace('href="index.html#quiz"', f'href="{t["home_link"]}#quiz"')
            content = content.replace('href="index.html#services"', f'href="{t["home_link"]}#services"')
            
            content = content.replace('>Каталог<', f'>{t["menu"][0]}<')
            content = content.replace('>Побережье<', f'>{t["menu"][1]}<')
            content = content.replace('>Подбор<', f'>{t["menu"][2]}<')
            content = content.replace('>Услуги<', f'>{t["menu"][3]}<')
            content = content.replace('>Отзывы<', f'>{t["menu"][4]}<')
            
            # Замена заголовков разделов
            content = content.replace('<h3>О доме</h3>', f'<h3>{t["headings"][0]}</h3>')
            content = content.replace('<h3>Преимущества</h3>', f'<h3>{t["headings"][1]}</h3>')
            content = content.replace('Расположение</h3>', f'{t["headings"][2]}</h3>')
            content = content.replace('Записаться на просмотр</button>', f'{t["headings"][4]}</button>')
            
            # Роль агента и подпись телефона
            content = content.replace('Ведущий специалист', t['agent_role'])
            content = content.replace('Калинингад и область', t['sub_phone'])
            content = content.replace('>Главная<', f'>{t["breadcrumb_home"]}<')

            # 6. Форма (Название объекта)
            content = content.replace('value="Дом в Зеленоградске (ID 10915771)"', f'value="{title} (ID {obj_id})"')

            # --- ССЫЛКИ И ЯЗЫКИ (ПОЛНАЯ ПЕРЕГЕНЕРАЦИЯ БЛОКОВ) ---
            # Генерируем HTML для переключателя языков
            switcher_html = '<div class="lang-switcher{extra_classes}">'
            for l in ['ru', 'en', 'de', 'zh']:
                link = f'object-{obj_id}.html' if l == 'ru' else f'object-{obj_id}-{l}.html'
                active_class = ' class="active"' if l == lang else ''
                switcher_html += f'\n                    <a href="{link}"{active_class}>{l.upper()}</a>'
            switcher_html += '\n                </div>'

            # 1. Заменяем мобильный переключатель
            # Ищем блок: <div class="lang-switcher mobile-lang-switcher">...</div>
            mobile_switcher = switcher_html.format(extra_classes=" mobile-lang-switcher")
            content = re.sub(
                r'<div class="lang-switcher mobile-lang-switcher">.*?</div>', 
                mobile_switcher, 
                content, 
                flags=re.DOTALL
            )
            
            # 2. Заменяем десктопный переключатель
            # Ищем блок: <div class="lang-switcher">...</div> (без mobile-lang-switcher)
            # Но так как мы уже заменили мобильный, можно искать просто <div class="lang-switcher">
            # Важно: регулярка должна не захватить лишнего. Ищем точное вхождение из шаблона.
            
            # Проще: заменим оставшийся блок
            desktop_switcher = switcher_html.format(extra_classes="")
            content = re.sub(
                r'<div class="lang-switcher">\s*<a href="object-10915771.*?</div>', 
                desktop_switcher, 
                content, 
                flags=re.DOTALL
            )



            # --- ГАЛЕРЕЯ (HTML ПРЕВЬЮ - ПЕРВЫЕ 5) ---
            gallery_html = f'<div class="gallery-grid" onclick="openGallery(0)">\n'
            
            main_img = f"images/object-{obj_id}/photo_1.jpg" if photo_count > 0 else "images/placeholder.jpg"
            gallery_html += f'''            <div class="gallery-item gallery-main">
                <img src="{main_img}" alt="{title}">
                <div class="gallery-overlay"><i class="far fa-image"></i> {photo_count} фото</div>
            </div>\n'''
            
            for i in range(2, min(6, photo_count + 1)):
                img_path = f"images/object-{obj_id}/photo_{i}.jpg"
                gallery_html += f'''            <div class="gallery-item">
                <img src="{img_path}" alt="фото {i}">
            </div>\n'''
            
            gallery_html += '        </div>'
            
            content = re.sub(
                r'<div class="gallery-grid".*?</div>', 
                gallery_html, 
                content, 
                flags=re.DOTALL
            )
            
            # --- JS ЦИКЛ ---
            js_loop = f'''
        const allPhotos = [];
        const photoCount = {photo_count};
        const folder = "images/object-{obj_id}/";
        
        for (let i = 1; i <= photoCount; i++) {{
            allPhotos.push(folder + `photo_${{i}}.jpg`);
        }}
            '''
            
            content = re.sub(
                r'const allPhotos = .*?const thumbContainer',
                f'{js_loop.strip()}\n\n        let currentImgIdx = 0;\n        const thumbContainer',
                content,
                flags=re.DOTALL
            )
            
            content = content.replace('id="modalCounter">1 / 3</div>', f'id="modalCounter">1 / {photo_count}</div>')
            
            # Сохраняем файл
            suffix = '' if lang == 'ru' else f'-{lang}'
            filename = f"object-{obj_id}{suffix}.html"
            with open(filename, 'w', encoding='utf-8') as out:
                out.write(content)

    print("✅ Генерация завершена")

    # === 3. ОЧИСТКА УДАЛЕННЫХ СТРАНИЦ ===
    current_ids = [p['id'] for p in properties]
    all_files = glob.glob("object-*.html")
    
    for f in all_files:
        match = re.match(r'object-(\d+)(-[a-z]{2})?\.html', f)
        if match:
            obj_id = int(match.group(1))
            if obj_id not in current_ids:
                print(f"🗑 Удаляем старый файл: {f}")
                os.remove(f)

if __name__ == "__main__":
    sync_images()
    generate_all()
