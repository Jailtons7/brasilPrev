build:
	docker-compose build --no-cache --parallel

makemigrations:
	docker-compose run --rm web python manage.py makemigrations

migrate:
	docker-compose run --rm web python manage.py migrate

collectstatic:
	docker-compose run --rm web python manage.py collectstatic --noinput

createsuperuser:
	docker-compose run --rm web python manage.py createsuperuser

runserver:
	docker-compose run --rm --service-port web python manage.py runserver 0.0.0.0:8002 --insecure

generateschema:
	docker-compose run --rm web python manage.py spectacular --color --file schema.yml

tests:
	docker-compose run --rm web python manage.py test

up:
	docker-compose up
