# scraper.py (Meta Tag Extraction)

import requests
from bs4 import BeautifulSoup
import re

custom_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def basic_url_validation(url: str) -> bool:
    """
    Extremely barebones validation. 
    """
    pattern = r'^https?://t\.me/[\w_]+/\d+$'
    return re.match(pattern, url) is not None

def get_telegram_post_text(share_link: str, custom_user_agent: str = None) -> str | None:
    """
    Fetches the standard public Telegram share link page and extracts the 
    main body text from the Open Graph (og:description) meta tag.
    """
    # hacky fix for last tg post
    if share_link.endswith("?single"):
        share_link = share_link[:-7]
        print("[NOTICE]: Removed ?single suffix from the URL: ", share_link)

    errors = basic_url_validation(share_link)
    if not errors:
        print("Invalid Telegram post URL format.")
        return None

    if custom_user_agent is not None:
        print("Using custom User-Agent for the request.")
        
        # ridiculous fix but ok
        global custom_agent
        custom_agent = custom_user_agent
    
    try:
        headers = {
            'User-Agent': custom_agent
        }
        
        response = requests.get(share_link, headers=headers, timeout=10)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    
    # tag contains the full text of the post for previews
    meta_tag = soup.find('meta', attrs={'property': 'og:description'})

    if meta_tag:
        # Extract the content attribute
        post_text = meta_tag.get('content', '').strip()
        
        if post_text:
            lines = post_text.split('\n')
            
            # Check if the last line looks like a channel handle
            if lines and re.match(r'^@[\w_]+$', lines[-1].strip()):
                cleaned_text = '\n'.join(lines[:-1]).strip()
            else:
                cleaned_text = post_text
            
            # cleanup excessive newlines
            cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

            print("Extraction successful from meta tag.")
            return cleaned_text
        else:
            print("Found the og:description tag, but it was empty.")
            return ""
    else:
        print("Could not find the <meta property='og:description'> tag.")
        return None

# for debugging
if __name__ == '__main__':
    sample_link = "https://t.me/nexta_live/106925" 
    
    print("-" * 50)
    
    extracted_text = get_telegram_post_text(sample_link)
    
    print("-" * 50)
    
    if extracted_text is not None:
        if extracted_text:
            print("Extracted Post Body:")
            print("=" * 25)
            print(extracted_text)
            print("=" * 25)
        else:
            print("Post has been successfully located but contains no text content.")
    else:
        print("Scraping failed.")