### ENG
## Telegram Game Sales Bot

This repository contains the code for Telegram Game Sales Bot, a bot developed for selling games. The bot provides a convenient and easy way for Telegram users to purchase various games at competitive prices, right from within the messenger.

### Setup

1. Open the `admin_bot/settings/config.py` file and insert your Telegram Bot API token and Telegram payment system token.
2. In the `whitelist.py` file located at the top level, manually add the user IDs of the sellers.
3. Install the required dependencies by running the command: `pip install -r requirements.txt`.

### Functionality

The bot has two key branches of operation: the seller and the buyer.

#### Seller
- Sellers are added to the whitelist and gain access to create "game cards." Each game card includes the game title, description, genre, price, and photos.
- Sellers can delete entire game cards or selectively edit their elements. For example, they can modify the price of a specific game card without affecting the rest.

#### Buyer
- When a buyer triggers the `/buy` command, they receive inline buttons with genres created by the sellers.
- Upon selecting a genre, the buyer receives a catalog of games assigned to that genre. The catalog can be navigated using inline buttons.
- Clicking on a game's button displays its card with detailed information and a button to initiate the payment process.
- The payment provider can be chosen by modifying the `PROVIDER_TOKEN` variable in the code.

### Tech Stack

The main technology stack used for this project includes:
- Python 3.10.6: Programming language for bot development.
- sqlite3: Database system for storing game and user information.
- aiogram: Python framework for building Telegram bots.

**Note:** Make sure you have the necessary version of Python installed along with the required dependencies mentioned in the `requirements.txt` file.

### Contributions

Contributions to this project are welcome! If you would like to contribute, please refer to the `CONTRIBUTING.md` file for guidelines on how to get started.

Feel free to explore the code, make improvements, and share your suggestions with the community.

Enjoy using the Telegram Game Sales Bot!

### RUS
## Telegram Game Sales Bot

Этот репозиторий содержит код для Telegram Game Sales Bot - бота, разработанного для продажи игр. Бот предоставляет удобный и простой способ для пользователей Telegram приобрести различные игры по выгодным ценам, прямо из мессенджера.

### Настройка

1. Откройте файл `admin_bot/settings/config.py` и вставьте токен Telegram Bot API и токен платежной системы Telegram.
2. В файле `whitelist.py`, расположенном на верхнем уровне, вручную добавьте идентификаторы пользователей-продавцов.
3. Установите необходимые зависимости, выполнив команду: `pip install -r requirements.txt`.

### Функциональность

Бот имеет две ключевые ветви работы: продавец и покупатель.

#### Продавец
- Продавцы добавляются в белый список и получают возможность создавать "карточки игр". Каждая карточка содержит название игры, описание, жанр, цену и фотографии.
- Продавцы могут удалить целиком карточку игры или выборочно отредактировать ее элементы. Например, изменить цену отдельной карточки игры, не затрагивая остальные.

#### Покупатель
- При использовании команды `/buy`, покупатель получает встроенные кнопки с жанрами, созданными продавцами.
- После выбора жанра, покупатель получает каталог игр, относящихся к этому жанру. Каталог можно просматривать с помощью встроенных кнопок.
- При нажатии на кнопку с названием игры отображается ее карточка с подробной информацией и кнопкой для начала процесса оплаты.
- Выбор платежного провайдера осуществляется путем изменения переменной `PROVIDER_TOKEN` в коде.

### Технологический стек

Основной технологический стек, используемый для данного проекта, включает:
- Python 3.10.6: Язык программирования для разработки бота.
- sqlite3: Система баз данных для хранения информации об играх и пользователях.
- aiogram: Python-фреймворк для создания Telegram-ботов.

**Примечание:** Убедитесь, что у вас установлена необходимая версия Python, а также все зависимости, указанны
