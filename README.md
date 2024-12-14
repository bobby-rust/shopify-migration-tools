# Shopify Migration Tools

## Getting Started

Ensure you have python3 installed on your system. https://www.python.org/downloads/
You can check if you have python3 installed by running `python3 --version` in your
shell.

### Create a virtual environment

`python3 -m venv <your_venv_name>`

### Activate the virtual environment

`source <your_venv_name>/bin/activate`

### Install the dependencies

`pip install -r requirements.txt`

### Create your environment variables

-   image_uploader requires [TODO]
-   blog_uploader requires SHOP_URL, API_ACCESS_TOKEN, SHOPIFY_CDN_BASE_URL, and CSV_FILE_PATH
    -   CSV_FILE_PATH is the path to your csv file exported with the WP_all_export tool
    -   You will need to export the following fields: [TODO]
-   get_product_count requires SHOP_URL and API_ACCESS_TOKEN
-   dl_images_from_wp_export_xml requires WP_MEDIA_XML_EXPORT, which is the filename of your exported xml

### Run the script

`python3 <tool>.py`

## Disclaimer

_These tools are not production ready_. In its current state, this is not code I
developed for other people to use, rather simply to achieve a goal as fast as
possible. This is not code to be proud of. If you need help, reach out and I
will assist you as best I can.
