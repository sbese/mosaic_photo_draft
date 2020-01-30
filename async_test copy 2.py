import flickrapi
from PIL import Image
import os
# from mosaic.models import Pic
from io import BytesIO
import aiohttp
import asyncio
from psycopg2 import connect
import json
# s = 0
proxy_url = "http://103.28.121.58:80"
keys = ['animal','forest','man','desert','NY','London','world','music']
con = connect(database="mosaic", user="postgres", password="zaq!23", host="127.0.0.1")
cur = con.cursor()
api_key = '5f0a0c4e04298e2e84ef379f8de4a7fe'
api_secret = 'df521e620606493c'
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

api_url = "https://www.flickr.com/services/rest/?method={}&api_key={}&format=json&{}"

# get_sizes = "https://www.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=5f0a0c4e04298e2e84ef379f8de4a7fe&photo_id={}&format=json"
# photos_search = 

def get_sizes(photo_id):
    return api_url.format(
        "flickr.photos.getSizes",
        api_key,
        f"photo_id={photo_id}"
    )

def photos_search(page,tags):
    return api_url.format(
        "flickr.photos.search",
        api_key,
        f"page={page}&tags={tags}&content_type=1&sort=relevance&license=9,10"
    )

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

async def get_square(photo_id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(get_sizes(photo_id),proxy=proxy_url,verify_ssl=False) as response:
                data = await response.read()
                finded_photo = json.loads(
                    data.decode().split('jsonFlickrApi(')[1].split(
                        ')')[0]) ['sizes']['size'][0]
                if finded_photo['label'] == "Square":
                    await asyncio.gather(
                        asyncio.create_task(fetch_content(finded_photo['source'], session)))
        except Exception as e:
            print('pased',e)
            task = asyncio.create_task(get_square(photo_id))
            await asyncio.gather(*task)


async def fetch_content(url, session):
    try:
        async with session.get(url,proxy=proxy_url,verify_ssl=False) as response:
            data = await response.read()
            to_db(data, url)
    except:
        await asyncio.gather(asyncio.create_task(fetch_content(url, session)))


async def main(photos_page):
    # print(photos_page)
    # print(photos_page['photos']["page"])
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i, photo in enumerate(photos_page['photos']['photo']):
            task = asyncio.create_task(get_square(photo['id']))
            tasks.append(task)
        await asyncio.gather(*tasks)




async def get_pages_by_key(key,pages_count):
    print("key ", key)
    tasks = []
    async with aiohttp.ClientSession() as session:
        for page in range(1,pages_count+1):
            # try:
            async with session.get(photos_search(page,key), proxy=proxy_url,verify_ssl=False) as response:
                data = await response.read()
                # print(len(data.decode()))
                photos_page = json.loads(
                    data.decode().split('jsonFlickrApi(')[1][0:-1])
                task = asyncio.create_task(main(photos_page))
                tasks.append(task)
                await asyncio.gather(*tasks)
            # except:
            #     pass


async def main2(keys):
    tasks = []
    pages = {}
    for key in keys:
        photos = flickr.photos.search(
            page=1,
            tags=key,
            content_type=1,
            sort='relevance',
            license='9,10',
            format='parsed-json')
        pages[key] = photos['photos']['pages']
    for key in pages:
        print("skey", key)
        task = asyncio.create_task(get_pages_by_key(key,pages[key]))
        tasks.append(task)
    await asyncio.gather(*tasks)


asyncio.run(main2(keys))
