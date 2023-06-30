import openai
import yt_transcript

prompt_file = open("prompt.txt", "r")


response = openai.Completion.create(
    model="text-davinci-003",
    
)

if __name__ == '__main__':
    file = open("requests.txt", "r")
    transcript_requests = file.readlines();

    for request in transcript_requests:
        yt_transcript.get_transcript(video_url=request.strip())
    
