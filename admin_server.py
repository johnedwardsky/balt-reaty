from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_JSON = os.path.join(BASE_DIR, 'data.json')
PROPERTIES_JS = os.path.join(BASE_DIR, 'js', 'properties.js')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

def read_properties():
    if not os.path.exists(DATA_JSON):
        return []
    with open(DATA_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_properties(data):
    # 1. Save to data.json (Source of Truth)
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # 2. Sync to js/properties.js (For Browser)
    with open(PROPERTIES_JS, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # We find where the array starts and ends to preserve the surrounding JS functions
    new_data_str = json.dumps(data, indent=4, ensure_ascii=False)
    
    start_line = -1
    end_line = -1
    for i, line in enumerate(lines):
        if 'const propertiesData = [' in line:
            start_line = i
        if start_line != -1 and '];' in line and end_line == -1:
            # Simple check for the end of the array assignment
            end_line = i
            break
            
    if start_line != -1 and end_line != -1:
        new_content = lines[:start_line]
        new_content.append(f"const propertiesData = {new_data_str};\n")
        new_content.extend(lines[end_line+1:])
        with open(PROPERTIES_JS, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
    else:
        # Fallback if structure changed
        with open(PROPERTIES_JS, 'w', encoding='utf-8') as f:
            f.write(f"const propertiesData = {new_data_str};\n\n")
            # We would lose functions here, but this is a safety fallback. 
            # In real usage, the structure should be stable.

STATS_JSON = os.path.join(BASE_DIR, 'stats.json')

def read_stats():
    if not os.path.exists(STATS_JSON):
        return {"views": {}, "banner": {"impressions": 0, "clicks": 0, "config": {"type": "image", "videoUrl": ""}}, "pages": {}}
    with open(STATS_JSON, 'r', encoding='utf-8') as f:
        stats = json.load(f)
        if 'config' not in stats['banner']:
            stats['banner']['config'] = {"type": "image", "videoUrl": ""}
        return stats

def save_stats(stats):
    with open(STATS_JSON, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

@app.route('/api/banner-config', methods=['POST'])
def save_banner_config():
    config = request.json
    stats = read_stats()
    stats['banner']['config'] = config
    save_stats(stats)
    
    # Sync to js/properties.js
    with open(PROPERTIES_JS, 'r', encoding='utf-8') as f:
        content = f.read()
    
    config_js = f"const bannerConfig = {json.dumps(config, indent=4, ensure_ascii=False)};"
    
    if 'const bannerConfig =' in content:
        import re
        content = re.sub(r'const bannerConfig = \{.*?\};', config_js, content, flags=re.DOTALL)
    else:
        content = config_js + "\n\n" + content
        
    with open(PROPERTIES_JS, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return jsonify({"status": "success"})

@app.route('/api/properties', methods=['GET'])
def get_properties():
    return jsonify(read_properties())

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(read_stats())

@app.route('/api/stats/track', methods=['POST'])
def track_stats():
    data = request.json
    t = data.get('type')
    obj_id = str(data.get('id'))
    
    stats = read_stats()
    
    if t == 'object':
        stats['views'][obj_id] = stats['views'].get(obj_id, 0) + 1
    elif t == 'banner_impression':
        stats['banner']['impressions'] += 1
    elif t == 'banner_click':
        stats['banner']['clicks'] += 1
    elif t == 'page_view':
        stats['pages'][obj_id] = stats['pages'].get(obj_id, 0) + 1
        
    save_stats(stats)
    return jsonify({"status": "success"})

@app.route('/api/properties', methods=['POST'])
def update_properties():
    data = request.json
    save_properties(data)
    return jsonify({"status": "success"})

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    files = request.files.getlist('image')
    obj_id = request.form.get('id')
    
    # Определяем папку назначения
    if obj_id:
        target_dir = os.path.join(IMAGES_DIR, f"object-{obj_id}")
    else:
        target_dir = IMAGES_DIR # Fallback
        
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        
    saved_paths = []
    for file in files:
        if file.filename:
            filename = file.filename
            filepath = os.path.join(target_dir, filename)
            file.save(filepath)
            # Возвращаем путь относительно корня сайта
            rel_path = f"images/object-{obj_id}/{filename}" if obj_id else f"images/{filename}"
            saved_paths.append(rel_path)
    
    if saved_paths:
        # Return first path for single-upload compatibility, and all paths for multi-upload
        return jsonify({
            "status": "success", 
            "path": saved_paths[0], 
            "paths": saved_paths
        })
    
    return jsonify({"status": "error"}), 400

@app.route('/api/generate-pages', methods=['POST'])
def generate_pages():
    import subprocess
    try:
        # Запускаем скрипт генерации страниц
        result = subprocess.run(
            ['python3', 'generate_all_pages.py'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return jsonify({"status": "success", "message": result.stdout})
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/deploy', methods=['POST'])
def deploy_to_github():
    import subprocess
    try:
        # 1. Add all changes
        subprocess.run(['git', 'add', '.'], cwd=BASE_DIR, check=True)
        
        # 2. Commit (ignore error if nothing to commit)
        subprocess.run(['git', 'commit', '-m', 'Content update from Admin Panel'], cwd=BASE_DIR, check=False)
        
        # 3. Push
        result = subprocess.run(['git', 'push', 'origin', 'main'], cwd=BASE_DIR, capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({"status": "success", "message": "Deployed successfully"})
        else:
            return jsonify({"status": "error", "message": result.stderr}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin')
def admin_page():
    path = os.path.join(BASE_DIR, 'admin', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    os.makedirs('images', exist_ok=True)
    app.run(port=8000, debug=False)
