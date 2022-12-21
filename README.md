# Brief
Create local mirror of Kaltura content using lowest bitrates and json metadata

# Usage
```
python3 local_mirror.py pid=### adminsecret=***** userid=YourUserID serviceurl=https://www.kaltura.com/
```

# Flow
Get list of media entries that were published to MediaSpace after the specified time

Loop over the entries

If an entry exists on the local file system, it is skipped

If it does not exist, download the lowest bitrate flavor for it, and generate a json file with the metadata.

# Kaltura API calls used

[session.start](https://developer.kaltura.com/api-docs/service/session/action/start)

[flavorAsset.list](https://developer.kaltura.com/api-docs/service/flavorAsset/action/list)

[flavorAsset.getUrl](https://developer.kaltura.com/api-docs/service/flavorAsset/action/getUrl)

[category.list](https://developer.kaltura.com/api-docs/service/category/action/list)

[media.list](https://developer.kaltura.com/api-docs/service/media/action/list)

