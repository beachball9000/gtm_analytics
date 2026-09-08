{% macro is_period_complete(date_column) %}
    ({{ date_column }} <= '{{ var("as_of_date") }}'::date)
{% endmacro %}