# Changelog

Все заметные изменения проекта описываются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версии нумеруются по [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

## [1.0.0] - 2026-10-15

### Added

- Игра «Морской бой» для двух игроков по локальной сети.
- Окно выбора роли: «Сервер» или «Клиент».
- Автопоиск сервера через UDP broadcast на порту 5051.
- Ручной ввод IP-адреса, если автопоиск не сработал.
- Игра по одному TCP-соединению на порту 5050 с текстовым протоколом.
- Случайная расстановка кораблей и кнопка «Расставить заново» до первого выстрела.
- Индикатор состояния соединения и сообщение «Соперник отключился».
- Тёмная тема на customtkinter.
- Модульные тесты для игровой логики.
- Сборка `SeaBattle.exe` через PyInstaller и GitHub Actions.

### Removed

- Старая версия проекта: смена картинки по кнопке (`server.py`, `client.py`, папка `pictures`).

[Unreleased]: https://github.com/kkaraumi/kisik/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/kkaraumi/kisik/releases/tag/v1.0.0
