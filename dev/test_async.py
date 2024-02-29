import asyncio
import aiohttp
from datetime import datetime
import requests

from utils.color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)

# url = "http://test.sh"
url = "http://127.0.0.1:5000/silic"
# data = {"file_name": "NTU_HS1_20240227_212741.flac"}
data = {"file_name": "NTU_XT1_20240127_234540.flac"}
data = {"file_name": "sss"}


async def count():
  logging.info(f"One ******** {datetime.now().strftime('%H:%M:%S')}")
  # async def _post():
  #   await asyncio.sleep(0)
  #   return requests.post(url, json=data)
  # response = await _post()
  async with aiohttp.request("POST", url=url, json=data) as response:
    status_code = response.status
    res_json = await response.json()
    if status_code == 200:
      logging.info(f"POST successfully: {res_json}")
    else:
      logging.warning(f"POST ERROR(res={response.status}): {res_json}")

  # await asyncio.sleep(1)
  logging.info(f"Two ******** {datetime.now().strftime('%H:%M:%S')}")

async def main():
  await asyncio.gather(count(), count(), count())
  # await asyncio.gather(count())

if __name__ == "__main__":
  import time
  s = time.perf_counter()
  logging.debug("Entering the task...")
  asyncio.run(main())
  # asyncio.run(count())
  logging.fatal("So important task!")
  elapsed = time.perf_counter() - s
  logging.info(f"{__file__} executed in {elapsed:0.5f} seconds.  (t={datetime.now().strftime('%H:%M:%S')})")



# import asyncio
# import aiohttp


# async def main():
#     async with aiohttp.request('GET', 'https://example.com') as resp:
#         assert resp.status == 200
#         html = await resp.text()
#         print(html)


# asyncio.run(main())
