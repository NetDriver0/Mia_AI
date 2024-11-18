# Mia_AI
Проект из себя представляет мои наработки по конкретному персонажу.
Основная цель данного проекта это сдвинуть рамки и ограничения существующих чат-бот систем, используя существующие методы работы с языковыми генеративными моделями.

На данный момент реализованы:
Cуммаризация части диалога, которая не входит в контекст.
Оценка суммаризации на количество символов (заготовка под COT)
Многоуровневая система суммаризаций (заготовка под RAG)

В планах:
Система запомянания информации и её обработки, не требующая вмешательста со стороны
Динамическая система ценностей
Эмоциональный модуль

В разработке:
Модуль поиска внутри памяти, не требующий вмешательства пользователя

Для запуска в директории нужен koboldcpp и модель для него (Я использую один из llama3.2 миксов, пойдет любая современная модель)
Далее запускается start.bat и диалог ведётся уже внутри консоли
