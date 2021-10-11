import requests
import logging
import http.client
import urllib

from pages.all_videos_page import AllVideoPage
from parsers.videos import DF_LINK

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO,
                    filename='logs.txt')

logger = logging.getLogger('scraping')


def load_page_content(website):
    logger.info("Loading website" + website)
    return requests.get(website).content


def get_page_object():
    logger.debug('Creating AllVideoPage from page content.')
    return AllVideoPage(load_page_content(DF_LINK))


def filewriter(filename, filetowrite):
    with open(filename, "w", newline="") as file:
        for each in filetowrite:
            logger.info(f'Writing line to text file: "{each} ')
            file.write(str(each) + "\n")


def filereader(filename):
    old_videos = []
    with open(filename, "r") as file:
        for each in file:
            logger.info(f'Reading line to text file: "{each} ')
            old_videos.append(each.strip("\n"))
    return old_videos


def stringsplit(inputstring):
    logger.debug(f'Splitting String: "{inputstring.split("%")} ')
    return inputstring.split("%")

def newvideolist():
    current_videos = get_page_object().videos
    current_videos = [str(e) for e in current_videos]
    old_videos = filereader("videos.txt")
    new_videos = set(current_videos).difference(set(old_videos))
    return list(new_videos)


def pushover(title, link):
    pushover_tokens = []

    with open("pushover_auth.txt", "r") as file:
        for token in file:
            pushover_tokens.append(token.strip("\n"))

    token = pushover_tokens[0].split(" ")
    user = pushover_tokens[1].split(" ")

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                     "token": token[1],
                     "user": user[1],
                     "message": title,
                     "url": link,
                 }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()
    logger.debug("Sent pushover response successfully ")


#filewriter("videos.txt", get_page_object().videos)

if __name__ == '__main__':
    logger.debug("Running __main__")
    for each in newvideolist():
        logger.debug("There was a new video passed to pushover1")
        string_split = stringsplit(each)
        pushover(string_split[0], string_split[1])
    filewriter("videos.txt", get_page_object().videos)
