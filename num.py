import numpy as np
from PIL import Image
import requests
from io import BytesIO

cols = np.array([[r,g,b] for r in range(0,256,32) for g in range(0,256,32) for b in range(0,256,32)])
print(cols)
def get_distance(colors):
    print(colors)
    return 30*(r-colors[0])**2 + 59*(g-colors[1])**2 + 11*(b-colors[2])^2

response = requests.get("https://live.staticflickr.com/842/42440403524_dd0dd8193f_s.jpg")
if response:
    data = response.content
    image = Image.open(BytesIO(data))
    npa = np.array(image)
    r,g,b = np.array(npa.T.reshape(3,75*75).mean(axis=1), int)
    rainbow = list(map(get_distance,cols))

a=np.array(
    [
        [[1,2],[3,4]],
        [[5,6],[7,8]],
        [[9,0],[1,2]],
    ]
)