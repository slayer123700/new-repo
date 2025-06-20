import sys
import shutil
from pathlib import Path
from .bing import Bing

def download(query, limit=100, output_dir='dataset', adult_filter_off=True, 
             force_replace=False, timeout=60, filter="", verbose=True):

    # Set adult filter
    adult = 'off' if adult_filter_off else 'on'

    # Define image directory path
    image_dir = Path(output_dir).joinpath(query).absolute()

    # Handle force_replace option
    if force_replace:
        if image_dir.is_dir():  # FIX: Call is_dir() on an instance of Path
            shutil.rmtree(image_dir)

    # Check directory and create if necessary
    try:
        if not image_dir.is_dir():  # FIX: Call is_dir() on an instance of Path
            image_dir.mkdir(parents=True)  # FIX: Call mkdir() on the instance
    except Exception as e:
        sys.exit(1)

    bing = Bing(query, limit, image_dir, adult, timeout, filter, verbose)
    bing.run()


if __name__ == '__main__':
    download('dog', output_dir="..\\Users\\cat", limit=10, timeout=1)
