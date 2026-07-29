import os
import yt_dlp
import shutil

def ensure_deno():

    if shutil.which("deno"):
        return

    subprocess.run(
        [
            "bash",
            "-c",
            "curl -fsSL https://deno.land/install.sh | sh"
        ],
        check=True
    )

    os.environ["PATH"] += ":" + os.path.expanduser(
        "~/.deno/bin"
    )


ensure_deno()

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

        "format": "bv*+ba/best",

        "merge_output_format": "mp4",

        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }
        ],

        "noplaylist": True,

        "js_runtimes": {
            "deno": {}
        },

        "extractor_args": {
            "youtube": {
                "player_client": [
                    "android"
                ]
            }
        },

        "progress_hooks": [
            progress_hook
        ]
    }


    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filepath = ydl.prepare_filename(info)


    return filepath