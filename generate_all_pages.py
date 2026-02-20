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
        # Только переводим если нужно, или просто убеждаемся что структура правильная
        properties[i] = translate_property_data(prop, force_retranslate=False)
    
    # Сохраняем обновленные данные с переводами
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(properties, f, indent=4, ensure_ascii=False)
    print("\n✅ Переводы сохранены в data.json")
    
    # --- ОБНОВЛЕНИЕ JS/PROPERTIES.JS ---
    # Читаем текущий js файл
    js_path = 'js/properties.js'
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Заменяем блок const propertiesData = [...]
        # Используем json.dumps чтобы корректно сформировать JS объект
        new_data_js = "const propertiesData = " + json.dumps(properties, indent=4, ensure_ascii=False) + ";"
        
        # Регулярка ищет от 'const propertiesData = [' до '];'
        # Но так как внутри могут быть скобки, надежнее найти начало и до function renderProperties
        # Или просто заменить всё от const propertiesData до ; (но там много строк)
        # Попробуем заменить весь блок
        
        # Стратегия: Ищем 'const propertiesData =' и ';' перед 'function renderProperties'
        # Или проще: полностью перезаписываем блок, зная структуру файла
        
        # Вариант: Найти начало и конец массива
        # Ищем начало переменной более гибко
        start_match = re.search(r'const\s+propertiesData\s*=', js_content)
        if start_match:
            start_idx = start_match.start()
            
            # Надежнее: найти function renderProperties и отступить назад
            func_match = re.search(r'function\s+renderProperties\s*\(\)', js_content)
            if func_match:
                func_idx = func_match.start()
                
                # Собираем файл заново
                new_js_content = js_content[:start_idx] + new_data_js + "\n\n" + js_content[func_idx:]
                
                # Перезаписываем файл
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(new_js_content)
                print("✅ Обновлен файл js/properties.js")
            else:
                 print("⚠️ Не удалось найти функцию renderProperties в js/properties.js")
        else:
             print("⚠️ Не удалось найти const propertiesData в js/properties.js")

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
            
            # --- AI: SCHEMA.ORG JSON-LD GENERATION ---
            def generate_schema_json(p, l):
                # Map type
                pt = p.get('type', 'house')
                schema_type = "House" if pt in ['house', 'townhouse'] else "Apartment"
                
                # Clean price
                raw_price = p.get('price', {}).get(l, p.get('price', {}).get('ru', ''))
                # Remove spaces and non-numeric except dot/comma
                clean_p = "".join(filter(lambda x: x.isdigit() or x in '.,', raw_price))
                clean_p = clean_p.replace(',', '.')
                
                currency = "RUB"
                if '€' in raw_price: currency = "EUR"
                elif '¥' in raw_price: currency = "CNY"
                elif '$' in raw_price: currency = "USD"

                schema = {
                    "@context": "https://schema.org",
                    "@type": schema_type,
                    "name": p.get('title', {}).get(l, p.get('title', {}).get('ru', '')),
                    "description": p.get('description', {}).get(l, p.get('description', {}).get('ru', '')),
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": "Kaliningrad",
                        "streetAddress": p.get('location', {}).get(l, p.get('location', {}).get('ru', ''))
                    },
                    "offers": {
                        "@type": "Offer",
                        "price": clean_p or "0",
                        "priceCurrency": currency,
                        "availability": "https://schema.org/InStock"
                    }
                }
                
                # Add images if any
                if p.get('images'):
                    schema["image"] = ["https://balthomes.ru/" + img for img in p['images'][:5]]

                return f'<script type="application/ld+json">\n{json.dumps(schema, indent=4, ensure_ascii=False)}\n</script>'

            content = content.replace('{{ SCHEMA_JSON_LD }}', generate_schema_json(prop, lang))
            
            # --- HELPER: Get translation for a field ---
            def get_text(field):
                if field in prop:
                    val = prop[field]
                    if isinstance(val, dict):
                        return val.get(lang, val.get('ru', ''))
                    return str(val)
                return ''

            # 1. Page Metadata
            title = get_text('title')
            location = get_text('location')
            price = get_text('price')
            description = get_text('description')
            
            # 2. Property Type Deduction
            prop_type = prop.get('type', 'house')
            if not prop_type:
                title_ru = prop.get('title', {}).get('ru', '').lower()
                if any(kw in title_ru for kw in ['квартира', 'апартамент', 'студия']): prop_type = 'apartment'
                elif 'таунхаус' in title_ru: prop_type = 'townhouse'
                else: prop_type = 'house'

            # 3. Translation Dictionary
            trans = {
                'ru': {
                    'subtitle': '<span>Б</span><span>а</span><span>л</span><span>т</span><span>и</span><span>й</span><span>с</span><span>к</span><span>и</span><span>е</span><span>&nbsp;</span><span>д</span><span>о</span><span>м</span><span>а</span>',
                    'menu': {
                        'Catalog': 'Каталог',
                        'Coast': 'Побережье',
                        'Selection': 'Подбор',
                        'Services': 'Услуги',
                        'Reviews': 'Отзывы'
                    },
                    'agent_role': 'Ведущий специалист',
                    'sub_phone': 'Калининград и область',
                    'breadcrumb_home': 'Главная',
                    'breadcrumb_loc': 'Калининград',
                    'home_link': 'index.html',
                    'about': {'house': 'О доме', 'apartment': 'О квартире', 'townhouse': 'О таунхаусе'},
                    'features_lbl': 'Преимущества',
                    'location_lbl': 'Расположение',
                    'spec_labels': {'area': 'Площадь', 'plot': 'Участок', 'floor': 'Этаж', 'floors': 'Этажей', 'rooms': 'Комнат'},
                    'form': {'name': 'Ваше имя', 'phone': 'Номер телефона', 'msg': 'Меня интересует этот объект', 'submit': 'Записаться на просмотр', 'tg': '*Новая заявка с сайта*'}
                },
                'en': {
                    'subtitle': '<span>B</span><span>a</span><span>l</span><span>t</span><span>i</span><span>c</span><span>&nbsp;</span><span>H</span><span>o</span><span>m</span><span>e</span><span>s</span>',
                    'menu': {
                        'Catalog': 'Catalog',
                        'Coast': 'Coastline',
                        'Selection': 'Selection',
                        'Services': 'Services',
                        'Reviews': 'Reviews'
                    },
                    'agent_role': 'Leading Specialist',
                    'sub_phone': 'Kaliningrad & Region',
                    'breadcrumb_home': 'Home',
                    'breadcrumb_loc': 'Kaliningrad',
                    'home_link': 'en.html',
                    'about': {'house': 'About House', 'apartment': 'About Apartment', 'townhouse': 'About Townhouse'},
                    'features_lbl': 'Features',
                    'location_lbl': 'Location',
                    'spec_labels': {'area': 'Area', 'plot': 'Plot', 'floor': 'Floor', 'floors': 'Floors', 'rooms': 'Rooms'},
                    'form': {'name': 'Your Name', 'phone': 'Phone Number', 'msg': 'I am interested in this property', 'submit': 'Book a Viewing', 'tg': '*New lead from website*'}
                },
                'de': {
                    'subtitle': '<span>B</span><span>a</span><span>l</span><span>т</span><span>и</span><span>с</span><span>к</span><span>и</span><span>е</span><span>&nbsp;</span><span>H</span><span>ä</span><span>u</span><span>s</span><span>e</span><span>r</span>',
                    'menu': {
                        'Catalog': 'Katalog',
                        'Coast': 'Ostseeküste',
                        'Selection': 'Auswahl',
                        'Services': 'Leistungen',
                        'Reviews': 'Bewertungen'
                    },
                    'agent_role': 'Führender Spezialist',
                    'sub_phone': 'Kaliningrad & Region',
                    'breadcrumb_home': 'Startseite',
                    'breadcrumb_loc': 'Kaliningrad',
                    'home_link': 'de.html',
                    'about': {'house': 'Über das Haus', 'apartment': 'Über die Wohnung', 'townhouse': 'Über das Townhouse'},
                    'features_lbl': 'Vorteile',
                    'location_lbl': 'Lage',
                    'spec_labels': {'area': 'Fläche', 'plot': 'Grundstück', 'floor': 'Etage', 'floors': 'Etagen', 'rooms': 'Zimmer'},
                    'form': {'name': 'Ihr Name', 'phone': 'Telefonnummer', 'msg': 'Ich interessiere mich für dieses Objekt', 'submit': 'Besichtigung buchen', 'tg': '*Neue Anfrage von der Website*'}
                },
                'zh': {
                    'subtitle': '<span>波</span><span>罗</span><span>的</span><span>海</span><span>之</span><span>家</span>',
                    'menu': {
                        'Catalog': '房产目录',
                        'Coast': '海岸线',
                        'Selection': '选房',
                        'Services': '服务',
                        'Reviews': '评论'
                    },
                    'agent_role': '首席专家',
                    'sub_phone': '加里宁格勒及地区',
                    'breadcrumb_home': '首页',
                    'breadcrumb_loc': '加里宁格勒',
                    'home_link': 'zh.html',
                    'about': {'house': '关于房屋', 'apartment': '关于公寓', 'townhouse': '关于联排别墅'},
                    'features_lbl': '房产特色',
                    'location_lbl': '地理位置',
                    'spec_labels': {'area': '面积', 'plot': '土地', 'floor': '楼层', 'floors': '层数', 'rooms': '房间'},
                    'form': {'name': '您的姓名', 'phone': '电话号码', 'msg': '我对这个房产感兴趣', 'submit': '预约看房', 'tg': '*来自网站的新询盘*'}
                }
            }
            t = trans.get(lang, trans['ru'])

            # 4. Fill Placeholders
            content = content.replace('{{ BREADCRUMB_HOME }}', t['breadcrumb_home'])
            content = content.replace('{{ BREADCRUMB_TITLE }}', title)
            content = content.replace('{{ BREADCRUMB_LOC }}', location.split(',')[0]) # Simplification
            
            content = content.replace('{{ TITLE }}', title)
            content = content.replace('<title>Дом в Зеленоградске 300 м² | BaltHomes — Элитная недвижимость</title>', f'<title>{title} | BaltHomes</title>')
            content = content.replace('{{ LOCATION }}', location)
            content = content.replace('{{ PRICE }}', price)
            
            content = content.replace('{{ SUBTITLE }}', t['subtitle'])
            content = content.replace('{{ HOME_LINK }}', t['home_link'])
            
            # Menu
            if isinstance(t['menu'], dict):
                content = content.replace('{{ MENU_CATALOG }}', t['menu'].get('Catalog', ''))
                content = content.replace('{{ MENU_COAST }}', t['menu'].get('Coast', ''))
                content = content.replace('{{ MENU_SELECTION }}', t['menu'].get('Selection', ''))
                content = content.replace('{{ MENU_SERVICES }}', t['menu'].get('Services', ''))
                content = content.replace('{{ MENU_REVIEWS }}', t['menu'].get('Reviews', ''))
            else:
                # Backwards compatibility
                content = content.replace('{{ MENU_CATALOG }}', t['menu'][0])
                content = content.replace('{{ MENU_COAST }}', t['menu'][1])
                content = content.replace('{{ MENU_SELECTION }}', t['menu'][2])
                content = content.replace('{{ MENU_SERVICES }}', t['menu'][3])
                content = content.replace('{{ MENU_REVIEWS }}', t['menu'][4] if len(t['menu']) > 4 else '')

            # Specs logic
            specs = prop.get('specs', {}).get(lang, prop.get('specs', {}).get('ru', {}))
            
            # Normalize spec keys (handle both Area and area)
            def find_spec(keys):
                for k in keys:
                    if k in specs and specs[k]: return specs[k]
                return '—'

            if prop_type == 'house':
                s1_lbl, s1_val = t['spec_labels']['area'], find_spec(['area', 'Area', 'houseArea']) + " м²"
                s2_lbl, s2_val = t['spec_labels']['plot'], find_spec(['plot', 'Plot', 'landArea']) + " сот."
                s3_lbl, s3_val = t['spec_labels']['floors'], find_spec(['floors', 'Floors'])
                s4_lbl, s4_val = t['spec_labels']['rooms'], find_spec(['rooms', 'Rooms'])
            else:
                s1_lbl, s1_val = t['spec_labels']['area'], find_spec(['area', 'Area']) + " м²"
                s2_lbl, s2_val = t['spec_labels']['floor'], find_spec(['floor', 'Floor'])
                s3_lbl, s3_val = t['spec_labels']['floors'], find_spec(['floors', 'Floors'])
                s4_lbl, s4_val = t['spec_labels']['rooms'], find_spec(['rooms', 'Rooms'])

            content = content.replace('{{ SPEC_1_LBL }}', s1_lbl)
            content = content.replace('{{ SPEC_1_VAL }}', s1_val)
            content = content.replace('{{ SPEC_1_VAL }}', s1_val) # Duplicate for safety
            content = content.replace('{{ SPEC_2_LBL }}', s2_lbl)
            content = content.replace('{{ SPEC_2_VAL }}', s2_val)
            content = content.replace('{{ SPEC_3_LBL }}', s3_lbl)
            content = content.replace('{{ SPEC_3_VAL }}', s3_val)
            content = content.replace('{{ SPEC_4_LBL }}', s4_lbl)
            content = content.replace('{{ SPEC_4_VAL }}', s4_val)

            # Description
            desc_html = description.replace('\n', '</p><p>').replace('\\n', '</p><p>')
            content = content.replace('{{ DESCRIPTION_BLOCK }}', f'<div class="description"><h3>{t["about"][prop_type]}</h3><p>{desc_html}</p></div>')
            
            # Features
            feat_list = prop.get('features', {}).get(lang, prop.get('features', {}).get('ru', [])) if isinstance(prop.get('features'), dict) else prop.get('features', [])
            feat_html = f'<div class="description"><h3>{t["features_lbl"]}</h3><div class="features-list">'
            for f in feat_list:
                feat_html += f'<div class="feature-item"><i class="fas fa-check"></i> {f}</div>'
            feat_html += '</div></div>'
            content = content.replace('{{ FEATURES_BLOCK }}', feat_html)

            # Map
            map_html = prop.get('mapUrl', '')
            if not map_html or '<iframe' not in map_html:
                # Fallback map or search
                map_html = f'<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2000!2d20.43!3d54.94!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2z{location}" width="100%" height="100%" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
            else:
                # Ensure width/height are 100%
                map_html = map_html.replace('width="600"', 'width="100%"').replace('height="450"', 'height="100%"')
            content = content.replace('{{ MAP_IFRAME }}', map_html)

            # Form
            content = content.replace('{{ FORM_OBJECT_VALUE }}', f"{title} (ID {obj_id})")
            content = content.replace('{{ FORM_NAME_PLH }}', t['form']['name'])
            content = content.replace('{{ FORM_PHONE_PLH }}', t['form']['phone'])
            content = content.replace('{{ FORM_MSG_PLH }}', t['form']['msg'])
            content = content.replace('{{ FORM_SUBMIT_BTN }}', t['form']['submit'])
            content = content.replace('{{ TG_MSG_HEADER }}', f"{t['form']['tg']} ({title}, ID {obj_id})")

            # --- GALLERY ---
            if photos:
                main_img = photos[0] if '/' in photos[0] else f"images/object-{obj_id}/{photos[0]}"
            else:
                main_img = "images/placeholder.jpg"
            
            gallery_html = f'<div class="gallery-grid" onclick="openGallery(0)">\n'
            gallery_html += f'''            <div class="gallery-item gallery-main">
                <img src="{main_img}" alt="{title}">
                <div class="gallery-overlay"><i class="far fa-image"></i> {photo_count} фото</div>
            </div>\n'''
            
            for i in range(1, min(5, photo_count)):
                img_p = photos[i] if '/' in photos[i] else f"images/object-{obj_id}/{photos[i]}"
                gallery_html += f'''            <div class="gallery-item">
                <img src="{img_p}" alt="{title} — фото {i+1}">
            </div>\n'''
            gallery_html += '        </div>'
            content = content.replace('{{ GALLERY_GRID }}', gallery_html)

            # JS Gallery
            final_photos = []
            for p in photos:
                final_photos.append(p if '/' in p else f"images/object-{obj_id}/{p}")
            content = content.replace('{{ GALLERY_JS }}', f'const allPhotos = {json.dumps(final_photos)};')

            # Lang Switchers
            def make_sw(is_mob):
                cls = "lang-switcher mobile-lang-switcher" if is_mob else "lang-switcher"
                h = f'<div class="{cls}">'
                for l in ['ru', 'en', 'de', 'zh']:
                    link = f'object-{obj_id}.html' if l == 'ru' else f'object-{obj_id}-{l}.html'
                    active_cls = ' class="active"' if l == lang else ''
                    h += f'<a href="{link}"{active_cls}>{l.upper()}</a>'
                return h + '</div>'
            
            content = content.replace('{{ MOBILE_LANG_SWITCHER }}', make_sw(True))
            content = content.replace('{{ DESKTOP_LANG_SWITCHER }}', make_sw(False))



            # Save
            f_name = f"object-{obj_id}.html" if lang == 'ru' else f"object-{obj_id}-{lang}.html"
            with open(f_name, 'w', encoding='utf-8') as out:
                out.write(content)

    print("✅ Генерирация страниц завершена")

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
