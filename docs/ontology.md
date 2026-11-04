# Легковагова онтологія StudyFlow

## Типи сутностей

| Тип | Папка vault | Приклад |
|---|---|---|
| concept | Concepts | Навчальна задача |
| component | Components | CLI |
| decision | Decisions | Локальне зберігання |
| glossary | Glossary | MCP-конектор |
| moc | корінь | MOC StudyFlow |

## Типізовані зв'язки

- `depends_on`: компонент потребує іншого компонента.
- `implements`: компонент реалізує поняття або вимогу.
- `belongs_to`: задача належить дисципліні.
- `has_status`: задача має статус.
- `supersedes`: нове рішення замінює попереднє.

У frontmatter записуємо, наприклад, `depends_on: ["SQLite-сховище"]`; у тексті дублюємо читабельним реченням `[[CLI]] depends_on [[SQLite-сховище]]`. Так є і тип зв'язку, і wiki-посилання для Obsidian.
