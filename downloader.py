import requests
import os
import time

from webpage_downloader import download_webpage_video


def download_file(
    url,
    filename,
    folder,
    progress_callback=None,
    retries=3
):

    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(
        folder,
        filename
    )

    last_error = None


    for attempt in range(1, retries + 1):

        try:

            response = requests.get(
                url,
                stream=True,
                timeout=60
            )

            response.raise_for_status()

            total_size = int(
                response.headers.get(
                    "content-length",
                    0
                )
            )

            downloaded = 0

            with open(filepath, "wb") as file:

                for chunk in response.iter_content(
                    chunk_size=1024 * 64
                ):

                    if not chunk:
                        continue

                    file.write(chunk)

                    downloaded += len(chunk)

                    if (
                        progress_callback
                        and total_size > 0
                    ):

                        progress_callback(
                            downloaded,
                            total_size,
                            filename
                        )


            return filepath


        except requests.exceptions.Timeout:

            last_error = "Download timed out"


        except requests.exceptions.ConnectionError:

            last_error = "Connection error"


        except requests.exceptions.HTTPError as e:

            last_error = (
                f"Server error: {e.response.status_code}"
            )


        except Exception as e:

            last_error = str(e)


        if attempt < retries:

            time.sleep(2)


    raise Exception(
        f"{last_error} after {retries} attempts"
    )



def download_from_json(
    data,
    folder,
    progress_callback=None,
    file_progress_callback=None
):

    downloaded_files = []

    failed_files = []

    total = len(data)

    completed = 0


    for item in data:

        try:

            if item.get("type") != "video":

                continue


            video_id = item.get(
                "id",
                f"video_{completed+1}"
            )


            url = item.get("url") or item["urls"]["hd"]


            if (
                ".mp4" in url.lower()
                or ".webm" in url.lower()
            ):

                filename = video_id + ".mp4"

                filepath = download_file(
                    url,
                    filename,
                    folder,
                    progress_callback=file_progress_callback
                )

            else:

                filepath = download_webpage_video(
                    url,
                    folder
                )


            downloaded_files.append(
                filepath
            )


        except Exception as e:

            failed_files.append(
                {
                    "id": item.get(
                        "id",
                        "unknown"
                    ),
                    "error": str(e)
                }
            )


        completed += 1


        if progress_callback:

            progress_callback(
                completed,
                total
            )


    return downloaded_files, failed_files