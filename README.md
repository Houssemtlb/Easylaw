# EasyLaw

### Requirements:
```
pip install -r requirements.txt
```

### Pdf docs scraping:


```
scrapy runspider joradp_scraper.py
```
### Laws and Laws associations scraping:

```
python .\joradp_db_population.py
```

### Database corrections:

```
python .\pages_fix_script.py
```
### Convert pdfs to images:

```
python3 convert_pdfs_to_images.py
```

### Perform ocr on images:

```
python3 ocr_images.py
```