# Web Scraper

command line tool, to scrape content of a website.
the main arguments are the url followed by the css selector.

## Usage

```bash
$ python ./main.py "https://dribbble.com/dchen" "#masthead"
> ['art / motion / code']

$ python ./main.py "https://dribbble.com/dchen" "#masthead" --first
> art / motion / code

$ python ./main.py "https://dribbble.com/dchen" "#masthead" --first --noProxy
> art / motion / code

$ python ./main.py "https://dribbble.com/dchen" "img.profile-avatar" --attr "src" --first
> https://cdn.dribbble.com/users/6084/avatars/normal/realNiceCrop.png?1390892447

$ python ./main.py "https://dribbble.com/dchen" ".shot-thumbnail-placeholder img" --attr "src" --regex "https:\/\/\S*"
> ['https://cdn.dribbble.com/users/6084/screenshots/17648361/media/010dd288a39a4f38e1c18ae821908125.png?compress=1&resize=400x300',
'https://cdn.dribbble.com/users/6084/screenshots/17294675/nockteaser43.png?compress=1&resize=400x300', ...]
```
