![WXR Radar Example(FASA FIR, 21 Feb 2025 0145Z)](docs/banner.png)
*Historic thunderstom activity over the FASA FIR on 21 Feb 2025 0145Z*
# WXR Radar Server for TopSky/EuroScope

This project is a WXR radar server that spoofs the [RainViewer API](https://www.rainviewer.com/api/weather-maps-api.html) to support the use of the [EUMETSAT](http://eutmetsat.int) [Blended SEVIRI / LEO MW precipitation and morphologic information - MSG - 0 degree product](https://data.eumetsat.int/product/EO:EUM:DAT:0620) to convert precipitation rate to a suitable radar reflectivity(dbZ) using the standard heuristical relationship.

## Features
- 1:1 spoof of the [RainViewer API](https://www.rainviewer.com/api/weather-maps-api.html) externally
- Matches the same [colour scheme](https://www.rainviewer.com/api/color-schemes.html#dbzMatrix) understood by TopSky
- Allows for custom image sizes
- Applies automatic dBZ adjustment based on the precipitation rate
- Provides accurate precipitation rate prediction using [EUMETSAT](http://eumetsat.int) [MSG](https://www.eumetsat.int/meteosat-second-generation) satellite network
- Uses [FastAPI](https://fastapi.tiangolo.com), for (*you guessed it*), nice quick async operations
- [httpx](https://www.python-httpx.org), for *nice async*

## Deploymemt
To deploy the server, install all the dependencies with pip:  

`pip install httpx uvicorn fastapi numpy pillow`

Run the server with:
`python main.py`

The server will start on port `8000` both on `localhost` and on the network.

**BONUS: Want to simulate historical storms? Just set the system time to the time of that storm +/- 15 minutes**

## Endpoints
With this API, the following endpoints are available

`weather.json` - file containing timestamps information

`/v2/radar/{timestamp}/{size}/{z}/{lat}/{lon}/{color}/{options}.png` - fetches and calculates radar tile based on precipitation rate

## TopSky configuration

Set `WXR_TimeStampsURL=http://localhost:8000/weather.json` or `WXR_TimeStampsURL=http://{your server IP}/weather.json`, that's it!

## How it works
The [Meteosat Second Generation (MSG)](https://www.eumetsat.int/meteosat-second-generation) satellite network is a set of satellites in a geostationary orbit, meaning that they orbit the earth at such a height that their orbital period is the same as the Earth's.

This means that to any observer on the earth it looks perfectly stationary.

Using equipment onboard it rotates and scans rapidly in the east, north west south location. It offers several cameras tuned to detect different particle sizes using both visual(*normal*) cameras and infrared cameras.

The data is then recieved by EUMETSAT and is processed to produce precipitation rate.

This data is sent out by the satellite every 15 minutes, so updates are also published almost instantaneously. We then recieve this data and process each pixel in the image to derieve the approximate precipiation rate for that area.

We then convert each precipitation rate to a dBZ value using to equation:

$$
\begin{align}
Z &= a R^b \\
\mathrm{dBZ} &= 10 \log_{10}(Z) = 10 \log_{10}(a) + 10 b \log_{10}(R)
\end{align}
$$

where typically $`a=200`$ and $`b=1.6`$

After that we use the RainViewer 0/0_0 color scheme to calculate the correct color for each pixel.



## Built with
- [EUMETSAT](http://eumetsat.int) [MSG](https://www.eumetsat.int/meteosat-second-generation) satellite network
- [FastAPI](https://fastapi.tiangolo.com)
- [httpx](https://www.python-httpx.org)
- [NumPy](https://numpy.org)
- [Pillow](https://pypi.org/project/pillow/)