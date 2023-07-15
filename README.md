# Youtube Summarizer
**Youtube Summarizer is an easy way to quickly absorb information from youtube videos**
The application can create pdf summaries of youtube videos for you fit with images to aid in understanding. Use it to quickly review information prior to tests, meetings, and more!
## Usage Instructions
### Step 1
```pip install -r requirements.txt```
### Step 2
Navigate into engine -> yt_summarizer.py and then place Open AI API Key in the designated variable on line 18 (inside of double quotation marks)
### Step 3
Edit requirements.txt
- Video URLs should be placed on separate lines
- Video URLs with the @ symbol in front of them will **not** be processed
### Step 4
```python main.py```
### Step 5
Generated PDFs will be created in resources/documents under the designated youtube video id visible in the Video URL
## Example
<img width="1182" alt="Screen Shot 2023-07-10 at 11 27 03 PM" src="https://github.com/AgarwalAarush/yt-summarizer/blob/main/assets/Screenshot%202023-07-14%20at%205.02.28%20PM.png">