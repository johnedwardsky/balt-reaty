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

# Словарь статических переводов для преимуществ
FEATURE_TRANS = {
    'Автономное отопление': {'en': 'Autonomous heating', 'de': 'Autonome Heizung', 'zh': '自主采暖'},
    'Новый дом': {'en': 'New building', 'de': 'Neubau', 'zh': '新建房屋'},
    'Рядом школа': {'en': 'Near school', 'de': 'Schule in der Nähe', 'zh': '靠近学校'},
    'С ремонтом': {'en': 'Renovated', 'de': 'Mit Renovierung', 'zh': '已装修'},
    'Первая линия': {'en': 'First line', 'de': 'Erste Meereslinie', 'zh': '第一线'},
    'Газовое отопление': {'en': 'Gas heating', 'de': 'Gasheizung', 'zh': '天然气采暖'},
    'Видеонаблюдение': {'en': 'Video surveillance', 'de': 'Videoüberwachung', 'zh': '视频监控'},
    'Ландшафтный дизайн': {'en': 'Landscape design', 'de': 'Landschaftsgestaltung', 'zh': '景观设计'},
    'Кирпичный дом': {'en': 'Brick house', 'de': 'Backsteinhaus', 'zh': '砖房'},
    'Зеленый двор': {'en': 'Green courtyard', 'de': 'Grüner Innenhof', 'zh': '绿色庭院'},
    'Рядом супермаркет': {'en': 'Near supermarket', 'de': 'Supermarkt in der Nähe', 'zh': '靠近超市'},
    'Хорошая транспортная развязка': {'en': 'Good transport links', 'de': 'Gute Verkehrsanbindung', 'zh': '便利的交通'},
    'Дизайнерский ремонт': {'en': 'Designer renovation', 'de': 'Designer-Renovierung', 'zh': '设计师装修'},
    'Мебель в подарок': {'en': 'Furniture included', 'de': 'Möbel inklusive', 'zh': '赠送家具'},
    'Рядом озеро': {'en': 'Near lake', 'de': 'See in der Nähe', 'zh': '靠近湖泊'},
    'Консьерж-сервис': {'en': 'Concierge service', 'de': 'Concierge-Service', 'zh': '礼宾服务'}
}

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
    if 'features' in prop:
        # Если это простой список, превращаем его в словарь с ключом 'ru'
        if isinstance(prop['features'], list):
            prop['features'] = {'ru': prop['features']}
            
        if isinstance(prop['features'], dict):
            ru_features = prop['features'].get('ru', [])
            for lang in languages:
                # Всегда обновляем преимущества, так как список короткий и это важно для синхронизации
                # if not force_retranslate and prop['features'].get(lang):
                #     if len(prop['features'][lang]) == len(ru_features):
                #         continue
                
                print(f"  🌐 Переводим преимущества на {lang.upper()}...")
                translated_features = []
                for feature in ru_features:
                    # Сначала ищем в статическом словаре
                    if feature in FEATURE_TRANS and FEATURE_TRANS[feature].get(lang):
                        translated_features.append(FEATURE_TRANS[feature][lang])
                    else:
                        # Если нет - переводим через Google
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
    # Отключаем жесткую синхронизацию, так как теперь фото управляются через админку
    pass



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
        # 1. Читаем реальное количество фото
        # Сначала пробуем взять список из JSON (так как там сохранен порядок из админки)
        json_images = prop.get('images', [])
        if json_images:
             # Очищаем пути, оставляем только имена файлов, если нужно, или используем как есть
             # В админке сохраняются полные пути типа "images/object-10/photo.jpg"
             # Нам для проверки существования нужны абсолютные пути или относительные от корня
             photos = []
             for img_path in json_images:
                 if os.path.exists(img_path):
                     photos.append(os.path.basename(img_path))
             photo_count = len(photos)
        else:
            # Fallback: читаем папку, если в JSON пусто
            img_dir = f"images/object-{obj_id}"
            if os.path.exists(img_dir):
                photos = [f for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.jpeg'))]
                
                # Натуральная сортировка
                def natural_keys(text):
                    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]
                    
                photos.sort(key=natural_keys)
                photo_count = len(photos)
            else:
                photos = []
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
            
            # 1. Определение типа объекта
            prop_type = prop.get('type', '')
            if not prop_type:
                # Получаем русское название для определения типа
                title_ru = ''
                raw_title = prop.get('title', '')
                if isinstance(raw_title, dict):
                    title_ru = raw_title.get('ru', '').lower()
                else:
                    title_ru = str(raw_title).lower()
                
                if any(kw in title_ru for kw in ['квартира', 'апартамент', 'студия']): 
                    prop_type = 'apartment'
                elif 'таунхаус' in title_ru: 
                    prop_type = 'townhouse'
                else: 
                    prop_type = 'house'

            # 2. Инициализация переводов интерфейса
            trans = {
                'ru': {
                    'subtitle': '<span>Б</span><span>а</span><span>л</span><span>т</span><span>и</span><span>й</span><span>с</span><span>к</span><span>и</span><span>е</span><span>&nbsp;</span><span>д</span><span>о</span><span>м</span><span>а</span>',
                    'menu': ['Каталог', 'Побережье', 'Подбор', 'Услуги', 'Отзывы'],
                    'headings': {
                        'house': 'О доме',
                        'apartment': 'О квартире',
                        'townhouse': 'О таунхаусе',
                        'features': 'Преимущества',
                        'location': 'Расположение',
                        'contacts': 'Контактные данные',
                        'viewing': 'Записаться на просмотр'
                    },
                    'agent_role': 'Ведущий специалист',
                    'sub_phone': 'Калининград и область',
                    'breadcrumb_home': 'Главная',
                    'home_link': 'index.html'
                },
                'en': {
                    'subtitle': '<span>B</span><span>a</span><span>l</span><span>t</span><span>i</span><span>c</span><span>&nbsp;</span><span>H</span><span>o</span><span>m</span><span>e</span><span>s</span>',
                    'menu': ['Catalog', 'Coastline', 'Selection', 'Services', 'Reviews'],
                    'headings': {
                        'house': 'About House',
                        'apartment': 'About Apartment',
                        'townhouse': 'About Townhouse',
                        'features': 'Features',
                        'location': 'Location',
                        'contacts': 'Contact Details',
                        'viewing': 'Book a Viewing'
                    },
                    'agent_role': 'Leading Specialist',
                    'sub_phone': 'Kaliningrad & Region',
                    'breadcrumb_home': 'Home',
                    'home_link': 'en.html'
                },
                'de': {
                    'subtitle': '<span>B</span><span>a</span><span>l</span><span>т</span><span>и</span><span>с</span><span>к</span><span>и</span><span>е</span><span>&nbsp;</span><span>H</span><span>ä</span><span>u</span><span>s</span><span>e</span><span>r</span>',
                    'menu': ['Katalog', 'Ostseeküste', 'Auswahl', 'Leistungen', 'Bewertungen'],
                    'headings': {
                        'house': 'Über das Haus',
                        'apartment': 'Über die Wohnung',
                        'townhouse': 'Über das Townhouse',
                        'features': 'Vorteile',
                        'location': 'Lage',
                        'contacts': 'Kontaktdaten',
                        'viewing': 'Besichtigung buchen'
                    },
                    'agent_role': 'Führender Spezialist',
                    'sub_phone': 'Kaliningrad & Region',
                    'breadcrumb_home': 'Startseite',
                    'home_link': 'de.html'
                },
                'zh': {
                    'subtitle': '<span>波</span><span>罗</span><span>的</span><span>海</span><span>之</span><span>家</span>',
                    'menu': ['房产目录', '海岸线', '选房', '服务', '评论'],
                    'headings': {
                        'house': '关于房屋',
                        'apartment': '关于公寓',
                        'townhouse': '关于联排别墅',
                        'features': '房产特色',
                        'location': '地理位置',
                        'contacts': '联系方式',
                        'viewing': '预约看房'
                    },
                    'agent_role': '首席专家',
                    'sub_phone': '加里宁格勒及地区',
                    'breadcrumb_home': '首页',
                    'home_link': 'zh.html'
                }
            }
            t = trans.get(lang, trans['ru'])
            about_heading = t['headings'].get(prop_type, t['headings']['house'])

            # 3. Основные замены текста
            content = content.replace('Дом в Зеленоградске 300 м² | BaltHomes — Элитная недвижимость', f'{title} | BaltHomes')
            content = content.replace('Современный дом в Зеленоградске', title)
            content = content.replace('27 500 000 ₽', get_text('price'))
            content = content.replace('г. Зеленоградск, 2-й Задонский переулок, 4', get_text('location'))
            content = content.replace('Зеленоградск, Район Малиновка', get_text('location'))
            content = content.replace('Дом в Малиновке', title) # Breadcrumbs
            content = content.replace('<span>Б</span><span>а</span><span>л</span><span>т</span><span>и</span><span>й</span><span>с</span><span>к</span><span>и</span><span>е</span><span>&nbsp;</span><span>д</span><span>о</span><span>м</span><span>а</span>', t['subtitle'])
            content = content.replace('href="index.html"', f'href="{t["home_link"]}"')
            
            # Ссылки меню
            for i, anchor in enumerate(['#catalog', '#categories', '#quiz', '#services']):
                content = content.replace(f'href="index.html{anchor}"', f'href="{t["home_link"]}{anchor}"')
            
            content = content.replace('>Каталог<', f'>{t["menu"][0]}<')
            content = content.replace('>Побережье<', f'>{t["menu"][1]}<')
            content = content.replace('>Подбор<', f'>{t["menu"][2]}<')
            content = content.replace('>Услуги<', f'>{t["menu"][3]}<')
            content = content.replace('>Отзывы<', f'>{t["menu"][4]}<')

            # 4. Характеристики (Specs)
            spec_labels = {
                'ru': {'area': 'Площадь', 'plot': 'Участок', 'floor': 'Этаж', 'floors': 'Этажей', 'rooms': 'Комнат'},
                'en': {'area': 'Area', 'plot': 'Plot', 'floor': 'Floor', 'floors': 'Floors', 'rooms': 'Rooms'},
                'de': {'area': 'Fläche', 'plot': 'Grundstück', 'floor': 'Etage', 'floors': 'Etagen', 'rooms': 'Zimmer'},
                'zh': {'area': '面积', 'plot': '土地', 'floor': '楼层', 'floors': '层数', 'rooms': '房间'}
            }
            sl = spec_labels.get(lang, spec_labels['ru'])
            
            content = content.replace('>Площадь</div>', f'>{sl["area"]}</div>')
            content = content.replace('>300 м²</div>', f'>{get_text("stats").split("|")[0].strip()}</div>')
            
            if prop_type == 'house':
                content = content.replace('>Участок</div>', f'>{sl["plot"]}</div>')
            else:
                content = content.replace('>Участок</div>', f'>{sl["floor"]}</div>')
            
            content = content.replace('>Этажей</div>', f'>{sl["floors"]}</div>')
            content = content.replace('>8.5 сот.</div>', f'>{get_text("stats").split("|")[-1].strip()}</div>')
            content = content.replace('>Комнат</div>', f'>{sl["rooms"]}</div>')

            # 5. Описание и преимущества
            desc = get_text('description')
            desc_html = desc.replace('\n', '</p><p>').replace('\\n', '</p><p>')
            new_desc_html = f'<div class="description"><h3>{about_heading}</h3><p>{desc_html}</p></div>'
            # Более гибкая регулярка для замены описания
            description_pattern = r'<div class="description">\s*<h3>О доме</h3>.*?</div>'
            content = re.sub(description_pattern, new_desc_html, content, flags=re.DOTALL)

            features = prop.get('features', [])
            feat_list = features.get(lang, features.get('ru', [])) if isinstance(features, dict) else features
            features_html = f'<div class="description"><h3>{t["headings"]["features"]}</h3><div class="features-list">'
            for f in feat_list:
                features_html += f'<div class="feature-item"><i class="fas fa-check"></i> {f}</div>'
            features_html += '</div></div>'
            # Исправленная регулярка: жадный поиск до закрывающего тега property-info (перед SIDEBAR)
            features_pattern = r'<div class="description">\s*<h3>Преимущества</h3>.*?(?=\s*</div>\s*<!-- SIDEBAR -->)'
            content = re.sub(features_pattern, features_html, content, flags=re.DOTALL)

            # 6. Остальные замены (включая страховку для заголовков)
            content = content.replace('<h3>О доме</h3>', f'<h3>{about_heading}</h3>')
            content = content.replace('<h3>Преимущества</h3>', f'<h3>{t["headings"]["features"]}</h3>')
            content = content.replace('Расположение</h3>', f'{t["headings"]["location"]}</h3>')
            content = content.replace('Записаться на просмотр</button>', f'{t["headings"]["viewing"]}</button>')
            content = content.replace('Ведущий специалист', t['agent_role'])
            content = content.replace('Калинингад и область', t['sub_phone'])
            content = content.replace('>Главная<', f'>{t["breadcrumb_home"]}<')
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
            # photos.sort() # Сортировка уже сделана правильно выше
            gallery_html = f'<div class="gallery-grid" onclick="openGallery(0)">\n'
            
            # Определяем путь к главному фото
            if photos:
                if '/' in photos[0]: # Это уже полный путь из JSON
                   main_img = photos[0]
                else: # Это просто имя файла из папки
                   main_img = f"images/object-{obj_id}/{photos[0]}"
            else:
                main_img = "images/placeholder.jpg"

            gallery_html += f'''            <div class="gallery-item gallery-main">
                <img src="{main_img}" alt="{title}">
                <div class="gallery-overlay"><i class="far fa-image"></i> {photo_count} фото</div>
            </div>\n'''
            
            for i in range(1, min(5, photo_count)):
                if '/' in photos[i]:
                    img_path = photos[i]
                else:
                    img_path = f"images/object-{obj_id}/{photos[i]}"
                gallery_html += f'''            <div class="gallery-item">
                <img src="{img_path}" alt="фото {i+1}">
            </div>\n'''
            
            gallery_html += '        </div>'
            
            content = re.sub(
                r'<div class="gallery-grid".*?</div>', 
                gallery_html, 
                content, 
                flags=re.DOTALL
            )
            
            # --- JS ЦИКЛ ---
            # Формируем массив реальных имен файлов
            final_photos_list = []
            for p in photos:
                if '/' in p:
                    final_photos_list.append(p)
                else:
                    final_photos_list.append(f"images/object-{obj_id}/{p}")
            
            js_photos_array = json.dumps(final_photos_list)
            
            js_code = f'const allPhotos = {js_photos_array};\n        const photoCount = {photo_count};'
            
            # Заменяем старый хардкод:
            # const allPhotos = [];
            # for (let i = 1; i <= 39; i++) { ... }
            # let currentImgIdx = 0;
            
            # Используем более широкий захват до следующей переменной
            content = re.sub(
                r'const allPhotos = \[\];.*?(?=let currentImgIdx)',
                f'{js_code}\n\n        ',
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
