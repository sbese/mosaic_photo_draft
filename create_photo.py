from PIL import Image
from psycopg2 import connect
from threading import Thread
import asyncio
import aiopg
import aiohttp
from io import BytesIO
dsn = 'dbname=mosaic user=postgres password=zaq!23 host=127.0.0.1'
# con = connect(database="mosaic", user="postgres", password="zaq!23", host="127.0.0.1")
# cur = con.cursor()

pics ={}
query = "select url from mosaic_pic order by 30*({}-r)^2+59*({}-g)^2+11*({}-b)^2 limit 1;"

async def set_pixel(url,x,y):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.read()
                img = Image.open(BytesIO(data))
                res_img.paste(img,(x*75,y*75))
                # res_img.save('res.jpg')
                print(x,y)
    except Exception:
        await asyncio.gather(asyncio.create_task(set_pixel(url,x,y)))



async def get_db_url(pool, x):
    # global pics
    querys = ""
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            for y in range(h):
                r,g,b = image.getpixel((x,y))
                await cur.execute(query.format(r,g,b))
                fet = await cur.fetchone()
                await asyncio.gather(
                    asyncio.create_task(set_pixel(fet[0],x,y)))

async def main():
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:
            for x in range(w):
                task = asyncio.create_task(get_db_url(pool, x))
                tasks.append(task)
            await asyncio.gather(*tasks)
tasks = []
image = Image.open('test.jpg')
w, h = image.size
res_img = Image.new('RGB', (w*75,h*75))
asyncio.run(main())
res_img.save('res.jpg')

