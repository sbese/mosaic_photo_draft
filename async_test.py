import flickrapi
from PIL import Image
import os
# from mosaic.models import Pic
from io import BytesIO
import aiohttp
import asyncio
from psycopg2 import connect

con = connect(database="mosaic", user="postgres", password="zaq!23", host="127.0.0.1")
cur = con.cursor()
api_key = '5f0a0c4e04298e2e84ef379f8de4a7fe'
api_secret = 'df521e620606493c'
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

flickr = flickrapi.FlickrAPI(api_key, api_secret)
try:
    os.mkdir('flickr_photo')
except OSError:
    pass


def to_db(data, url):
    try:
        image = Image.open(BytesIO(data))
        w, h = image.size
        rr, gg, bb = 0, 0, 0
        for x in range(w):
            for y in range(h):
                r, g, b = image.getpixel((x, y))
                rr += r
                gg += g
                bb += b

        cnt = w * h
        print(rr//cnt, gg//cnt, bb//cnt)
    except Exception as e:
        print(e)
        return
    try:
        cur.execute(f"select url from mosaic_pic where url = '{url}'")
        fet=cur.fetchone()
        if fet is not None:
            print(fet)
            return
        else:
            cur.execute(f"insert into mosaic_pic (url, r, g, b) values ('{url}', {rr//cnt}, {gg//cnt}, {bb//cnt})")
    except Exception as e:
        print(e)
    finally:
        con.commit()



async def fetch_content(url, session):
    async with session.get(url) as response:
        data = await response.read()
        to_db(data, url)


async def main(urls):
    tasks = []

    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(fetch_content(url, session))
            tasks.append(task)
        await asyncio.gather(*tasks)


key = 'girl'
photos = flickr.photos.search(
    page=1,
    tags=key,
    content_type=1,
    sort='relevance',
    license='9,10',
    format='parsed-json')

urls = []
print()
for page in range(15,photos['photos']['pages']+1):
    photos_page = flickr.photos.search(
    page=page,
    tags=key,
    content_type=1,
    sort='relevance',
    license='9,10',
    format='parsed-json')
    # for i, photo in enumerate(photos_page['photos']['photo']):
        # print (page,i)
        # finded_photo = flickr.photos.getSizes(
        #     photo_id=photo['id'], format='parsed-json')['sizes']['size'][0]
        # if finded_photo['label'] == "Square":
        #     urls.append(finded_photo['source'])
        # if len(urls)==10:
        #     asyncio.run(main(urls))
        #     urls = []

asyncio.run(main(urls))