
<div align="center">
  <img src="https://github.com/nkgian/tg-strike-extractor/blob/main/demo_media/demo.gif" alt="Demo MP4 converted to GIF" width="700">
</div>

## Summary

This project is a proof-of-concept for an OSINT data pipeline focused on automated geolocation from Telegram posts. The tool processes Telegram post data to automatically extract geographic locations using locally run AI models, effectively linking textual claims to real-world impact indicators like larger fires from military activity using publicly available FIRMS data. 

The initial motivation was to find an automated way to validate or falsify otherwise unsubstantiated Russian Telegram claims of great victories or strikes against deep targets.

For some basic notes and observations, see the [Notes](#Notes) section.

## Setup

Create a virtual environment in the project directory and activate it:

```
python -m venv venv

venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

Install the dependencies:

```
pip install streamlit pandas numpy pydeck beautifulsoup4 geopy requests openai python-dotenv
```

There is no config file. API keys are stored in a `.env` file placed **inside the virtual environment**, which `src/settings.py` loads automatically at startup. On Windows that file is `venv\.env`:

```
# Required
FIRMS_API_KEY=YOUR-FIRMS-MAP-KEY-GOES-HERE

# Optional - defaults shown below - NOTE: DEFAULT PORT IS 1234 (I.E. LM STUDIO)! 
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=openai/gpt-oss-20b
LOCAL_LLM_API_KEY=not-needed
```

The loader checks the `VIRTUAL_ENV` environment variable of the active venv and falls back to a `.env` file in the project root if no venv is detected. If you do not have a FIRMS map key, you can get one for free from [NASA's FIRMS site](https://firms.modaps.eosdis.nasa.gov/api/map_key/).

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
* OpenAI Python client
    * *Used to talk to a local OpenAI-compatible model server such as [LM Studio](https://lmstudio.ai/), llama.cpp server, or vLLM. Point `LOCAL_LLM_BASE_URL` at whichever server you run.*
* python-dotenv
    * *Used to load the API keys from the `.env` file stored inside the virtual environment.*

    
## Default settings

* By default the project targets LM Studio on `http://localhost:1234/v1` and uses the `openai/gpt-oss-20b` model. Change `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL` in your venv `.env` to use another local OpenAI-compatible server (e.g. `http://localhost:8080/v1` for llama.cpp) or model. The exact model identifier is shown in LM Studio's server tab.

* By default, the app will send four requests to the FIRMS API for data from the following sources: `VIIRS_NOAA20_NRT`, `VIIRS_SNPP_NRT`, `MODIS_NOAA20_NRT`, and `MODIS_SNPP_NRT`. Near Real-Time (NRT) data is generally available ~3 hours after observation by the satellite. All requests will try to fetch data for fires that occured **during the last day** and within a radius of **50km**. You can change these default values in `/src/firms/firms_grabber.py`.

* The `prompt.txt` file also includes the default prompt for instructing the LLM to extract the location data from the Telegram post. The prompt's contents are specifically designed to work well within the context of Russia's full scale invasion of Ukraine. You may wish to alter the contents for more generic tasks.

* The Telegram scraper uses a hardcoded custom user-agent `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36`. You can change this in `/src/tg_scraper/scraper.py`.
  
## Notes

- Generally speaking the locally run `gpt-oss-20b` model has performed extremely well and consistently. It is a larger and more taxing model but at least it actually sticks to the instructions provided by the prompt, unlike some smaller models. Running the model on my personal computer takes ~10-40 seconds to perform a task, so there's quite a bit of variance in runtime.

- The prompt in `prompt.txt` explicitly tells the LLM to avoid returning the name of the country found in the social media post and instead to return the name of the local settlement and province. This is primarily to avoid situations where internationally unrecognized Russian territorial claims (e.g. Donetsk Oblast, Russian Federation) cause issues with the LLM or geocoding. It's a niche problem and you should change it depending on your use-case.

- Given the current prompt, the model will struggle with situations where a social media post mentions several targets within a single post. If you want to ensure that all locations in a post will be extracted and plotted (with FIRMS data) then you will need to change the prompt to return all locations mentioned and change the script to accept a list of locations and iterate through each of them.

- You can optimize the flow further by adding more services. For example, you can integrate weather APIs or use the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) to filter fires that are outside of likely targets such as industrial zones.
