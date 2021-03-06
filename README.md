# Song map API
Description coming soon..

## Secrets
In order for project to work, you need to create a python file named **secrets.py**, which must contain these variables 
with your own values: <br>
    
    SECRET_KEY_HASH = ""
    DB_PASSWORD = ""
   
Generate your own SECRET_KEY_HASH with: 

    openssl rand -hex 32
    
Never push any secret values to the repository.


## Database requirements
- Postgre
- DB name must follow this: 

      postgresql://postgres:{DB_PASSWORD}@localhost/song_map_db
    
- DB must have PostGIS installed

