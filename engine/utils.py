from PIL import Image
from fpdf import FPDF
from fpdf.enums import XPos, YPos

import requests
from bs4 import BeautifulSoup

import os
import math

# import urllib
# import simplejson

def get_num_paragraphs(video_id):
    # Retrieve text
    summary_file = open("resources/summaries/summary_%s.txt" % video_id, "r")
    summary_text = summary_file.read()
    summary_file.close()

    # Alternative paragraph and text
    num_paragraphs = summary_text.count("\n\n") + 1
    
    if num_paragraphs == 1:
        num_paragraphs = math.ceil((summary_text.count(".") / 3))

    return num_paragraphs

def get_video_id(video_url):
    video_id = ""
    if "&pp=" in video_url: video_id = video_url[video_url.index("watch?v=") + 8:video_url.index("&pp=")]
    else: video_id = video_url[video_url.index("watch?v=") + 8:]
    return video_id

def get_cell_height(text):
    temp = FPDF('P', 'mm')
    temp.set_auto_page_break(auto=True)
    temp.add_page()

    temp.add_font("JetBrains Mono", '', "assets/JetBrainsMono/JetBrainsMonoNerdFont-Light.ttf")
    temp.set_font('JetBrains Mono', '', 8)

    initial_y = temp.y
    temp.multi_cell(85, 8, text)
    final_y = temp.y

    return final_y - initial_y

def create_pdf(video_url) :

    # Define Parameters
    paragraph_length = 3

    # FPDF Setup
    pdf = FPDF('P', 'mm')
    pdf.set_auto_page_break(auto=True)
    pdf.add_page()

    summary_file = open("resources/summaries/summary_%s.txt" % get_video_id(video_url=video_url), "r")
    summary_text = summary_file.read()
    summary_file.close()
    
    num_paragraphs = get_num_paragraphs(get_video_id(video_url))

    pdf.add_font("JetBrains Mono", '', "assets/JetBrainsMono/JetBrainsMonoNerdFont-Light.ttf")

    pdf.set_font("JetBrains Mono", '', 12)

    pdf.multi_cell(0, 10, get_video_title(video_url=video_url), align='C', new_x=XPos.LMARGIN)

    pdf.set_font("JetBrains Mono", '', 7)

    pdf.multi_cell(0, 5, video_url, align='C', new_x = XPos.LMARGIN)

    pdf.set_font('JetBrains Mono', '', 8)

    # Check for Paragraphs
    is_paragraphs = summary_text.count("\n\n") > 0
    print("Paragraph Status: " + str(is_paragraphs))
    # Create Paragraph/Image Format
    image_idx = 0
    iteration = 0
    x_pos, y_pos = pdf.get_x(), pdf.get_y()
    for i in range(num_paragraphs):
        # Retrieve Text
        # Change: add sentence paragraph adoption
        if is_paragraphs:
            try:
                current_text = summary_text[:summary_text.index("\n\n")]
                summary_text = summary_text[summary_text.index("\n\n") + 2:]
            except ValueError:
                current_text = summary_text
        else:
            val = -1
            for i in range(0, paragraph_length):
                temp_val = summary_text.find(".", val + 1)
                if temp_val != -1: val = temp_val
                else: break
            try:
                current_text = summary_text[:val + 1]
                summary_text = summary_text[val + 1:]
            except ValueError:
                current_text = summary_text

         # Check For Space
        text_height = get_cell_height(current_text)
        if text_height + y_pos > 290:
            pdf.add_page()
            y_pos = pdf.get_y()
            if iteration == 1: pdf.multi_cell(100, 0, new_x=XPos.RIGHT)
        # Create Text Cells & Formatting
        y_initial = pdf.y
        pdf.multi_cell(85, 8, current_text, border=0, new_x=XPos.LMARGIN)
        y_final = pdf.y
        # Spacing Cell
        if iteration == 0:
            pdf.multi_cell(100, 8, new_x=XPos.RIGHT)
        else:
            pdf.multi_cell(85, 8, new_x=XPos.LMARGIN)
        # Position Image
        max_height = y_final - y_initial
        # Check For Image
        while not os.path.isfile("resources/photos/%s/%s.jpeg" % (alphanumeric(get_video_id(video_url)), chr(image_idx + 97))):
            image_idx += 1
        # Retrieve Image Width & Height
        image = Image.open("resources/photos/%s/%s.jpeg" % (alphanumeric(get_video_id(video_url)), chr(image_idx + 97)))
        image_width = image.width
        image_height = image.height
        # Use Max Height (Text Cell Height) and Height/Width Ratio To Determine Image Dimensions
        width = 85 if image_height / image_width * 85 <= max_height else image_width / image_height * max_height
        final_img_height = image_height / image_width * width
        # Use width To Determine Left Shift
        shift = (85 - width) / 2
        # Shift Image Up/Down (From Y-Pos) && Left (From XPos.LMARGIN)
        if iteration == 0:
            pdf.image("resources/photos/%s/%s.jpeg" % (alphanumeric(get_video_id(video_url)), chr(image_idx + 97)), 110 + shift, y_pos + (max_height - final_img_height) / 2, width)
        else:
            pdf.image("resources/photos/%s/%s.jpeg" % (alphanumeric(get_video_id(video_url)), chr(image_idx + 97)), 10 + shift, y_pos + (max_height - final_img_height) / 2, width)
        # Update Position From Spacing Cell
        y_pos = pdf.y
        
        # Switch Image/Text Sides For Every Paragraph
        iteration = (iteration + 1) % 2
        # Move to Next Image
        image_idx += 1

    pdf.output("resources/documents/%s.pdf" % get_video_id(video_url=video_url))

def alphanumeric(text):
        ans = [c for c in text if c.isalnum()]
        ans_str = ""
        return ans_str.join(ans)

def get_video_title(video_url):
    r = requests.get(video_url)
    s = BeautifulSoup(r.text, "html.parser")
    content = s.text
    return content[:content.find(" - YouTubeAboutPressCopyrightContact")]