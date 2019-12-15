import requests


def fetch_thumbnail(wistia_id, width=640, height=360):
    """ TODO: Put this in an S3 bucket before returning the URL. """
    url = "http://fast.wistia.net/oembed?url=http://home.wistia.com/medias/{}?embedType=async&videoWidth=640".format(
        wistia_id
    )
    data = requests.get(url).json()
    return data["thumbnail_url"].split("?")[0] + "?image_crop_resized={}x{}".format(
        width, height
    )
