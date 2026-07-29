import streamlit as st
import json
import zipfile
import os
import tempfile

from downloader import download_from_json


st.set_page_config(
    page_title="Gifs Downloader",
    page_icon="⬇️"
)


st.title("⬇️ Gifs Downloader")

st.write(
    "Upload a JSON file or paste video links."
)

download_type = st.selectbox(
    "Download format:",
    [
        "🎥 Video",
        "🎵 Audio (MP3)"
    ]
)

audio_only = download_type == "🎵 Audio (MP3)"
# -------------------------
# URL validation
# -------------------------

from urllib.parse import urlparse


def is_valid_url(url):

    try:

        result = urlparse(url)

        return (
            result.scheme in ["http", "https"]
            and result.netloc != ""
        )

    except Exception:

        return False



# -------------------------
# Input selection
# -------------------------

input_method = st.radio(
    "Choose input method:",
    [
        "Upload JSON file",
        "Paste links"
    ]
)


data = None
preview_count = 3



# =========================
# JSON Upload
# =========================

if input_method == "Upload JSON file":

    uploaded_file = st.file_uploader(
        "Upload JSON file",
        type="json"
    )


    if uploaded_file:

        try:

            json_data = json.load(uploaded_file)


            if not isinstance(json_data, list):

                st.error(
                    "JSON must contain a list of videos."
                )

            else:

                valid_items = []
                invalid_count = 0


                for item in json_data:

                    try:

                        if (
                            item.get("type") == "video"
                            and is_valid_url(
                                item["urls"]["hd"]
                            )
                        ):

                            valid_items.append(item)

                        else:

                            invalid_count += 1


                    except Exception:

                        invalid_count += 1


                data = valid_items


                st.success(
                    f"Found {len(data)} valid videos"
                )


                if invalid_count:

                    st.warning(
                        f"{invalid_count} invalid items removed."
                    )


        except Exception:

            st.error(
                "Invalid JSON file."
            )



# =========================
# Paste Links
# =========================

else:

    link_text = st.text_area(
        "Paste links separated by commas or new lines:"
    )


    if link_text.strip():

        raw_links = (
            link_text
            .replace(",", "\n")
            .splitlines()
        )


        link_data = []
        invalid_links = []


        for index, link in enumerate(raw_links):

            link = link.strip()


            if not link:

                continue


            if is_valid_url(link):

                link_data.append(
                    {
                        "id": f"video_{index+1}",
                        "type": "video",
                        "url": link,
                        "urls": {
                            "hd": link
                        }
                    }
                )

            else:

                invalid_links.append(link)



        data = link_data


        if data:

            st.success(
                f"Found {len(data)} valid links"
            )


        if invalid_links:

            st.warning(
                f"{len(invalid_links)} invalid links removed."
            )



# =========================
# Preview slider
# =========================

if data:

    if len(data) > 1:

        preview_count = st.slider(
            "Number of previews to show:",
            min_value=1,
            max_value=len(data),
            value=min(3, len(data))
        )

    else:

        preview_count = 1



# =========================
# Download
# =========================

if data:

    if st.button("Start Download"):


        progress_bar = st.progress(0)

        status_text = st.empty()


        file_progress = st.progress(0)

        file_status = st.empty()



        def update_progress(done, total):

            percentage = int(
                done / total * 100
            )

            progress_bar.progress(
                percentage
            )

            status_text.write(
                f"Downloading {done}/{total}"
            )



        def update_file_progress(
            downloaded,
            total,
            filename
        ):

            if total <= 0:

                return


            percentage = int(
                downloaded / total * 100
            )


            file_progress.progress(
                percentage
            )


            file_status.write(
                f"Current file: **{filename}**\n\n"
                f"{percentage}% "
                f"({downloaded / 1024 / 1024:.1f} MB / "
                f"{total / 1024 / 1024:.1f} MB)"
            )



        with tempfile.TemporaryDirectory() as temp_folder:


            with st.spinner("Downloading files..."):


                file_progress.progress(0)

                file_status.write(
                    "Preparing download..."
                )


                files, failed_files = download_from_json(
                    data,
                    temp_folder,
                    progress_callback=update_progress,
                    file_progress_callback=update_file_progress,
                    audio_only=audio_only
                )



                # =========================
                # Create download file
                # =========================

                if len(files) == 1:


                    with open(files[0], "rb") as file:

                        download_data = file.read()


                    download_name = os.path.basename(files[0])

                    if audio_only:
                        download_type = "audio/mpeg"
                    else:
                        download_type = "video/mp4"



                else:


                    zip_path = os.path.join(
                        temp_folder,
                        "downloads.zip"
                    )


                    with zipfile.ZipFile(
                        zip_path,
                        "w"
                    ) as zip_file:


                        for file in files:

                            zip_file.write(
                                file,
                                os.path.basename(file)
                            )



                    with open(zip_path, "rb") as file:

                        download_data = file.read()



                    download_name = "downloads.zip"

                    download_type = "application/zip"



                file_progress.progress(100)

                file_status.write(
                    "Current file: ✅ Complete"
                )



                # =========================
                # Video previews
                # =========================

                if files:


                    st.subheader("Preview")


                    preview_files = files[:preview_count]


                    for i in range(0, len(preview_files), 3):


                        cols = st.columns(3)


                        for j, col in enumerate(cols):


                            index = i + j


                            if index < len(preview_files):


                                with col:

                                    if audio_only:

                                        st.audio(
                                            preview_files[index]
                                        )

                                    else:

                                        st.video(
                                            preview_files[index]
                                        )



        st.success(
            f"Downloaded {len(files)} files!"
        )



        if failed_files:


            st.warning(
                f"{len(failed_files)} files failed."
            )


            with st.expander("See failed files"):


                for item in failed_files:


                    st.write(
                        f"{item['id']}: {item['error']}"
                    )


        else:


            st.success(
                "All files downloaded successfully!"
            )



        st.download_button(
            label="⬇️ Download",
            data=download_data,
            file_name=download_name,
            mime=download_type
        )