# ImageDownloader
 Download images

## Python
Developed on Python 3.11.4

## Install
```
pip install -r requirements.txt
```

## Usage
Set config values
```python
api_root_url = ''
api_user = ''
api_key = ''
```

Run script from terminal
```
python download_images.py "<search parameter>"
python download_images.py "erling haaland"

python download_images.py "<search parameter>" <start_position>
python download_images.py "erling haaland" 1000
```