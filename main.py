# http://maps.openweathermap.org/maps/2.0/weather/PAC0/{z}/{x}/{y}?appid
#
import math
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, RedirectResponse
import time
from PIL import Image
import numpy as np
from io import BytesIO
from dotenv import load_dotenv
import httpx
import os

load_dotenv()



app = FastAPI()


@app.get("/weather.json")
async def weather_tile():
	print("Weather tile request received")
	# Example logic - replace this with your actual tile generation or proxy logic
	return JSONResponse({
		"version": "2.0",
			"generated": int(time.time()),
			"host": "http://localhost:8000",
			"radar": {
					"past": [
						{
								"time": int(time.time()),
									"path": "/radar"
							},
						{
								"time": int(time.time()),
									"path": "/radar"
							}
					],
				"nowcast": [
						{
								"time": int(time.time()),
									"path": "/radar"
							},
						{
								"time": int(time.time()),
									"path": "/radar"
							}
					]
			}
	})


def latlon_to_tile(lat: float, lon: float, zoom: int):
	lat_rad = math.radians(lat)
	n = 2.0 ** zoom
	xtile = int((lon + 180.0) / 360.0 * n)
	ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 /
				math.cos(lat_rad)) / math.pi) / 2.0 * n)
	return xtile, ytile

# @app.get("/radar/{size}/{z}/{x}/{y}/{color}/{options}.png")
# async def weather_tile_proxy(size: str, z: int, x: int, y: int, color: int, options: str):
#     # Modify this if you want to choose a different map layer based on input
#     tile_layer = "precipitation_new"
#     appid = "f442d940b4831ea8b36eca668995e87d"

#     # Build the OpenWeatherMap tile URL
#     remote_url = f"http://tile.openweathermap.org/map/{tile_layer}/{z}/{x}/{y}.png?appid={appid}"

#     async with httpx.AsyncClient() as client:
#         response = await client.get(remote_url)

#     if response.status_code != 200:
#         return Response(content="Failed to fetch tile", status_code=response.status_code)

#     return Response(content=response.content, media_type="image/png")


