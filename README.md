# Лабораторія робототехніки

Статичний сайт із 12 інтерактивними уроками для 5–7 класів. Відкрийте index.html у браузері.

## Структура

- index.html — головна сторінка з вибором класу.
- assets/site.css — спільні стилі каталогу.
- 5 клас/index.html, 6 клас/index.html, 7 клас/index.html — каталоги.
- <клас>/Робототехніка/<урок>/ — HTML та опис.
- .github/workflows/pages.yml — публікація GitHub Pages.
- build-navigation.ps1 — оновлення каталогів і навігації.

Приклади та робочі архіви залишаються локально й виключені з Git. Посилання відносні та працюють у підпапці GitHub Pages.

## GitHub Pages

1. Створіть порожній репозиторій GitHub, наприклад robotics-lessons.
2. Виконайте команди, замінивши YOUR-USERNAME:

    git add .
    git commit -m "Create robotics lessons website"
    git remote add origin https://github.com/YOUR-USERNAME/robotics-lessons.git
    git push -u origin main

3. У Settings → Pages → Build and deployment → Source оберіть GitHub Actions.
4. Якщо перший запуск не вдався до налаштування Pages, запустіть Deploy lessons to GitHub Pages у вкладці Actions.

Адреса сайту з’явиться в результаті workflow.

## Додавання уроків

Зберігайте уроки за схемою <номер> клас/Робототехніка/Урок NN — Тема/Урок NN — Тема.html.
Додайте meta description. Презентації зберігайте лише в оригінальних папках поза site/; вони не публікуються.
Запустіть ./build-navigation.ps1 у PowerShell та закомітьте зміни.
Скрипт оновлює каталоги класів 5–7 і навігацію, зберігаючи вміст уроків.
