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


st.title("⬇️ Gifs Downloader work?")

st.write(
    "Upload a JSON file or paste video links."
)


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


    if st.button("Enter Links"):

        if link_text.strip():

            raw_links = (
                link_text
                .replace(",", "\n")
                .splitlines()
            )


            links = []
            invalid_links = []


            for link in raw_links:

                link = link.strip()


                if not link:
                    continue


                if is_valid_url(link):

                    links.append(link)

                else:

                    invalid_links.append(link)



            link_data = []


            for index, link in enumerate(links):

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


            st.session_state["link_data"] = link_data


            st.success(
                f"Found {len(link_data)} valid links"
            )


            if invalid_links:

                st.warning(
                    f"{len(invalid_links)} invalid links removed."
                )


        else:

            st.warning(
                "Please enter at least one link."
            )


    if "link_data" in st.session_state:

        data = st.session_state["link_data"]



# =========================
# Download
# =========================

if data:

    if st.button("Start Download"):

        progress_bar = st.progress(0)

        status_text = st.empty()


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


        with tempfile.TemporaryDirectory() as temp_folder:

            with st.spinner("Downloading files..."):

                files, failed_files = download_from_json(
                    data,
                    temp_folder,
                    update_progress
                )


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

                    zip_data = file.read()



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
            label="⬇️ Download ZIP",
            data=zip_data,
            file_name="downloads.zip",
            mime="application/zip"
        )