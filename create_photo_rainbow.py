from PIL import Image
from psycopg2 import connect
from threading import Thread
import asyncio
import aiopg
import aiohttp
from io import BytesIO
import numpy as np
import time
dsn = 'dbname=mosaic_raibow user=postgres password=zaq!23 host=127.0.0.1'
# con = connect(database="mosaic", user="postgres", password="zaq!23", host="127.0.0.1")
# cur = con.cursor()

pics = {}
urls = []
images= {}
query = "select url from mosaic_pic order by 30*({r}-r)^2+59*({g}-g)^2+11*({b}-b)^2 limit 1;"

query_rainbow = '''
select url 
    from (select url,r,g,b from mosaic_pic inner 
        join color_{div_r}_{div_g}_{div_b} as color 
            on color.pic_id=mosaic_pic.id order by color.distance limit 500) as tmp
order by 30*({r}-r)^2+59*({g}-g)^2+11*({b}-b)^2 limit 1;'''


def set_image(color,x,y):
    res_img.paste(images[
        pics[str([color[0],color[1],color[2]])]],
        (x*75,y*75))
    # print("paste",x,y)
async def get_image(url,x,y):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url,verify_ssl=False) as response:
                data = await response.read()
                img = Image.open(BytesIO(data))
                images[url] = img
                # res_img.paste(img,(x*75,y*75))
                # res_img.save('res.jpg')
                # print("pix",x,y)
    except Exception as e:
        print(e)
        await asyncio.gather(asyncio.create_task(get_image(url,x,y)))



async def get_db_url(pool, colors, x):
    # global pics
    querys = ""
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            for y,color in enumerate(colors):
                # print(color)
                r,g,b = color
                # await cur.execute(query_rainbow.format(
                #     div_r=r//32,
                #     div_g=g//32,
                #     div_b=b//32,
                #     r=r,
                #     g=g,
                #     b=b))
                

                await cur.execute(query_rainbow.format(
                    div_r=r//32,
                    div_g=g//32,
                    div_b=b//32,
                    r=r,
                    g=g,
                    b=b))

                fet = await cur.fetchone()
                # print(x,y)
                pics[str(list(color))] = fet[0]
                urls.append(fet[0])

async def main():
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:
            matrix = np.array(image)
            colors = np.unique(matrix.reshape(w*h,3)//4*4,axis=0)
            # print(len(colors))
            # time.sleep(5)
            for i in range(0,len(colors),100):
                task = asyncio.create_task(get_db_url(pool, colors[i:i+100],i))
                tasks.append(task)
            await asyncio.gather(*tasks)
            urls_set = set(urls)

            for i in range(0,len(urls_set),200):
                t = []
                end = i+200 if i+200<len(urls_set) else len(urls_set)
                for j in range(i,end):
                    task = asyncio.create_task(get_image(list(urls_set)[j],i,j))
                    t.append(task)
                await asyncio.gather(*t)

            for x in range(w):
                for y in range(h):
                    pix = np.array(image.getpixel((x,y)))//4*4
                    set_image(pix,x,y)
                    

tasks = []
t = time.time()
image = Image.open('test.jpg')
w, h = image.size
res_img = Image.new('RGB', (w*75,h*75))
asyncio.run(main())
res_img.save('res.jpg')
print(time.time()-t)

