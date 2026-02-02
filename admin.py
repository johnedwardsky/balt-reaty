import tkinter as tk
from tkinter import messagebox, filedialog
import json
import shutil
import os

DATA_FILE = "data.json"
JS_FILE = "js/properties.js"
IMAGES_DIR = "images"

# Ensure images directory exists
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Админка Balthomes")
        self.properties = []
        self.load_data()

        # Left Listbox
        self.listbox = tk.Listbox(root, width=40, height=20)
        self.listbox.pack(side=tk.LEFT, padx=10, pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        # Right frame for inputs
        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.vars = {
            "title": tk.StringVar(),
            "price": tk.StringVar(),
            "description": tk.StringVar(),
            "meta1": tk.StringVar(), # Area
            "meta2": tk.StringVar(), # District or whatever
            "image": tk.StringVar()
        }

        # Inputs
        self.create_input("Заголовок:", "title")
        self.create_input("Цена:", "price")
        self.create_input("Описание:", "description")
        self.create_input("Параметр 1 (площадь):", "meta1")
        self.create_input("Параметр 2 (район/этаж):", "meta2")
        
        # Image picker
        tk.Label(self.frame, text="Картинка:").pack(anchor="w")
        img_frame = tk.Frame(self.frame)
        img_frame.pack(fill=tk.X)
        self.img_entry = tk.Entry(img_frame, textvariable=self.vars["image"])
        self.img_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(img_frame, text="Выбрать файл...", command=self.pick_image).pack(side=tk.RIGHT)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(side=tk.BOTTOM, pady=10)
        tk.Button(btn_frame, text="Новая квартира", command=self.new_property).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сохранить изменения", command=self.save_current).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить выбранное", command=self.delete_current).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="ЗАПИСАТЬ НА САЙТ", command=self.save_to_file, bg="green").pack(side=tk.LEFT, padx=20)

        self.current_index = None
        self.refresh_list()

    def create_input(self, label, key):
        tk.Label(self.frame, text=label).pack(anchor="w")
        tk.Entry(self.frame, textvariable=self.vars[key]).pack(fill=tk.X, pady=(0, 5))

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.properties = json.load(f)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for p in self.properties:
            self.listbox.insert(tk.END, p.get("title", "Без названия"))

    def on_select(self, event):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        self.current_index = index
        data = self.properties[index]
        for key in self.vars:
            self.vars[key].set(data.get(key, ""))

    def new_property(self):
        self.properties.append({
            "title": "Новая квартира",
            "price": "0 ₽",
            "description": "",
            "meta1": "",
            "meta2": "",
            "image": ""
        })
        self.refresh_list()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(tk.END)
        self.on_select(None)

    def save_current(self):
        if self.current_index is None:
            return
        
        data = {}
        for key in self.vars:
            data[key] = self.vars[key].get()
        
        self.properties[self.current_index] = data
        self.refresh_list()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.current_index)
        messagebox.showinfo("Успех", "Данные обновлены в памяти. Нажмите 'ЗАПИСАТЬ НА САЙТ', чтобы применить.")

    def delete_current(self):
        if self.current_index is None:
            return
        del self.properties[self.current_index]
        self.current_index = None
        self.refresh_list()
        for key in self.vars:
            self.vars[key].set("")

    def pick_image(self):
        filename = filedialog.askopenfilename(title="Выберите фото", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if filename:
            # Copy to images folder
            basename = os.path.basename(filename)
            target = os.path.join(IMAGES_DIR, basename)
            shutil.copy(filename, target)
            self.vars["image"].set(f"images/{basename}")

    def save_to_file(self):
        # 1. Save JSON
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.properties, f, indent=4, ensure_ascii=False)
        
        # 2. Generate JS
        js_content = "const properties = " + json.dumps(self.properties, indent=4, ensure_ascii=False) + ";\n"
        
        # Add the rendering logic (read from existing file or hardcode template)
        # Ideally, we should append the static JS functions.
        # Let's read the static part from properties.js if it exists, or use a hardcoded tail.
        
        js_tail = """
// Функция для отрисовки карточек
function renderProperties() {
    const container = document.getElementById('properties-container');
    if (!container) return; 

    container.innerHTML = ''; 

    properties.forEach(prop => {
        const cardHTML = `
            <div class="card">
                <div class="card-img">
                    <img src="${prop.image}" alt="${prop.title}">
                    <div class="card-price">${prop.price}</div>
                </div>
                <div class="card-body">
                    <h3>${prop.title}</h3>
                    <div class="card-meta">
                        <span>${prop.meta1}</span>
                        <span>${prop.meta2}</span>
                    </div>
                    <p style="font-size: 14px; color: #555;">${prop.description}</p>
                    <button class="btn btn-primary" onclick="openModal('${prop.title}')" style="width:100%; margin-top:10px;">Подробнее</button>
                </div>
            </div>
        `;
        container.innerHTML += cardHTML;
    });
}

document.addEventListener('DOMContentLoaded', renderProperties);

function openModal(propertyName) {
    const quizSection = document.getElementById('quiz');
    if(quizSection) {
        quizSection.scrollIntoView({behavior: 'smooth'});
        console.log("Интересует объект: " + propertyName);
    }
}
"""
        with open(JS_FILE, "w", encoding="utf-8") as f:
            f.write(js_content + js_tail)
            
        messagebox.showinfo("Готово", "Сайт обновлен! Откройте index.html чтобы проверить.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
