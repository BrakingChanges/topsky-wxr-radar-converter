from io import BytesIO
import numpy as np

from PIL import Image
from dbz_calculation import estimate_dbz_advanced



# Define the dBZ range
min_dbz = -32
max_dbz = 95

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

def hex_to_rgba(hex_code):
	return tuple(int(hex_code[i:i+2], 16) for i in (1, 3, 5, 7))

rain_lut = [hex_to_rgba(color) for color in rain_colors]
snow_lut = [hex_to_rgba(color) for color in snow_colors]

def dbz_to_color(dbz, lut):
	if min_dbz <= dbz <= max_dbz:
		color = lut[dbz - min_dbz]
	else:
		color = (0, 0, 0, 0)  # Transparent for out-of-range
	return color

def remove_white_background_from_bytes(img_bytes: bytes, threshold: int = 240) -> bytes:
	"""Remove white background and return new image as PNG in memory."""
	img = Image.open(BytesIO(img_bytes)).convert("RGBA")
	datas = img.getdata()

	new_data = []
	for item in datas:
		if item[0] > threshold and item[1] > threshold and item[2] > threshold:
			new_data.append((255, 255, 255, 0))  # transparent
		else:
			new_data.append(item)

	img.putdata(new_data)

	output_buffer = BytesIO()
	img.save(output_buffer, format="PNG")
	output_buffer.seek(0)
	
	return output_buffer.getvalue()

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

def rgb_to_precip_rate(rgb):
	# Define thresholds using RGB tuples
	color_map = {
		(238, 249, 208): (0, 2),
		(196, 235, 198): (2, 5),
		(140, 213, 207): (5, 10),
		(88, 187, 208): (10, 15),
		(50, 152, 198): (15, 20),
		(39, 104, 163): (20, 30),
		(22, 63, 143): (30, 50),
		(13, 42, 117): (50, 100),  # upper bound arbitrary
	}

	# Find the closest RGB match
	rgb = tuple(rgb[:3])
	for color, rate_range in color_map.items():
		if np.linalg.norm(np.array(color) - np.array(rgb)) < 10:
			return rate_range
	return None


def process_image(layer_images: dict[str, bytes], size: int, min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> bytes:
	# msg_fes_h60b processing
	precip_image = Image.open(BytesIO(layer_images["precip_rate"])).convert("RGBA")
	precip_pixels = np.array(precip_image)
	precip_rates = []

	for y in range(precip_pixels.shape[0]):
		precip_rates_y = []
		for x in range(precip_pixels.shape[1]):
			r, g, b, a = precip_pixels[y, x]
			precip_rate = interpolate_rain_rate((r, g, b, a))
			precip_rates_y.append(precip_rate)
		precip_rates.append(precip_rates_y)
	
	precip_rates = np.array(precip_rates)

	pixels = np.zeros((size, size, 4), dtype=np.uint8)
	for y in range(size):
		for x in range(size):
			rain_rate = precip_rates[y, x]
			dbz = estimate_dbz_advanced(rain_rate=rain_rate, height_km=None)
			color = dbz_to_color(dbz, rain_lut)
			pixels[y, x] = color
	# Convert pixels to RGBA image
	image = Image.fromarray(pixels.astype(np.uint8), mode='RGBA')
	imaage_buffer = BytesIO()
	image.save(imaage_buffer, format="PNG")
	imaage_buffer.seek(0)
	
	return imaage_buffer.getvalue()