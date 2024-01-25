// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const chatsContainer = document.getElementById('chats');
    const messagesContainer = document.getElementById('messages');
    const messageContentInput = document.getElementById('message-content');
    const sendMessageBtn = document.getElementById('send-message-btn');

    // Функция для отображения чатов
    function displayChats(chats) {
        chatsContainer.innerHTML = '';
        chats.forEach(chat => {
            const chatItem = document.createElement('li');
            chatItem.textContent = chat.name;
            chatItem.addEventListener('click', function() {
                // При выборе чата загружаем сообщения
                getChatMessages(chat.id);
            });
            chatsContainer.appendChild(chatItem);
        });
    }

    // Функция для отображения сообщений
    function displayMessages(messages) {
        messagesContainer.innerHTML = '';
        messages.forEach(message => {
            const messageItem = document.createElement('li');
            messageItem.textContent = `${message.sender.user.username}: ${message.content}`;
            messagesContainer.appendChild(messageItem);
        });
    }

    // Функция для получения чатов с сервера
    function getChats() {
        fetch('/api/chats/')
            .then(response => response.json())
            .then(chats => {
                displayChats(chats);
            })
            .catch(error => console.error('Error:', error));
    }

    // Функция для получения сообщений из конкретного чата
    function getChatMessages(chatId) {
        fetch(`/api/messages/?chat=${chatId}`)
            .then(response => response.json())
            .then(messages => {
                displayMessages(messages);
            })
            .catch(error => console.error('Error:', error));
    }

    // Получаем чаты при загрузке страницы
    getChats();

    // Обработчик события для отправки сообщения
    sendMessageBtn.addEventListener('click', function() {
        const chatId = 1;  // Замените на реальный идентификатор чата
        const messageContent = messageContentInput.value;

        fetch(`/api/messages/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat: chatId,
                content: messageContent,
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Message sent:', data);
            // Обновление интерфейса или другие действия
            getChatMessages(chatId);  // Обновляем сообщения после отправки
        })
        .catch(error => console.error('Error:', error));
    });
});
