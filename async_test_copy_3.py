import flickrapi
from PIL import Image
import os
# from mosaic.models import Pic
from io import BytesIO
import aiohttp
import asyncio
from psycopg2 import connect
import json

con = connect(database="mosaic", user="postgres", password="zaq!23", host="127.0.0.1")
cur = con.cursor()
api_key = '5f0a0c4e04298e2e84ef379f8de4a7fe'
api_secret = 'df521e620606493c'
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

api_url = "https://www.flickr.com/services/rest/?method="

get_sizes = "{}flickr.photos.getSizes&api_key={}&photo_id={}&format=json"

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

async def get_square(photo_id,session):
    try:
        async with session.get(get_sizes.format(api_url,api_key,photo_id)) as response:
            data = await response.read()
            finded_photo = json.loads(
                data.decode().split('jsonFlickrApi(')[1].split(
                    ')')[0])['sizes']['size'][0]
            if finded_photo['label'] == "Square":
                await asyncio.gather(
                    asyncio.create_task(fetch_content(finded_photo['source'], session)))
    except:
        task = asyncio.create_task(get_square(photo_id,session))
        await asyncio.gather(*task)


async def fetch_content(url, session):
    try:
        async with session.get(url) as response:
            data = await response.read()
            to_db(data, url)
    except:
        await asyncio.gather(asyncio.create_task(fetch_content(url, session)))

async def main(urls):

    tasks = []
    async with aiohttp.ClientSession() as session:
        for i, photo in enumerate(photos_page['photos']['photo']):
            task = asyncio.create_task(get_square(photo['id'], session))
            tasks.append(task)
        await asyncio.gather(*tasks)

pages = []
keys = ['animal','forest','man','desert','NY','London','world','music']
for key in keys:
    photos = flickr.photos.search(
        page=1,
        tags=key,
        content_type=1,
        sort='relevance',
        license='9,10',
        format='parsed-json')

    urls = []
    print(photos['photos']['pages'])
    for page in range(1,photos['photos']['pages']+1):
        photos_page = flickr.photos.search(
        page=page,
        tags=key,
        content_type=1,
        sort='relevance',
        license='9,10',
        format='parsed-json')
        print(key, page)
        pages.append(photos_page)

for page in pages:
    asyncio.run(main(page))
