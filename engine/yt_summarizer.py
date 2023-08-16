from bs4 import BeautifulSoup
from urllib.request import urlopen
from yt_channel_scraper import YoutubeScraper

import os
import openai
import engine.utils as utils

import concurrent.futures
from engine.images_engine.patch import webdriver_executable
from engine.images_engine.GoogleImageScraper import GoogleImageScraper

from reportlab.pdfgen import canvas

class YoutubeSummarizer():
    def __init__(self):

        settings_file = open("settings.txt", "r")
        api_text = settings_file.read();
        settings_file.close()

        api_key = ""
        if  api_text.count("\n") > 0:
            api_key = api_text[api_text.find("sk"):api_text.find("\n")]
        else:
            api_key = api_text[api_text.find("sk"):]

        # Set OpenAI Key
        openai.api_key = api_key

        #Define file path
        self.webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'resources/webdriver', webdriver_executable()))
        self.image_path = os.path.normpath(os.path.join(os.getcwd(), 'resources/photos'))

        #Parameters
        self.number_of_images = 5                # Desired number of images
        self.headless = True                     # True = No Chrome GUI
        self.min_resolution = (0, 0)             # Minimum desired image resolution
        self.max_resolution = (9999, 9999)       # Maximum desired image resolution
        self.max_missed = 10                     # Max number of failed images before exit
        self.number_of_workers = 1               # Number of "workers" used
        self.keep_filenames = False              # Keep original URL image filenames

    def get_transcript(self, video_url):

        video_id = utils.get_video_id(video_url=video_url)

        file_name = "resources/transcripts/transcript_%s.txt" % video_id
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

    def summarize_transcript(self, video_url):

        video_id = utils.get_video_id(video_url=video_url)

        file_name = "resources/summaries/summary_%s.txt" % video_id
        if os.path.isfile(file_name):
            file = open(file_name, "r")
            video_transcript = file.read()
            file.close()
            return video_transcript

        transcript_file_url = "resources/transcripts/transcript_%s.txt" % video_id
        transcript_file = open(transcript_file_url, "r")
        transcript = transcript_file.read();
        transcript_file.close();

        prompt_file = open("resources/prompt.txt", "r")
        prompt = prompt_file.read()
        prompt_file.close()

        complete_prompt = prompt + "\n\n%s" % transcript

        print("Retrieving OpenAI API Response")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "Assistant is a large language model trained by OpenAI to summarize text in a human-like manner with the purpose of teaching."},
                {"role": "user", "content": complete_prompt}
            ],
            frequency_penalty=0.2
        )

        print("OpenAI API Response Recieved")

        write_file_name = open("resources/summaries/summary_%s.txt" % video_id, "w")
        write_file_name.write(response['choices'][0]['message']['content'])
        write_file_name.close()

    def worker_thread(self, search_key):
        image_scraper = GoogleImageScraper(
            self.webdriver_path,
            self.image_path,
            self.video_id,
            search_key,
            self.number_of_images,
            self.headless,
            self.min_resolution,
            self.max_resolution,
            self.max_missed)
        image_urls = image_scraper.find_image_urls()
        image_scraper.save_images(image_urls, self.keep_filenames)

        #Release resources
        del image_scraper

    def get_images(self, key):
        # Add to search key set
        search_keys=[]
        search_keys.append(self.key_conversion(key))

        # Update Number of Images
        self.number_of_images = utils.get_num_paragraphs(self.video_id) * 2

        #Run each search_key in a separate thread
        #Automatically waits for all threads to finish
        #Removes duplicate strings from search_keys
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.number_of_workers) as executor:
            executor.map(self.worker_thread, search_keys)

    def create_document(self, video_url):
        self.video_id = utils.get_video_id(video_url)
        self.get_transcript(video_url=video_url)
        self.summarize_transcript(video_url=video_url)
        video_id = utils.get_video_id(video_url=video_url)
        summary_file = open("resources/summaries/summary_%s.txt" % video_id, "r")
        summary = summary_file.read()
        topic = summary[:summary.index('.')]
        summary_file.close()
        self.get_images(topic)
        utils.create_pdf(video_url)

    # def create_pdf(self, video_id):
    #     summary_directory = "resources/summaries/"
    #     summary_file = ''.join([summary_directory, video_id])
    #     photos_directory = "resources/photos/%s/" % (self.alphanumeric(video_id))
    #     for filename in os.listdir(photos_directory):
    #         f = os.path.join(photos_directory, filename)
    #         if os.path.isfile(f): print(f)

    def key_conversion(self, key):
        print("Converting Key")
        key = key.replace(' ', '-')
        return key

    def alphanumeric(self, text):
        ans = [c for c in text if c.isalnum()]
        ans_str = ""
        return ans_str.join(ans)