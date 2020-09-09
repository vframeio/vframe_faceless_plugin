# VFRAME Faceless Web Server

VFRAME Faceless Web Server is a prototype to explore the potential for using face detection/blurring to minimize facial biometrics in web publications. This repo is a prototype for exploring and testing ideas, and feedback is welcome.

## Usage 

- Setup VFRAME [main repo](https://github.com/vframeio/vframe)
- Source environment variables for demo script
- Run demo script to generate blurred faces
- Setup apache or nginx config

```
cd vframe/vframe_cli

# source env vars
source plugins/vframe_faceless_plugin/data/examples/filepaths.sh

# run the CLI process to detect, blur, and save images w/subdirs
# Use ssdface for CPU or yoloface or retinaface models for GPU
./cli.py pipe \
  open -i $DIR_DEMO --recursive \
  detect -m ssdface \
  blur \
  draw \
  save-images -o $DIR_DEMO_OUT --subdirs
```

Read more about [redaction.md](https://github.com/vframeio/vframe/blob/master/docs/redaction.md)

## How it works

- Glob all image files in local directories
- Create faceless versions of images
- Save faceless images to replicated directory structure
- Setup [Nginx](data/configs/nginx.conf) or [Apache](data/configs/apache.conf) to serve faceless images for bot-like user agents
- Images are manually processed using CLI scripts, but could be set to a CRON job, or dynamically created using the docker-compose local Flask server API endpoints

## Features

- run locally and sync files or remotely using Python CLI
- uses OpenCV DNN CUDA acceleration when available
- includes Model Zoo options for YOLOV4 and RetinaFace
- example Nginx and Apache config scripts for bot-like user agent redirects

### Testing

To see the nginx configration in action on this web server, run the following `curl` commands.

```
curl 'http://faceless.vframe.io/face.jpg' \
  -H 'Cache-Control: no-cache' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36' \
  > face.jpg

curl 'http://faceless.vframe.io/face.jpg' \
  -L \
  -H 'Cache-Control: no-cache' \
  -H 'User-Agent: Googlebot/2.1 (+http://www.google.com/bot.html)' \
  > face_removed.jpg
```

### NGINX

* [Sample NGINX configuration](sample/nginx.conf)

Add this user agent detection outside of your server block:

```
map $http_user_agent $limit_bots {
  default 0;
  ~*(google|bing|yandex|msnbot) 1;
  ~*(AltaVista|Googlebot|Slurp|BlackWidow|Bot|ChinaClaw|Custo|DISCo|Download|Demon|eCatch|EirGrabber|EmailSiphon|EmailWolf|SuperHTTP|Surfbot|WebWhacker) 1;
  ~*(Express|WebPictures|ExtractorPro|EyeNetIE|FlashGet|GetRight|GetWeb!|Go!Zilla|Go-Ahead-Got-It|GrabNet|Grafula|HMView|Go!Zilla|Go-Ahead-Got-It) 1;
  ~*(rafula|HMView|HTTrack|Stripper|Sucker|Indy|InterGET|Ninja|JetCar|Spider|larbin|LeechFTP|Downloader|tool|Navroad|NearSite|NetAnts|tAkeOut|WWWOFFLE) 1;
  ~*(GrabNet|NetSpider|Vampire|NetZIP|Octopus|Offline|PageGrabber|Foto|pavuk|pcBrowser|RealDownload|ReGet|SiteSnagger|SmartDownload|SuperBot|WebSpider) 1;
  ~*(Teleport|VoidEYE|Collector|WebAuto|WebCopier|WebFetch|WebGo|WebLeacher|WebReaper|WebSauger|eXtractor|Quester|WebZIP|Wget|Widow|Zeus) 1;
  ~*(Twengabot|htmlparser|libwww|Python|perl|urllib|scan|Curl|email|PycURL|Pyth|PyQ|WebCollector|WebCopy|webcraw) 1;
}
```

Add the URL redirection inside of your server block:

```
server {
  # server_name, root, etc
  # ...
  location /faceless {
    try_files $uri $uri/ =404;
  }
  location / {
    set $face_matches 0;
    if (-f /faceless$request_filename) {
      set $face_matches 1$limit_bots;
    }
    location ~* \.(jpg|jpeg|png|gif)$ {
      if ($limit_bots = 11) {
        return 301 /faceless$request_uri;
      }
    }
    try_files $uri $uri/ =404;
  }
```

### Apache

* [Sample Apache configuration](sample/apache.conf)

First, make sure you have `mod_rewrite` enabled.

```
sudo a2enmod rewrite
```

Integrate the following code into the configuration for your domain name:

```
<Directory "/">
  RewriteEngine on
  RewriteCond %{REQUEST_URI} !^/faceless/
  RewriteCond %{HTTP_USER_AGENT} googlebot|yahoobot|microsoftbot [NC]
  RewriteRule (\.jpg|\.jpeg|\.gif|\.png)$ /faceless%{REQUEST_URI} [L,R=301]
</Directory>
```

### Sources

Our list of crawlers is built from the [monperrus/crawler-user-agents](https://github.com/monperrus/crawler-user-agents/).


## Prototype Ideas

- explore using adversarial modifications to face image using *fawkes* style negative-face interpolation
- explore using adversarial noise into facial region
- explore using face resolution degradation techniques to simply lower the amount of unique information in a face while still presenting the same image to bots and users
- develop benchmarking scripts to analyze amount of biometric information on a website

## Known Issues

- Using `if` statements in NGINX is not allowed. Can't use `if` with sub_filter.
- Referrer and user-agent can and will be easily spoofed
- Google indexes the URL to the non-redacted image and does not seem to follow the 301 redirect. This exposes the unredacted image.
- On Firefox Ubuntu, Firefox sends referrer `facetest.vframe.io` which reveals the unredacted image, but not on MacOS