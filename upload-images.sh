#!/bin/bash

# 🚀 Скрипт для загрузки папки images/ на GitHub
# Использование: ./upload-images.sh

echo "🎯 Загрузка папки images/ на GitHub"
echo "===================================="
echo ""

# Проверяем, что мы в правильной директории
if [ ! -d "images" ]; then
    echo "❌ Ошибка: папка images/ не найдена!"
    echo "Убедитесь, что вы запускаете скрипт из корня проекта"
    exit 1
fi

# Проверяем количество файлов в images/
file_count=$(ls -1 images/ | wc -l | tr -d ' ')
echo "📁 Найдено файлов в images/: $file_count"
echo ""

if [ "$file_count" -eq 0 ]; then
    echo "⚠️  Папка images/ пустая!"
    echo "Добавьте изображения в папку images/ перед загрузкой"
    exit 1
fi

# Показываем файлы
echo "📸 Файлы для загрузки:"
ls -lh images/
echo ""

# Спрашиваем URL репозитория
echo "🔗 Введите URL вашего GitHub репозитория:"
echo "Пример: https://github.com/username/repo-name.git"
read -p "URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ URL не может быть пустым!"
    exit 1
fi

# Проверяем, инициализирован ли git
if [ ! -d ".git" ]; then
    echo ""
    echo "📦 Инициализация Git репозитория..."
    git init
    git remote add origin "$REPO_URL"
    git branch -M main
    echo "✅ Git инициализирован"
else
    echo ""
    echo "✅ Git репозиторий уже инициализирован"
fi

# Добавляем файлы
echo ""
echo "➕ Добавление файлов в Git..."
git add images/

# Проверяем статус
echo ""
echo "📊 Статус:"
git status --short

# Коммит
echo ""
read -p "💬 Введите комментарий для коммита (Enter = 'Добавлены изображения'): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Добавлены изображения для сайта"}

git commit -m "$COMMIT_MSG"

# Пуш
echo ""
echo "🚀 Загрузка на GitHub..."
echo "⚠️  Если появится конфликт, используйте: git pull origin main --allow-unrelated-histories"
echo ""

read -p "Продолжить загрузку? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Успешно загружено на GitHub!"
        echo ""
        echo "🌐 Проверьте изображения по адресу:"
        # Извлекаем username и repo из URL
        REPO_PATH=$(echo "$REPO_URL" | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
        echo "https://${REPO_PATH}/tree/main/images"
        echo ""
        echo "🖼️  Прямая ссылка на изображение:"
        FIRST_IMAGE=$(ls images/ | head -n 1)
        USERNAME=$(echo "$REPO_PATH" | cut -d'/' -f1)
        REPONAME=$(echo "$REPO_PATH" | cut -d'/' -f2)
        echo "https://${USERNAME}.github.io/${REPONAME}/images/${FIRST_IMAGE}"
    else
        echo ""
        echo "❌ Ошибка при загрузке!"
        echo "Попробуйте вручную:"
        echo "  git pull origin main --allow-unrelated-histories"
        echo "  git push origin main"
    fi
else
    echo "❌ Загрузка отменена"
fi
