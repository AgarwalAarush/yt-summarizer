from engine.yt_summarizer import YoutubeSummarizer

if __name__ == '__main__':
    file = open("requests.txt", "r")
    lines = file.readlines()
    for line in lines:
        if (line.count("@") > 0): continue  
        yts = YoutubeSummarizer()
        yts.create_document(line)