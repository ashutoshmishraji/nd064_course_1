import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys
import sqlite3


# Total amount of connections to the database
total_connections=0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global total_connections
    try:
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        total_connections+=1
        return connection
    
    except :
        raise Exception("Database connection failure")
           

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('healthz request successful')

    return response

@app.route('/metrics')
def metrics():
    total_posts=0
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    total_posts=len(posts)
    connection.close()
    response = app.response_class(
            response=json.dumps({"db_connection_count": total_connections, "post_count":total_posts}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info("Metrics request successful")
    return response

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info("Index Page retrieved!")
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info("Article Not Found Page retrieved!") 
      return render_template('404.html'),404
    else:
      app.logger.info('{0} Article "{1}" retrieved!' .format(post['created'],post['title']) )  
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About Us Page retrieved!") 
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('New Article of Title "{0}" created!' .format(title)) 
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   
   ## stream logs to app.log file
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    
    handlers = [stderr_handler, stdout_handler]

    format_output = '%(levelname)s: %(name)-2s - [%(asctime)s] - %(message)s'
    logging.basicConfig(level=logging.DEBUG, handlers=handlers, format=format_output)
    app.run(host='0.0.0.0', port='3111')

  
