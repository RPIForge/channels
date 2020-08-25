# channels
This repo holds the code for the RPI Forge's chat functionality. This is seperate than the main site to allow ease of seperation if we ever want to split up the two sites due to performance reasons.

## Development Requirements
The python requirements for this application can be installed by using the following two commands. Be aware you have to first install postgresql and the requirements for psycopg2.
```
pip3 install -r requirements.txt
```

This is based on Django 3.1 and Channels 2.4.0. It also uses a postgresql server located at 127.0.0.1 with the following credentials:
```
database: forge_devel_channels
username: postgres
password: password
```

It also requires a redis server running on port 6379. These credentials and addresses are for development only and not for production. To use the default values execute the following line:
```
sudo docker run -p 6379:6379  --name redis-channels -d redis
```

## Project Description
This project is built as a standalone chat feature for the RPI Forge website. While works very closely with the main site it is designed to be completely seperate from it. The two main reasons for this and the beginins are documented in the first section.

### Project Requirements
This projected required a secure and feature complete chat functionality for the RPI Forge website. This was to be implemented using django channels as it builds upon our already django focused code base within the organization. This lead to our second major requirement. The chat feature must be completely seperable from the main site. This is due to 2 reasons. The first is that django channels runs on ASGI backed with dafine running routing while django itself runs on WSGI thus not messing with our currently running WSGI server was important. The second reason is that chat servers in our expiernce can take a lot of resources thus it might be necisarry to offload the chat to a seperate instance if need be. Thus it needs to be easily spereable. This is represented by different postgres databases, interacting using rest end points only, and this site being displayed in iframes on the main site.

### Phase 1
This is the phase we are currently in. It is the first major push to make the site feature complete. This phases focus is chat reliability and functionality and not so much form. This is getting the site to be as reliable as can be because it does not matter how many functions or how pretty it looks if it just dont work. This also allows us to make a large amount of backend changes with out affecting the UX as we are ignoring it completely. 

### Phase 2
This phase is the final phase before release and will envolve a large front end rework. This is where we bring form to the site.
