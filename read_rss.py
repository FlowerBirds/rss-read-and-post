import yaml
import os
import feedparser
import html2text as ht
import hashlib
from jinja2 import Environment
from jinja2 import FileSystemLoader
import datetime
import pytz
from github import Github


def read_config():
    with open("subscribe_list.yaml", encoding="UTF-8") as fs:
        datas = yaml.load(fs, Loader=yaml.FullLoader)
        rss_list = datas['rss']
    return rss_list


def read_feed(item):
    url = item['url']
    print("read feed: " + str(item['name']) + " from " + url)
    feed_list = list()
    try:
        feed = feedparser.parse(url)
        title = feed.feed.title
        text_maker = ht.HTML2Text()
        text_maker.bypass_tables = False
        md5 = hashlib.md5()
        for entry in feed.entries:
            e_title = entry.title
            e_desc = entry.description
            e_link = entry.link

            text = text_maker.handle(e_desc)
            e_desc = text.split('#')[0].replace("\n", " ")
            article = dict()
            article['title'] = e_title
            article['link'] = e_link
            article['desc'] = e_desc
            article['md5'] = hashlib.md5(e_link.encode(encoding='UTF-8')).hexdigest()
            feed_list.append(article)
        return title, feed_list
    except:
        print("error with url: " + url)
    return item['name'], list()


def read_history():
    history = dict()
    if not os.path.exists("history.log"):
        record_history(list())
    with open("history.log", encoding="UTF-8", mode='r') as fs:
        for line in fs.readlines():
            line = line.strip()
            history[line] = 0
    return history


def build_markdown(articles, datestr):

    env = Environment(loader=FileSystemLoader('./templates', 'utf-8'))
    template = env.get_template('report.md')
    report = template.render(datestr=datestr, name="python", articles=articles)
    return report

def record_history(md5s):
    with open("history.log", "a") as fs:
        fs.writelines(map(lambda x: x + "\n", md5s))
        pass

def read_and_record():
    history = read_history()
    items = read_config()
    all_articles = dict()
    all_md5s = list()
    for item in items:
        title, articles = read_feed(item)
        updates = list(filter(lambda x: x['md5'] not in history, articles))
        md5s = list(map(lambda x: x['md5'], updates))
        all_md5s = all_md5s + md5s
        all_articles[title] = {"articles": updates, "item": item}
    datestr = datetime.datetime.now(pytz.timezone('PRC')).strftime("%Y-%m-%d")
    return build_markdown(all_articles, datestr), all_md5s, datestr


if __name__ == '__main__':
    report, md5s, datestr = read_and_record()
    if len(md5s) > 0:
        # or using an access token
        token = os.getenv("GITHUB_TOKEN")
        if token is None:
            raise EnvironmentError("token not find")
        g = Github(token)
        repo = g.get_repo("FlowerBirds/flowerbirds.github.io")
        repo.create_issue(title="Bolg report on " + datestr + ": " + str(len(md5s)) + " articles", body=report)
        record_history(md5s)
    pass
