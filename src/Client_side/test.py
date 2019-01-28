#!/usr/bin/python3.6
import re
import sys

def youtube_url_validation(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    match = re.match(youtube_regex, url)

    if match:
        print("URL!")
        return match.group()
    else:
        print("No es url")
        return "HOLA"

    

print(youtube_url_validation(sys.argv[1]))
