## {{ datestr }} 订阅文章
## In today's articles: 
{% for title, articles in articles.items() %}
* {{ articles['articles']|length }} from {{title}}
{%endfor%}

## Article list:

{% set ns=namespace(count=0) %}
{% for title, rss_item in articles.items() %}
    {% for item in rss_item['articles'] %}
### {{ns.count + loop.index }}. [{{ item['title'] }}({{title}})]({{ item['link'] }})
{{ item['desc'] }}
    {% endfor %}
    {% set ns.count = ns.count + rss_item['articles']|length %}
{%endfor%}