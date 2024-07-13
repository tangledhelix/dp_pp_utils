## {{ title }} by {{ author }} ({{ pg_ebook_number }})

This is an [errata report][1] for a [Project Gutenberg][2] EBook.

[1]: https://www.gutenberg.org/help/errata.html
[2]: https://www.gutenberg.org

"{{ title }}" by {{ author }}

- [Project Gutenberg listing][3]
{% if project_id -%}
- [DP project page][4]
{%- endif %}

[3]: https://www.gutenberg.org/ebooks/{{ pg_ebook_number }}
{% if project_id -%}
[4]: https://www.pgdp.net/c/project.php?id=projectID{{ project_id }}
{%- endif %}

Assigned ID `[errata #xxxxx]`

### Corrections

```
{{ title }}, by {{ author }}
    MONTH, YEAR  [EBook #{{ pg_ebook_number }}]


```
