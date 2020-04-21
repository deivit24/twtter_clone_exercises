As I setup the project, I started playing around with the Web Application. I created an account started going through the each component.

Below are the bugs as stated in the assessment project files

PART 1

Bugs:

- bug 1. Fixing the logout - fix: I needed to do some research on the Flask's **g** object, `add_user_to_g` and `@app.before_request`. The I implemented the code

- bug 2. Fixing the User Profile (the location, bio and header_image) - fix: I had to call `{{user.bio}}`, `{{user.location}}`. as for the header_image, I had to implement it as a style on the html page :
  `<div`
  `id="warbler-hero"`
  ` style="background-image: url``````({{ user.header_image_url }}); background-size: cover;" `
  `class="full-width"`
  `></div>`

* bug 3. Fixing the bio cards on - fix: added the `{{user.bio}}` on the card div
* bug 4. Fixing Home Page - fix: I had to filter only the ids that the user is following. Researched the `_in` methond in sqlalchemy

I also added the global user to check if there is a user already in session when loggin in and singing up. For instance even do a user is logged in and the signup/login links are hidden, you can still paste it on to the url and make a request.

I handeled that by checking if there is already a user and if there is, it will redirect back to '/' and flash a message.

Part 2

Added likes. Took me about 3 to 4 hours to figure out the likes

Part 3 Testing:

Took me about a day to test models and view.
