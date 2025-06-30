import math
import uvicorn

from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, Response
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import httpx

import socket
import os
import xml.dom.minidom

from image_processing import process_image

async def propogate_time():
	while True:
		timestamps.propogate_timestamps()
		await asyncio.sleep(15 * 60)  # Sleep for 15 minutes

@asynccontextmanager
async def lifespan(app: FastAPI):
	asyncio.create_task(propogate_time())
	yield

app = FastAPI(lifespan=lifespan)

load_dotenv()

production = os.getenv("PRODUCTION_MODE", "False")
production_domain = os.getenv("PRODUCTION_DOMAIN", "localhost:8000")

async def get_latest_timestamp(layer_name: str) -> datetime:
	"""Fetch the latest timestamp from the EUMETSAT API."""
	eumetsat_wms_endpoint = "https://view.eumetsat.int/geoserver/wms"
	service = "WMS"
	version = "1.3.0"
	layer = "msg_fes:h60b"

	async with httpx.AsyncClient() as client:
		url = f"{eumetsat_wms_endpoint}?service={service}&version={version}&request=GetCapabilities"
		response = await client.get(url)
		if response.status_code != 200:
			raise Exception("Failed to fetch capabilities from EUMETSAT WMS")

	dom = xml.dom.minidom.parseString(response.content)
	layers = dom.getElementsByTagName("Layer")

	for layer in layers:
		name = layer.getElementsByTagName("Name")[0].firstChild.nodeValue
		
		if name == layer_name:
			times = layer.getElementsByTagName("Dimension")

			for time in times:
				if time.getAttribute("name") == "time":
					print(f"Latest timestamp for layer {layer_name}: {time.firstChild.nodeValue}")
					return datetime.fromisoformat(time.firstChild.nodeValue.split("/")[1])

	return datetime.now(timezone.utc)

class Timestamps():
	def __init__(self):
		self.now = datetime.now()
		self.now = self.now.replace(
			minute=(self.now.minute // 15) * 15, second=0, microsecond=0)
		self.now15 = self.now + timedelta(seconds=15 * 60)
		self.now30 = self.now + timedelta(seconds=30 * 60)
		self.past_timestamps = [
			self.now,
			self.now - timedelta(seconds=15 * 60),
			self.now - timedelta(seconds=30 * 60),
			self.now - timedelta(seconds=45 * 60),
			self.now - timedelta(seconds=60 * 60),
			self.now - timedelta(seconds=75 * 60),
			self.now - timedelta(seconds=90 * 60),
			self.now - timedelta(seconds=105 * 60),
			self.now - timedelta(seconds=120 * 60),
		]

	def propogate_timestamps(self, current_time: datetime = None):
		self.now = current_time if current_time else datetime.now()
		self.now = self.now.replace(
			minute=(self.now.minute // 15) * 15, second=0, microsecond=0)
		self.now15 = self.now + timedelta(seconds=15 * 60)
		self.now30 = self.now + timedelta(seconds=30 * 60)
		self.past_timestamps = [
			self.now,
			self.now - timedelta(seconds=15 * 60),
			self.now - timedelta(seconds=30 * 60),
			self.now - timedelta(seconds=45 * 60),
			self.now - timedelta(seconds=60 * 60),
			self.now - timedelta(seconds=75 * 60),
			self.now - timedelta(seconds=90 * 60),
			self.now - timedelta(seconds=105 * 60),
			self.now - timedelta(seconds=120 * 60),
		]

	def json(self):
		return {
			"version": "2.0",
			"generated": int(self.now.timestamp()),
			"host": "http://localhost:8000" if production == "False" else f"https://{production_domain}",
			"radar": {
					"past": [{
						"time": int(timestamp.timestamp()),
						"path": f"/v2/radar/{int(timestamp.timestamp())}"
					} for timestamp in self.past_timestamps],
				"nowcast": [
						{
							"time": int(self.now15.timestamp()),
							"path": f"/v2/radar/{int(self.now15.timestamp())}"
						},
						{
							"time": int(self.now30.timestamp()),
							"path": f"/v2/radar/{int(self.now30.timestamp())}"
						}
				]
			}
		}

timestamps = Timestamps()

@app.get("/weather.json")
async def weather_tile():
	current_timestamp = await get_latest_timestamp("msg_fes:h60b")
	timestamps.propogate_timestamps(current_timestamp)

	return timestamps.json()

def tile_to_bbox(xtile: int, ytile: int, zoom: int):
    """
    Returns bounding box (minx, miny, maxx, maxy) in WGS 84 (lon/lat)
    for the given tile coordinates at a specific zoom level.
    """
    n = 2.0 ** zoom

    # Left (min lon)
    lon_left = xtile / n * 360.0 - 180.0

    # Right (max lon)
    lon_right = (xtile + 1) / n * 360.0 - 180.0

    # Top (min y tile => max lat)
    lat_top_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_top = math.degrees(lat_top_rad)

    # Bottom (max y tile => min lat)
    lat_bottom_rad = math.atan(math.sinh(math.pi * (1 - 2 * (ytile + 1) / n)))
    lat_bottom = math.degrees(lat_bottom_rad)

    return lon_left, lat_bottom, lon_right, lat_top

def latlon_to_tile(lat: float, lon: float, zoom: int):
	lat_rad = math.radians(lat)
	n = 2.0 ** zoom
	xtile = int((lon + 180.0) / 360.0 * n)
	ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 /
								math.cos(lat_rad)) / math.pi) / 2.0 * n)
	return xtile, ytile

@app.get("/v2/radar/{timestamp}/{size}/{zoom}/{lat}/{lon}/{color}/{options}.png")
async def weather_tile_proxy_lat_lon(timestamp: int, size: int, zoom: int, lat: float, lon: float, color: int, options: str):
	""" Fetches weather tile from EUMETSAT"""
	xtile, ytile = latlon_to_tile(lat, lon, zoom)
	lon_left, lat_bottom, lon_right, lat_top = tile_to_bbox(
		xtile, ytile, zoom)

	eumetsat_wms_endpoint = "https://view.eumetsat.int/geoserver/wms"
	service = "WMS"	
	version = "1.3.0"

	width, height = 512, 512
	image_format = "image/png"
	bbox = f"{lat_bottom},{lon_left},{lat_top},{lon_right}"
	srs = "EPSG:4326"

	request_time = datetime.fromtimestamp(
		timestamp, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

	layer_images = {}
	layers_purpose = {
		"msg_fes:h60b": "precip_rate"
	}

	for layer, purpose in layers_purpose.items():
		async with httpx.AsyncClient() as client:
			url = f"{eumetsat_wms_endpoint}?service={service}&version={version}&request=GetMap&layers={layer}&styles=&bbox={bbox}&width={width}&height={height}&format={image_format}&crs={srs}&time={request_time}"
			print(url)
			layer_image = await client.get(url)
			
			if layer_image.status_code != 200:
				return Response(content=f"Failed to fetch tile {layer} for {purpose}", status_code=layer_image.status_code)
			
			layer_images[purpose] = layer_image.content

	image = process_image(layer_images, size, min_lat=lat_bottom, min_lon=lon_left, max_lat=lat_top, max_lon=lon_right)

	return Response(content=image, media_type="image/png")

@app.head("/health")
@app.get("/health")
def health():
	return {
		"status": "OK",
		"message": "API fully operational"
	}


if __name__ == '__main__':
	uvicorn.run(app, host="0.0.0.0", port=8000)
