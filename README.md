# MovCommender
#### Video Demo:  <URL https://youtu.be/psAxxOfCzxQ>
#### Description:
hello there, my name is Chakib El Basssam from croatia/Morocco i live in ireland and this is my cs50 final project, please watch the video and an read this: it took me 2 weeks to create it but i had to scrape it and remake it again which took about 1 week . the website it's self is created using python (Flask), HTML, css, JavaScript, jQuery, Ajax and some C (for a customer Library i needed in python), The way this website works internally is by using IMDB's API to get the data which then get filtered and cleaned up in the backend and stored in the website's local database and the reason for that is to minimize the use of IMDB's API because they only provide the user with 100 API calls a day which is low considering every time you press get another recommendation you lose 2 API calls, so the more people are using the site the more data will be available the site's local database and the less you'll need to use IMDb's API because someone else might of already choosed the same combination of choices as you did so the data has been already been called, processed and stored in site's database plus getting the data from the database rather than IMDb's API is extremely faster and more efficient. The website is also mobile friendly meaning it will work just fine on mobiles, and you can easily modify your data meaning you can easily change your username, email API key and password, the password itself is  encrypted so no one can access it except you, there is also a quick access bar at the top which has top genres, best of the best and title search. And finally you can easily delete your account or log out.


## Explanations about the files in this project:

1. flask session
    - It's a folder containing the user's session (coockies)


2. static
    - script.js
        - it's a file containing necessary scripts for the site to work like scripts for ordering and cleaning up data and scripts for the site's animations, i'm sorry it's a bit messy.

    - .css files
        - there are 3 css files each containing specific atributes for allot of elements.

    - titles.txt
        - it's a file containing bunch of content tiles to help the user search for content with autocomplete


3. templates
    - It's a folder containing the site's pages/templates and some of the templates contain scripts and css atributes for the site to work correctly


4. app.py
    - It's the main site's engine, it contains all the necessary scripts and functions for the site to work, it's messy in there so if you want to change something please read the things there carefully


5. helpers.py
    - It's file containing some components use by app.py


6. requirements.txt
    - please download the libraries in this file for the site to work


7. site_data.db
    - it's the site local database where every api call is stored (the data returned from the api), if deleted it can recreate it self so don't worry about accidentally deleting it. if you have a bug with site it's recommended to delete it.


8. users_data.db
    - it's the site local database where the users account are stored , if deleted it can recreate it self so don't worry about accidentally deleting it. if you have a bug with site it's recommended to delete it.

