import os
import time
import requests
from typing import Dict, Optional, Union
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from firecrawl import FirecrawlApp
from langchain_ollama.llms import OllamaLLM
from dotenv import load_dotenv
import re
from webpage.prompt import summary_prompt

load_dotenv()

class WebpageError(Exception):
    """Base exception class for webpage summarizer errors"""
    pass

class URLError(WebpageError):
    """Raised when there are issues with the URL"""
    pass

class ScrapingError(WebpageError):
    """Raised when there are issues with scraping content"""
    pass

class SummarizationError(WebpageError):
    """Raised when there are issues with generating summary"""
    pass

class ConfigError(WebpageError):
    """Raised when there are configuration issues"""
    pass

class WebpageSummarizer:
    """A class to handle webpage content extraction and summarization"""

    # Class constants
    DEFAULT_TIMEOUT = 30
    MAX_CONTENT_LENGTH = 100000
    RATE_LIMIT_DELAY = 1
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    SUMMARY_MAX_LENGTH = 1000
    SUMMARY_MIN_LENGTH = 100

    def __init__(self):
        """Initialize the WebpageSummarizer with necessary components"""
        # Get FireCrawl API key from environment
        self.api_key = os.getenv('FIRECRAWL_API_KEY')
        if not self.api_key:
            raise ConfigError("FireCrawl API key not found. Please set FIRECRAWL_API_KEY environment variable.")
        
        # Initialize FireCrawl with API key
        self.scraper = FirecrawlApp(api_key=self.api_key)
        self.llm = OllamaLLM(model="llama3.2:latest")  # Using llama3.2 as default model
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def validate_url(self, url: str) -> str:
        """
        Validate and normalize the URL
        
        Args:
            url (str): The URL to validate
            
        Returns:
            str: Normalized URL
            
        Raises:
            URLError: If URL is invalid or inaccessible
        """
        try:
            # Add scheme if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Parse and validate URL
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise URLError("Invalid URL format")

            # Check if URL is accessible
            response = self.session.head(url, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()

            return url

        except requests.RequestException as e:
            raise URLError(f"Failed to access URL: {str(e)}")

    def scrape_content(self, url: str) -> str:
        """
        Scrape content from the webpage using FireCrawl
        
        Args:
            url (str): The URL to scrape
            
        Returns:
            str: Extracted main content
            
        Raises:
            ScrapingError: If content cannot be scraped
        """
        try:
            # Apply rate limiting
            time.sleep(self.RATE_LIMIT_DELAY)
            
            # Use FireCrawl to extract content
            try:
                # First attempt with FireCrawl
                scrape_result = self.scraper.scrape_url(
                    url, 
                    formats=['markdown', 'html']
                )
                # print(f"Scrape result: {scrape_result}")
                
                # Check if scraping was successful
                if not scrape_result or not scrape_result.markdown:
                    raise ScrapingError("FireCrawl returned empty content")
                
                main_content = scrape_result.markdown
                
            except Exception as fire_err:
                # Log FireCrawl error for debugging
                print(f"FireCrawl error: {str(fire_err)}")
                raise ScrapingError(f"FireCrawl extraction failed: {str(fire_err)}")

            return self.clean_text(main_content)

        except Exception as e:
            raise ScrapingError(f"Failed to scrape content: {str(e)}")

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize the scraped text content
        
        Args:
            text (str): Raw scraped text content
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
            
        # Split into lines for processing
        lines = text.split('\n')
        cleaned_lines = []
        
        # Track state
        in_footer = False
        in_comments = False
        previous_line = ""
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Skip navigation/UI elements
            if any(ui_element in line.lower() for ui_element in [
                'sign up', 'sign in', 'open in app', 'get started',
                'follow', 'subscribe', 'download', 'menu', 'navigation',
                'cookie', 'privacy', 'terms', 'conditions'
            ]):
                continue
                
            # Skip social media/metadata
            if any(meta in line.lower() for meta in [
                'min read', 'followers', 'following', 'listen',
                'share', 'like', 'comment', 'bookmark'
            ]):
                continue
                
            # Skip footer content
            if 'footer' in line.lower() or any(footer_text in line for footer_text in [
                'All rights reserved', '©', 'Copyright'
            ]):
                in_footer = True
                continue
            
            if in_footer:
                continue
                
            # Skip comment sections
            if any(comment_marker in line.lower() for comment_marker in [
                'responses', 'comments', 'discussion'
            ]):
                in_comments = True
                continue
                
            if in_comments:
                continue
                
            # Clean up image markdown and captions
            if line.startswith('!['):
                # Extract caption if it exists
                caption_match = re.search(r'!\[([^\]]+)\]', line)
                if caption_match and caption_match.group(1) and not caption_match.group(1).startswith('http'):
                    cleaned_lines.append(caption_match.group(1))
                continue
                
            # Skip source attribution lines
            if line.strip().startswith('_Source:') or line.strip().startswith('(Source:'):
                continue
                
            # Skip redundant title/header if it matches previous line
            if previous_line and (
                line.strip() in previous_line or 
                previous_line.strip() in line
            ):
                continue
                
            # Skip medium-specific elements
            if any(medium_element in line for medium_element in [
                'Medium Logo', 'Originally published at', 
                'Read more from', 'More from', 'Recommended from Medium'
            ]):
                continue
                
            # Skip promotional content
            if any(promo in line.lower() for promo in [
                'sponsored', 'advertisement', 'promoted',
                'premium', 'membership', 'subscribe now'
            ]):
                continue
                
            # Remove markdown link syntax while keeping text
            line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
            
            # Remove remaining markdown formatting
            line = re.sub(r'[*_`#]', '', line)
            
            # Clean up whitespace
            line = line.strip()
            
            if line:
                cleaned_lines.append(line)
                previous_line = line
        
        # Join cleaned lines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive newlines
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text.strip()

    def generate_summary(self, text: str) -> str:
        """
        Generate summary using LLM
        
        Args:
            text (str): Cleaned text content
            
        Returns:
            str: Generated summary
            
        Raises:
            SummarizationError: If summary generation fails
        """
        try:
            prompt = f"""
            {summary_prompt}

            {text}

            Summary:"""

            summary = self.llm.invoke(prompt)
            return summary.strip()

        except Exception as e:
            raise SummarizationError(f"Failed to generate summary: {str(e)}")

    def get_metadata(self, url: str, content: str) -> Dict[str, str]:
        """
        Extract metadata from the webpage and content
        
        Args:
            url (str): The webpage URL
            content (str): The page content
            
        Returns:
            dict: Metadata dictionary
        """
        return {
            'url': url,
            'length': len(content),
            'word_count': len(content.split()),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def process_url(self, url: str) -> Dict[str, Union[str, Dict[str, str]]]:
        """
        Process a URL and return summary with metadata
        
        Args:
            url (str): The URL to process
            
        Returns:
            dict: Dictionary containing summary and metadata
            
        Raises:
            WebpageError: If any step fails
        """
        try:
            # Validate URL
            validated_url = self.validate_url(url)
            
            # Scrape content
            content = self.scrape_content(validated_url)
            
            # Generate summary
            summary = self.generate_summary(content)
            
            # Get metadata
            metadata = self.get_metadata(validated_url, content)
            
            return {
                'status': 'success',
                'summary': summary,
                'metadata': metadata
            }

        except WebpageError as e:
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {'url': url, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
            }

# Example usage
if __name__ == "__main__":
    # Test the summarizer
    try:
        summarizer = WebpageSummarizer()
        test_url = "https://medium.com/@kemalpiro/step-by-step-visual-introduction-to-diffusion-models-235942d2f15c"
        result = summarizer.process_url(test_url)
        print(result)
    except ConfigError as e:
        print(f"Configuration Error: {str(e)}")
        print("Please set the FIRECRAWL_API_KEY environment variable before running.") 