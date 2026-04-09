import re

with open('templates/full-object-template.html', 'r', encoding='utf-8') as f:
    full_html = f.read()

# Extract parts
head_part_match = re.search(r'(<!DOCTYPE html>.*?</header>)', full_html, re.DOTALL)
footer_part_match = re.search(r'(<footer class="footer".*</html>)', full_html, re.DOTALL)

if not head_part_match or not footer_part_match:
    print("Could not extract parts")
    exit(1)

head_part = head_part_match.group(1)
footer_part = footer_part_match.group(1)

# Modify head part slightly for blog index
blog_index_head = head_part.replace('{{ TITLE }} | BaltHomes — Элитная недвижимость', '{{ PAGE_TITLE }} | BaltHomes').replace('content="{{ META_DESCRIPTION }}"', 'content="{{ PAGE_DESCRIPTION }}"')

blog_index_html = blog_index_head + """
    <div class="container" style="padding-top: 50px; padding-bottom: 80px; min-height: 60vh;">
        <h1 style="text-align: center; margin-bottom: 40px; color: var(--primary);">{{ BLOG_MAIN_TITLE }}</h1>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px;">
            {{ ARTICLES_GRID }}
        </div>
    </div>
""" + footer_part

with open('templates/blog-index-template.html', 'w', encoding='utf-8') as f:
    f.write(blog_index_html)

blog_article_html = blog_index_head + """
    <article class="container" style="max-width: 800px; padding-top: 100px; padding-bottom: 80px; min-height: 60vh;">
        <a href="{{ BLOG_HOME_URL }}" style="display: inline-block; margin-bottom: 20px; color: var(--accent); font-weight: 600; font-size: 14px;"><i class="fas fa-arrow-left"></i> {{ BACK_TO_BLOG }}</a>
        <img src="{{ ARTICLE_IMAGE }}" alt="{{ ARTICLE_TITLE }}" style="width: 100%; height: 400px; object-fit: cover; border-radius: 20px; margin-bottom: 30px; box-shadow: var(--shadow);">
        <div style="font-size: 14px; color: #777; margin-bottom: 10px;">{{ ARTICLE_DATE }}</div>
        <h1 style="margin-bottom: 30px; color: var(--primary); font-size: 32px; line-height: 1.3;">{{ ARTICLE_TITLE }}</h1>
        <div class="article-content" style="font-size: 18px; line-height: 1.8; color: #444;">
           {{ ARTICLE_CONTENT }}
        </div>
    </article>
    <style>
        .article-content h2 { margin-top: 40px; margin-bottom: 15px; font-size: 24px; color: var(--primary); }
        .article-content p { margin-bottom: 20px; }
        .article-content ul { margin-bottom: 20px; padding-left: 20px; }
        .article-content li { margin-bottom: 10px; }
        .card:hover { transform: translateY(-5px); }
    </style>
""" + footer_part

# Cleanup gallery scripts which throw errors in blog context
for html_str, filename in [(blog_index_html, 'blog-index-template.html'), (blog_article_html, 'blog-article-template.html')]:
    cln = re.sub(r'let currentImgIdx = 0;.*?\}\);', '', html_str, flags=re.DOTALL)
    cln = re.sub(r'const thumbContainer.*?', '', cln)
    cln = re.sub(r'allPhotos\.forEach.*?\}\);', '', cln, flags=re.DOTALL)
    cln = re.sub(r'\{\s*{\s*GALLERY_JS\s*}\s*\}', '', cln)
    with open('templates/' + filename, 'w', encoding='utf-8') as f:
        f.write(cln)

print("Blog templates created.")

