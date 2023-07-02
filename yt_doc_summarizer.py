import os
import openai
import yt_transcript
from UnlimitedGPT import ChatGPT

openai.api_key = "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"

def summarize_transcript(video_url):

    yt_transcript.get_transcript(video_url=video_url)

    video_id = ""
    if "&pp=" in video_url: video_id = video_url[video_url.index("watch?v=") + 8:video_url.index("&pp=")]
    else: video_id = video_url[video_url.index("watch?v=") + 8:]

    transcript_file_url = "transcripts/transcript_%s.txt" % video_id
    transcript_file = open(transcript_file_url, "r")
    transcript = transcript_file.read();
    transcript_file.close();

    prompt_file = open("prompt.txt", "r")
    prompt = prompt_file.read()
    prompt_file.close()

    complete_prompt = prompt + "\n\n%s" % transcript

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Assistant is a large language model trained by OpenAI to summarize text in a human-like manner with the purpose of teaching."},
            {"role": "user", "content": complete_prompt}
        ],
        frequency_penalty= 0.2
    )

    write_file_name = open("summaries/summary_%s.txt" % video_id, "w")
    write_file_name.write(response['choices'][0]['message']['content'])
    write_file_name.close()

    print(complete_prompt + "\n")
    print(response)

if __name__ == '__main__':
    file = open("requests.txt", "r")
    transcript_requests = file.readlines();

    for request in transcript_requests:
        summarize_transcript(video_url=request.strip())
    
    file.close();