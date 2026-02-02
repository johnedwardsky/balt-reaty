
try:
    with open('index.html', 'rb') as f:
        content = f.read()
    
    # Try decoding
    text = content.decode('utf-8', errors='ignore')
    
    # Find start of HTML
    start = text.find('<')
    if start != -1:
        text = text[start:]
        
    with open('index_clean.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Cleaned successfully")
except Exception as e:
    print(e)
