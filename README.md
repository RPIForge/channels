# channels
This repo holds the code for the RPI Forge's chat functionality. This is seperate than the main site to allow ease of seperation if we ever want to split up the two sites due to performance reasons.

## requirements
This is based on Django 3.1 and Channels 2.4.0. It also uses a postgresql server located at 127.0.0.1 with the following credentials:

```
database: forge_devel_channels
username: postgres
password: password
```

It also requires a redis server running on port 6379. These credentials and addresses are for development only and not for production

## Notes
I will expand this documentation when I have the time. 
