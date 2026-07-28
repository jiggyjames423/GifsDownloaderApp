from downloader import download_file
from webpage_downloader import download_webpage_video


def download_url(url, folder, filename=None):

    if (
        ".mp4" in url.lower()
        or ".webm" in url.lower()
    ):

        if filename is None:
            filename = url.split("/")[-1]

        return download_file(
            url,
            filename,
            folder
        )

    else:

        return download_webpage_video(
            url,
            folder
        )