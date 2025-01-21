## Как запустить на своём устройстве
Для запуска необходимо клонировать себе данный репозиторий

#### Далее ввести в терминале следующие команды поочерёдно
* pip install -r requirements.txt
* cd service_center
* python manage.py runserver

После переходим по адресу http://127.0.0.1:8000/

#### Должна открыться страница home:
![image](https://github.com/user-attachments/assets/1f2c49c9-73b2-4454-92a3-bcc683c66bac)

## Суперпользователь
По умолчанию логин для суперпользователя - eachi, пароль - 23232321a

## Тесты
Для запуска тестов необходимо ввести следующую команду:
* python manage.py test service_center_app.tests
