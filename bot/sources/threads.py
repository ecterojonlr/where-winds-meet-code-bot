import feedparser


RSS_URL = "https://www.threads.com/@tery0920"


class Threads:

    @staticmethod
    def fetch() -> list[str]:

        feed = feedparser.parse(RSS_URL)

        posts = []

        for entry in feed.entries:
            text = ""

            if "title" in entry:
                text += entry.title + "\n"

            if "summary" in entry:
                text += entry.summary

            posts.append(text)

        return posts
