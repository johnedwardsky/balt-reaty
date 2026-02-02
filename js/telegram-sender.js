/**
 * Скрипт отправки формы в Telegram.
 * 
 * ВНИМАНИЕ: Для работы вам нужно:
 * 1. Получить токен бота у @BotFather в Telegram.
 * 2. Узнать свой ID у @userinfobot или аналогичного бота.
 * 3. Вставить их ниже в переменные.
 */

// !!! ЗАМЕНИТЕ ЭТИ ЗНАЧЕНИЯ !!!
const TELEGRAM_BOT_TOKEN = '8210607938:AAHjhkVwJiCXTLJ3enh9OzdY_9QZ9D5LoJs';
const TELEGRAM_CHAT_ID = '7622360260';

async function sendToTelegram(event) {
    event.preventDefault(); // Остановить стандартную отправку формы

    const form = event.target;
    const formData = new FormData(form);

    // Сбор данных из формы
    const messageLines = [];
    messageLines.push(`🔔 *Новая заявка с сайта!*`);

    formData.forEach((value, key) => {
        // Пропускаем пустые поля если нужно
        if (value) {
            messageLines.push(`🔹 *${key}:* ${value}`);
        }
    });

    const message = messageLines.join('\n');

    const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: TELEGRAM_CHAT_ID,
                text: message,
                parse_mode: 'Markdown'
            })
        });

        if (response.ok) {
            // Перенаправление на страницу "Спасибо"
            window.location.href = 'thanks.html';
        } else {
            console.error('Ошибка отправки:', await response.text());
            alert('Что-то пошло не так. Попробуйте снова или свяжитесь по телефону.');
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
        alert('Проблема с подключением. Проверьте интернет.');
    }
}

// Привязываем функцию к форме, когда документ загрузится
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form'); // Или конкретный ID формы
    if (form) {
        form.addEventListener('submit', sendToTelegram);
    }
});
