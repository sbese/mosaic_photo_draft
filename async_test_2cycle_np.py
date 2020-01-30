import flickrapi
from PIL import Image
import os
# from mosaic.models import Pic
from io import BytesIO
import aiohttp
import asyncio
from psycopg2 import connect
import json
import numpy as np

timeout = aiohttp.ClientTimeout(total=60)
proxy_url = None #"http://103.28.121.58:80"
keys = ['animal','forest','man','desert','NY','London','world','music']
photo_pages=[]
con = connect(database="mosaic_raibow", user="postgres", password="zaq!23", host="127.0.0.1")
cur = con.cursor()
api_key = '5f0a0c4e04298e2e84ef379f8de4a7fe'
api_secret = 'df521e620606493c'

cols = np.array([[r,g,b] for r in range(0,256,32) for g in range(0,256,32) for b in range(0,256,32)])

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


def get_distance(colors):
    print(colors)
    return 30*(r-colors[0])**2 + 59*(g-colors[1])**2 + 11*(b-colors[2])^2

def to_db(data, url):
    def get_distance(colors):
        # print(colors)
        return 30*(r-colors[0])**2 + 59*(g-colors[1])**2 + 11*(b-colors[2])^2
    try:
        image = Image.open(BytesIO(data))
        npa = np.array(image)
        r,g,b = np.array(npa.T.reshape(3,75*75).mean(axis=1), int)
        rainbow = list(map(get_distance,cols))
        print(r,g,b)
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
            cur.execute(f"insert into mosaic_pic (url, r, g, b) values ('{url}', {r}, {g}, {b})")
            con.commit()
            cur.execute(f"select id from mosaic_pic where url = '{url}'")
            fet=cur.fetchone()
            print(f'///////////////////////////////////////////////{fet[0]}')
            a = [[cur.execute(f"insert into color_{r}_{g}_{b} values ({fet[0]},{rainbow.pop(0)})"),con.commit()] for r in range(8) for g in range(8) for b in range(8)]
            con.commit()
    except Exception as e:
        print(e)
    finally:
        con.commit()

async def get_square(photo_id):
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
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
        # task = asyncio.create_task(get_square(photo_id))
        # await asyncio.gather(*task)


async def fetch_content(url, session):
    try:
        async with session.get(url,proxy=proxy_url,verify_ssl=False) as response:
            data = await response.read()
            to_db(data, url)
    except:
        print("passed")
        # await asyncio.gather(asyncio.create_task(fetch_content(url, session)))


async def main(photos_page):
    # print(photos_page)
    # print(photos_page['photos']["page"])
    tasks = []
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i, photo in enumerate(photos_page['photos']['photo']):
            task = asyncio.create_task(get_square(photo['id']))
            tasks.append(task)
        await asyncio.gather(*tasks)




async def get_pages_by_key(key,pages_count):
    # print("key ", key)
    tasks = []
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for page in range(1,pages_count+1):
            # try:
            async with session.get(photos_search(page,key), proxy=proxy_url,verify_ssl=False) as response:
                data = await response.read()
                # print(len(data.decode()))
                photos_page = json.loads(
                    data.decode().split('jsonFlickrApi(')[1][0:-1])
                print(key, page)
                photo_pages.append(photos_page)
                # task = asyncio.create_task(main(photos_page))
                # tasks.append(task)
                # await asyncio.gather(*tasks)
            # except:
            #     pass


# async def main2(keys):
#     tasks = []
#     pages = {}
#     for key in keys:
#         photos = flickr.photos.search(
#             page=1,
#             tags=key,
#             content_type=1,
#             sort='relevance',
#             license='9,10',
#             format='parsed-json')
#         pages[key] = photos['photos']['pages']
#     for key in pages:
#         print("skey", key)
#         task = asyncio.create_task(get_pages_by_key(key,pages[key]))
#         tasks.append(task)
#     await asyncio.gather(*tasks)


# asyncio.run(main2(keys))
# for page in photo_pages:
#     asyncio.run(main(page))



keys = ['forest','man','desert','NY','London','world','music','animal','girl','money','car','bike']
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
        print(page)
        asyncio.run(main(photos_page))
