# kanoe

 Download entries from https://entries.gbcanoemarathon.co.uk/entries.

 1. Login.
 2. At top/right click on name and then "Newbucy CC Admin".

## App

Running the app:

```
flask --app kanoe run
```

During development you will want to run the app in debug mode:

```
flask --app kanoe --debug run
```

The app will be available on http://127.0.0.1:5000.

## Users

Followed these articles to setup user management:

- https://www.freecodecamp.org/news/how-to-authenticate-users-in-flask/
- https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
