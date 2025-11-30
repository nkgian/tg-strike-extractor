
<div align="center">
  <img src="https://github.com/nkgian/tg-strike-extractor/blob/main/demo_media/demo.gif" alt="Demo MP4 converted to GIF" width="700">
</div>

## Summary

This project is a proof-of-concept for an OSINT data pipeline focused on automated geolocation from Telegram posts. The tool processes Telegram post data to automatically extract geographic locations using locally run AI models, effectively linking textual claims to real-world impact indicators like larger fires from military activity using publicly available FIRMS data. 

The initial motivation was to find an automated way to validate or falsify otherwise unsubstantiated Russian Telegram claims of great victories or strikes against deep targets.

For some basic notes and observations, see the [Notes](#Notes) section.

## Setup

Before running the application, make sure you create a new `config.json` file in the same folder as `dashboard.py`. In that file add the following lines:

```json
{
    "firms_api_key": "YOUR-FIRMS-MAP-KEY-GOES-HERE"
}
```

If you do not have a map key, you can get one for free from [NASA's FIRMS site](https://firms.modaps.eosdis.nasa.gov/api/map_key/).

Alternatively, you can you can set your map key as an env variable and make the necessary changes to `load_api_key()` in `/src/firms/firms_grabber.py`.

Once you are properly set up you can run the app from the main directory with

```
streamlit run dashboard.py
```
## Key Libraries and Tools


* Streamlit
* Pandas
* NumPy
* Pydeck
    * *Used as a more versatile alternative to the default `st.map()` provided by Streamlit*
* BeautifulSoup
    * *Used to extract individual social media posts from Telegram*
* GeoPy
    * *Used to call the [Nominatim](https://nominatim.org/) geocoding API*
* Ollama
    * *There are better ways to run local AI models, however Ollama trivializes swapping between models and supports running models on the cloud, e.g. `gpt-oss:120b-cloud`. For more information, see the official [Ollama documentation](https://docs.ollama.com/cloud).*

    
## Default settings

* By default the project is set to use the `gpt-oss:20b` model by OpenAi and [available on Ollama](https://ollama.com/library/gpt-oss:20b). You can swap to any other Ollama model, however these have not been tested thoroughly. 

* By default, the app will send four requests to the FIRMS API for data from the following sources: `VIIRS_NOAA20_NRT`, `VIIRS_SNPP_NRT`, `MODIS_NOAA20_NRT`, and `MODIS_SNPP_NRT`. Near Real-Time (NRT) data is generally available ~3 hours after observation by the satellite. All requests will try to fetch data for fires that occured **during the last day** and within a radius of **50km**. You can change these default values in `/src/firms/firms_grabber.py`.

* The `prompt.txt` file also includes the default prompt for instructing the LLM to extract the location data from the Telegram post. The prompt's contents are specifically designed to work well within the context of Russia's full scale invasion of Ukraine. You may wish to alter the contents for more generic tasks.

* The Telegram scraper uses a hardcoded custom user-agent `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36`. You can change this in `/src/tg_scraper/scraper.py`.
  
## Notes

- Generally speaking the locally run `gpt-oss:20b` model has performed extremely well and consistently. It is a larger and more taxing model but at least it actually sticks to the instructions provided by the prompt, unlike some smaller models. Running the model on my personal computer takes ~10-40 seconds to perform a task, so there's quite a bit of variance in runtime.

- The prompt in `prompt.txt` explicitly tells the LLM to avoid returning the name of the country found in the social media post and instead to return the name of the local settlement and province. This is primarily to avoid situations where internationally unrecognized Russian territorial claims (e.g. Donetsk Oblast, Russian Federation) cause issues with the LLM or geocoding. It's a niche problem and you should change it depending on your use-case.

- Given the current prompt, the model will struggle with situations where a social media post mentions several targets within a single post. If you want to ensure that all locations in a post will be extracted and plotted (with FIRMS data) then you will need to change the prompt to return all locations mentioned and change the script to accept a list of locations and iterate through each of them.

- You can optimize the flow further by adding more services. For example, you can integrate weather APIs or use the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) to filter fires that are outside of likely targets such as industrial zones.
