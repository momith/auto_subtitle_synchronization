This (docker) service can be installed on your media server (emby, plex, ...). It will automatically synchronize the subtitle file with the video file. When downloading subtitles it can happen that there is an offset and aligning it manually takes some time. The service solves this issue by using https://github.com/kaegi/alass.
It expects that there is only one video file in the same folder as the subtitle file. Currently there is no automatic detection of a matching video file. It will take the first video file it finds.
It will output a modified version of the subtitle file with a suffix "_synced".

Setup:
- Install docker and docker-compose if not already installed
- Fill environment variables in the docker-compose.yml
- WATCH_FOLDERS shall be the directories where to recursively check for subtitle files for which no synchronization was done yet
- CHECK_INTERVAL the interval in which to check for new subtitle files
- Run docker-compose up -d to start the service
