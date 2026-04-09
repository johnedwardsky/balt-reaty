import os

with open('templates/full-object-template.html', 'r', encoding='utf-8') as f:
    html = f.read()

parts = html.split('<main class="container property-hero">')
head_and_header = parts[0]
footer_and_scripts = '</main>' + html.split('</main>')[1]

# Remove gallery javascript from footer
import re
footer_and_scripts = re.sub(r'let currentImgIdx = 0;.*?\}\);', '', footer_and_scripts, flags=re.DOTALL)
footer_and_scripts = re.sub(r'const thumbContainer.*?', '', footer_and_scripts)
footer_and_scripts = re.sub(r'allPhotos\.forEach.*?\}\);', '', footer_and_scripts, flags=re.DOTALL)
footer_and_scripts = re.sub(r'\{\{\s*GALLERY_JS\s*\}\}', '', footer_and_scripts)


blog_index_html = head_and_header + """<main class="container" style="padding-top: 50px; padding-bottom: 80px; min-height: 60vh;">
    <h1 style="text-align: center; margin-bottom: 40px; color: var(--primary);">{{ BLOG_MAIN_TITLE }}</h1>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px;">
        {{ ARTICLES_GRID }}
    </div>
""" + footer_and_scripts

blog_article_html = head_and_header + """<main class="container" style="max-width: 800px; padding-top: 50px; padding-bottom: 80px; min-height: 60vh;">
    <a href="{{ BLOG_HOME_URL }}" style="display: inline-block; margin-bottom: 20px; color: var(--accent); font-weight: 600; font-size: 14px;"><i class="fas fa-arrow-left"></i> Назад в блог</a>
    <img src="{{ ARTICLE_IMAGE }}" alt="Фото статьи" style="width: 100%; height: 400px; object-fit: cover; border-radius: 20px; margin-bottom: 30px; box-shadow: var(--shadow);">
    <div style="font-size: 14px; color: #777; margin-bottom: 10px;">{{ ARTICLE_DATE }}</div>
    <h1 style="margin-bottom: 30px; color: var(--primary); font-size: 32px; line-height: 1.3;">{{ ARTICLE_TITLE }}</h1>
    <div class="article-content" style="font-size: 18px; line-height: 1.8; color: #444;">
       {{ ARTICLE_CONTENT }}
    </div>
    <style>
        .article-content h2 { margin-top: 40px; margin-bottom: 15px; font-size: 24px; color: var(--primary); }
        .article-content p { margin-bottom: 20px; }
        .article-content ul { margin-bottom: 20px; padding-left: 20px; }
        .article-content li { margin-bottom: 10px; }
    </style>
""" + footer_and_scripts

with open('templates/blog-index-template.html', 'w', encoding='utf-8') as f:
    f.write(blog_index_html)

with open('templates/blog-article-template.html', 'w', encoding='utf-8') as f:
    f.write(blog_article_html)

print("✅ Templates created successfully")
