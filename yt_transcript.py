import os.path
from bs4 import BeautifulSoup
from urllib.request import urlopen
from yt_channel_scraper import YoutubeScraper

def get_transcript(video_url):

    if "&pp=" in video_url: video_id = video_url[video_url.index("watch?v=") + 8:video_url.index("&pp=")]
    else: video_id = video_url[video_url.index("watch?v=") + 8:]

    file_name = "transcripts/transcript_%s.txt" % video_id
    if os.path.isfile(file_name):
        file = open(file_name, "r")
        video_transcript = file.read()
        file.close()
        return video_transcript

    page = urlopen(video_url)
    soup = BeautifulSoup(page.read().decode("utf8"), features="lxml")
    link_divs = soup.find_all("link")
    channel_link = ""
    
    for div in link_divs:
        try: 
            link = div['href']
            if "http://www.youtube.com/@" in link: channel_link = link; break;
        except Exception: continue

    fy = YoutubeScraper(channel_link)
    video_transcript = fy.get_video_transcript(video_id=video_id)

    file = open(file_name, "w")
    file.write(video_transcript)
    file.close()