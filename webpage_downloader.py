import os
import yt_dlp


def download_webpage_video(
    url,
    folder,
    progress_callback=None
):

    os.makedirs(folder, exist_ok=True)


    def progress_hook(data):

        if (
            progress_callback
            and data["status"] == "downloading"
        ):

            downloaded = data.get(
                "downloaded_bytes",
                0
            )

            total = (
                data.get("total_bytes")
                or data.get("total_bytes_estimate")
                or 0
            )

            filename = os.path.basename(
                data.get(
                    "filename",
                    "video"
                )
            )

            if total > 0:

                progress_callback(
                    downloaded,
                    total,
                    filename
                )


    options = {
        "outtmpl": os.path.join(
            folder,
            "%(title)s.%(ext)s"
        ),
        "format": "best",
        "noplaylist": True,
        "progress_hooks": [
            progress_hook
        ]
    }


    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filepath = ydl.prepare_filename(
            info
        )


    return filepath