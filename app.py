#Prerequisites & Authentication
from requests_oauthlib import OAuth1

CONSUMER_KEY    = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"

# Two-legged OAuth: resource_owner_key and resource_owner_secret are empty strings
auth = OAuth1(
    client_key=CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key="",
    resource_owner_secret="",
    signature_method="PLAINTEXT",
)
API_BASE = "https://api.schoology.com/v1"

#Acquire an upload endpoint
import os, hashlib, json
import requests

def initiate_upload(filepath):
    # Compute filesize & MD5
    filesize = os.path.getsize(filepath)
    md5 = hashlib.md5(open(filepath, "rb").read()).hexdigest()

    url = f"{API_BASE}/upload"
    body = {
        "filename": os.path.basename(filepath),
        "filesize": filesize,
        "md5_checksum": md5,
    }

    resp = requests.post(url, json=body, auth=auth)
    resp.raise_for_status()

    # Response XML → you can use an XML parser; here we'll do a quick hack:
    from xml.etree import ElementTree as ET
    root = ET.fromstring(resp.text)
    return {
        "upload_url": root.findtext("upload_location"),
        "file_id":      root.findtext("id"),
    }

# Example:
upload_info = initiate_upload("path/to/Myfile.jpg")
print(upload_info)


#Step 2 – PUT the file contents
def upload_bytes(filepath, upload_url):
    mime = "application/octet-stream"
    # or detect via Python's mimetypes module
    import mimetypes
    mime = mimetypes.guess_type(filepath)[0] or mime

    with open(filepath, "rb") as f:
        resp = requests.put(
            upload_url,
            data=f,
            headers={"Content-Type": mime},
            auth=auth,
        )
    resp.raise_for_status()
    # You’ll get back a full FILE object in XML
    return resp.text

# Example:
result_xml = upload_bytes("path/to/Myfile.jpg", upload_info["upload_url"])
print(result_xml)

