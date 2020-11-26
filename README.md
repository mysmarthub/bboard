Доска объявлений
===
Python/Django

Use
---

`pip install -r requirements.txt`

`python manage.py makemigrations`

`python manage.py migrate`

`python manage.py createsuperuser`

`python manage.py loaddata fixtures/rubric.main.json --app main.models`

`python manage.py dumpdata --format=json main > fixtures/main.json`

API test
---
`http://localhost:8000/api/bbs/`

