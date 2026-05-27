.PHONY: help up up-build down logs ps psql seed restart clean

help:
	@echo "Dostepne komendy:"
	@echo "  make up         - uruchom serwisy w tle"
	@echo "  make up-build   - przebuduj i uruchom serwisy"
	@echo "  make down       - zatrzymaj serwisy"
	@echo "  make logs       - logi (follow)"
	@echo "  make ps         - status kontenerow"
	@echo "  make psql       - wejscie do psql"
	@echo "  make seed       - zaladuj dane testowe (admin + 5 salek)"
	@echo "  make restart    - restart serwisow"
	@echo "  make clean      - down + usun wolumeny (kasuje dane)"

up:
	docker compose up -d

up-build:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

psql:
	docker compose exec db sh -c 'psql -U $$POSTGRES_USER -d $$POSTGRES_DB'

seed:
	docker compose exec backend python -m app.seed

restart:
	docker compose restart

clean:
	docker compose down -v
