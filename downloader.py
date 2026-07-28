import requests
import os
import time


def download_file(
    url,
    filename,
    folder,
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
                timeout=60
            )

            response.raise_for_status()


            with open(filepath, "wb") as file:

                file.write(
                    response.content
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
    progress_callback=None
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


            url = item["urls"]["hd"]


            filename = (
                video_id + ".mp4"
            )


            filepath = download_file(
                url,
                filename,
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