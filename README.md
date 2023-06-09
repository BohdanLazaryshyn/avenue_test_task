# Test task Dev
## Simple Django REST API with CRUD operations and two Telegram bots for creating and managing notes and tasks.

Preparation for project launch
```
- Write in Git Bash
git clone https://github.com/BohdanLazaryshyn/test_task_GIS
- Open the project in your interpreter
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

# Environment variables
create .env file in root directory with following variables
```
TASK_BOT_TOKEN=TASK_BOT_TOKEN
NOTEBOOK_BOT_TOKEN=NOTEBOOK_BOT_TOKEN
```


