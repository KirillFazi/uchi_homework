Тестовое задание: Разработка чат-бота поддержки для Moodle LMS
Цель
В этом задании вам нужно создать чат-бота для Moodle. Основная идея: бот должен искать ответы на вопросы пользователей в официальной документации Moodle (которую вы предварительно обработаете и сохраните в векторной базе данных, например, Qdrant или Chroma). 
Цель этого тестового задания — не нагрузить вас работой на неделю, а проверить умение использовать готовые инструменты и библиотеки для решения прикладной задачи.
Это вполне реально сделать за пару вечеров, так как вы будете использовать готовые библиотеки для обработки текста, векторных баз данных и языковых моделей. 
Главное — правильно настроить RAG и создать простое REST API для взаимодействия с ботом.
Требования
Обработка документации
Используйте общедоступную документацию Moodle, доступную по ссылке: Moodle User Documentation(https://docs.moodle.org/403/en/Main_page).
Реализуйте систему для извлечения текста из этих страниц и подготовки их для использования в RAG-конвейере.
Реализация RAG
Используйте векторную базу данных для хранения эмбеддингов документов.
Используйте одну из нижеперечисленных БД:
Qdrant
Chroma
Milvus
Реализуйте механизм поиска для нахождения наиболее релевантных частей документа на основе запросов пользователя.
Разработка чат-бота
Разработайте чат-бота с использованием языковой модели для генерации ответов на основе извлечённых частей документа.
Убедитесь, что чат-бот поддерживает контекст диалога и даёт связные ответы.
API для интеграции чат-бота на фронт или в приложение
Создайте REST API для того, чтобы чат-бота можно было интегрировать на сайт или в приложение. 
Документация и качество кода
Предоставьте README с инструкциями по настройке и запуску вашего решения.
Код должен быть читаемым, идиоматическим, с понятной структурой и валидными именами. Комментарии, ошибки — обрабатываются.
Ограничения
Используйте только локальные инструменты и библиотеки; внешние сервисы (например, OpenAI API, облачные векторные базы данных) запрещены.
Бот понимает русский и английский язык.
Предоставляемые материалы
Документация: Используйте указанные разделы из Moodle User Documentation.
Тестовые запросы пользователей и ожидаемые ответы
Примеры запросов пользователей, на которые должен ответить чат-бот:
Запрос: "Как создать новый курс в Moodle?"
Запрос: "Как настроить систему оценок в Moodle?"
Запрос: "Как просмотреть журналы активности пользователей?"
Критерии оценки
Что мы будем проверять в этом задании:
Точность ответов: чат-бот правильно отвечает на вопросы пользователей? Часто ли он неправильно понимает вопрос или отвечает совсем неверно?
Сложность и осмысленность решения: какие дополнительные инструменты вы использовали? Насколько архитектурные решения обоснованы?
Качество кода и документация: Код чистый, хорошо документированный и понятный? README понятен (как установить, запустить, что делает проект; описаны зависимости, требования, структура кода)?
Результаты, которые мы ожидаем получить
Исходный код чат-бота и системы RAG.
Документация (README.md).