@app.get("/radar/{size}/{z}/{lat}/{lon}/{color}/{options}.png")
async def weather_tile_proxy_lat_lon(size: int, z: int, lat: float, lon: float, color: int, options: str):
	# Modify this if you want to choose a different map layer based on input
	tile_layer = "precipitation_new"
	appid = os.getenv("APPID")

	# Build the OpenWeatherMap tile URL
	x, y = latlon_to_tile(lat, lon, z)
	remote_url = f"http://tile.openweathermap.org/map/{tile_layer}/{z}/{x}/{y}.png?appid={appid}"

	async with httpx.AsyncClient() as client:
		response = await client.get(remote_url)

	if response.status_code != 200:
		return Response(content="Failed to fetch tile", status_code=response.status_code)

	image = Image.open(BytesIO(response.content)).convert("RGBA")
	pixels = np.array(image)

	# Define the dBZ range
	min_dbz = -32
	max_dbz = 95
	dbz_range = max_dbz - min_dbz + 1

	# Define Rain and Snow color maps from your table
	rain_colors = [
		"#00000000", "#010101ff", "#020202ff", "#030303ff", "#040404ff", "#050505ff", "#060606ff", "#070707ff",
			"#080808ff", "#090909ff", "#0a0a0aff", "#0b0b0bff", "#0c0c0cff", "#0d0d0dff", "#0e0e0eff", "#0f0f0fff",
			"#101010ff", "#111111ff", "#121212ff", "#131313ff", "#141414ff", "#151515ff", "#161616ff", "#171717ff",
			"#181818ff", "#191919ff", "#1a1a1aff", "#1b1b1bff", "#1c1c1cff", "#1d1d1dff", "#1e1e1eff", "#1f1f1fff",
			"#202020ff", "#212121ff", "#222222ff", "#232323ff", "#242424ff", "#252525ff", "#262626ff", "#272727ff",
			"#282828ff", "#292929ff", "#2a2a2aff", "#2b2b2bff", "#2c2c2cff", "#2d2d2dff", "#2e2e2eff", "#2f2f2fff",
			"#303030ff", "#313131ff", "#323232ff", "#333333ff", "#343434ff", "#353535ff", "#363636ff", "#373737ff",
			"#383838ff", "#393939ff", "#3a3a3aff", "#3b3b3bff", "#3c3c3cff", "#3d3d3dff", "#3e3e3eff", "#3f3f3fff",
			"#404040ff", "#414141ff", "#424242ff", "#434343ff", "#444444ff", "#454545ff", "#464646ff", "#474747ff",
			"#484848ff", "#494949ff", "#4a4a4aff", "#4b4b4bff", "#4c4c4cff", "#4d4d4dff", "#4e4e4eff", "#4f4f4fff",
			"#505050ff", "#515151ff", "#525252ff", "#535353ff", "#545454ff", "#555555ff", "#565656ff", "#575757ff",
			"#585858ff", "#595959ff", "#5a5a5aff", "#5b5b5bff", "#5c5c5cff", "#5d5d5dff", "#5e5e5eff", "#5f5f5fff",
			"#606060ff", "#616161ff", "#626262ff", "#636363ff", "#646464ff", "#656565ff", "#666666ff", "#676767ff",
			"#686868ff", "#696969ff", "#6a6a6aff", "#6b6b6bff", "#6c6c6cff", "#6d6d6dff", "#6e6e6eff", "#6f6f6fff",
			"#707070ff", "#717171ff", "#727272ff", "#737373ff", "#747474ff", "#757575ff", "#767676ff", "#777777ff",
			"#787878ff", "#797979ff", "#7a7a7aff", "#7b7b7bff", "#7c7c7cff", "#7d7d7dff", "#7e7e7eff", "#7f7f7fff"
	]

	snow_colors = [
		"#808080ff", "#818181ff", "#828282ff", "#838383ff", "#848484ff", "#858585ff", "#868686ff", "#878787ff",
			"#888888ff", "#898989ff", "#8a8a8aff", "#8b8b8bff", "#8c8c8cff", "#8d8d8dff", "#8e8e8eff", "#8f8f8fff",
			"#909090ff", "#919191ff", "#929292ff", "#939393ff", "#949494ff", "#959595ff", "#969696ff", "#979797ff",
			"#989898ff", "#999999ff", "#9a9a9aff", "#9b9b9bff", "#9c9c9cff", "#9d9d9dff", "#9e9e9eff", "#9f9f9fff",
			"#a0a0a0ff", "#a1a1a1ff", "#a2a2a2ff", "#a3a3a3ff", "#a4a4a4ff", "#a5a5a5ff", "#a6a6a6ff", "#a7a7a7ff",
			"#a8a8a8ff", "#a9a9a9ff", "#aaaaaaff", "#abababff", "#acacacff", "#adadadff", "#aeaeaeff", "#afafafff",
			"#b0b0b0ff", "#b1b1b1ff", "#b2b2b2ff", "#b3b3b3ff", "#b4b4b4ff", "#b5b5b5ff", "#b6b6b6ff", "#b7b7b7ff",
			"#b8b8b8ff", "#b9b9b9ff", "#bababaff", "#bbbbbbff", "#bcbcbcff", "#bdbdbdff", "#bebebeff", "#bfbfbfff",
			"#c0c0c0ff", "#c1c1c1ff", "#c2c2c2ff", "#c3c3c3ff", "#c4c4c4ff", "#c5c5c5ff", "#c6c6c6ff", "#c7c7c7ff",
			"#c8c8c8ff", "#c9c9c9ff", "#cacacaff", "#cbcbcbff", "#ccccccff", "#cdcdcdff", "#cececeff", "#cfcfcfff",
			"#d0d0d0ff", "#d1d1d1ff", "#d2d2d2ff", "#d3d3d3ff", "#d4d4d4ff", "#d5d5d5ff", "#d6d6d6ff", "#d7d7d7ff",
			"#d8d8d8ff", "#d9d9d9ff", "#dadadaff", "#dbdbdbff", "#dcdcdcff", "#ddddddff", "#dededeff", "#dfdfdfff",
			"#e0e0e0ff", "#e1e1e1ff", "#e2e2e2ff", "#e3e3e3ff", "#e4e4e4ff", "#e5e5e5ff", "#e6e6e6ff", "#e7e7e7ff",
			"#e8e8e8ff", "#e9e9e9ff", "#eaeaeaff", "#ebebebff", "#ecececff", "#edededff", "#eeeeeeff", "#efefefff",
			"#f0f0f0ff", "#f1f1f1ff", "#f2f2f2ff", "#f3f3f3ff", "#f4f4f4ff", "#f5f5f5ff", "#f6f6f6ff", "#f7f7f7ff",
			"#f8f8f8ff", "#f9f9f9ff", "#fafafaff", "#fbfbfbff", "#fcfcfcff", "#fdfdfdff", "#fefefeff", "#ffffffff"
	]

	# Define the original colorizer stops (rain rate to RGBA)
	rain_stops = [
		(0, (225, 200, 100, 0)),
		(0.1, (200, 150, 150, 0)),
		(0.2, (150, 150, 170, 0)),
		(0.5, (120, 120, 190, 0)),
		(1, (110, 110, 205, int(0.3 * 255))),
		(10, (80, 80, 225, int(0.7 * 255))),
		(140, (20, 20, 255, int(0.9 * 255)))
	]

	# Define color-to-dBZ mapping
	dbz_color_map = {
		tuple(int(c[i:i+2], 16) for i in (1, 3, 5, 7)): dbz
		for dbz, c in {
			-32 + i: f"#{i:02x}{i:02x}{i:02x}ff" for i in range(128)
		}.items()
	}

	# Build reverse mapping: RGBA color to rain rate (linear interpolation)


	def interpolate_rain_rate(color):
		r, g, b, a = color
		if a == 0:
			return 0.0
		for i in range(len(rain_stops) - 1):
			val1, col1 = rain_stops[i]
			val2, col2 = rain_stops[i + 1]
			if col1[:3] <= (r, g, b) <= col2[:3] or col2[:3] <= (r, g, b) <= col1[:3]:
				# Linear interpolation on brightness
				b1 = sum(col1[:3]) / 3
				b2 = sum(col2[:3]) / 3
				b_target = sum((r, g, b)) / 3
				if b2 != b1:
					f = (b_target - b1) / (b2 - b1)
					return val1 + f * (val2 - val1)
		return 0.0

	# Convert rain rate to dBZ (using standard Z-R relationship Z = 200*R^1.6)


	def rain_rate_to_dbz(rain_rate):
		if rain_rate <= 0:
			return -32
		z = 200 * (rain_rate ** 1.6)
		dbz = 10 * np.log10(z)
		return int(round(dbz))

	def hex_to_rgba(hex_code):
		return tuple(int(hex_code[i:i+2], 16) for i in (1, 3, 5, 7))

	# Convert to RGBA tuples
	rain_lut = [hex_to_rgba(color) for color in rain_colors]
	snow_lut = [hex_to_rgba(color) for color in snow_colors]

	# Dummy dBZ array for example (replace with real one if available)
	# Assuming shape and dBZ values match the image
	# For demonstration, we will simulate a linear gradient from -32 to 95
	height, width = pixels.shape[:2]
	dbz_values = np.linspace(-32, 95, num=height * \
								width, dtype=int).reshape((height, width))

	# Choose mode: "rain" or "snow"
	mode = "rain"  # Change to "snow" for snow LUT

	# Pick the correct LUT
	lut = rain_lut if mode == "rain" else snow_lut

	def dbz_to_color(dbz):
		if min_dbz <= dbz <= max_dbz:
			color = lut[dbz - min_dbz]
		else:
			color = (0, 0, 0, 0)  # Transparent for out-of-range
		return color
	# Analyze image and convert
	new_pixels = np.zeros_like(pixels)
	for y in range(pixels.shape[0]):
		for x in range(pixels.shape[1]):
			color = tuple(pixels[y, x])
			rain_rate = interpolate_rain_rate(color)
			dbz = rain_rate_to_dbz(rain_rate)
			new_pixels[y, x] = dbz_to_color(dbz)

	# Save the output image
	output_image = Image.fromarray(new_pixels, "RGBA")
	buffer = BytesIO()
	output_image.save(buffer, format="PNG")
	image_bytes = buffer.getvalue()


	return Response(content=image_bytes, media_type="image/png")
