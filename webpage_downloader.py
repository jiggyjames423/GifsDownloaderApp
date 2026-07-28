import os
import yt_dlp


def download_webpage_video(url, folder):

    os.makedirs(folder, exist_ok=True)

    options = {
        "outtmpl": os.path.join(
            folder,
            "%(title)s.%(ext)s"
        ),
        "format": "best",
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filepath = ydl.prepare_filename(info)

    return filepath