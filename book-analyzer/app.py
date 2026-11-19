import html

from chalice import Chalice, NotFoundError, Response
from chalicelib.analyze import COLLECTION, DATABASE, analyze_book, connect
from chalice import Chalice

app = Chalice(app_name='book-analyzer')


@app.route('/')
def index():
    return {'hello': 'world'}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
import logging
from chalice import Chalice
from chalicelib.analyze import analyze_book

BUCKET = "public-sophiamosss-ds2022"

app = Chalice(app_name="book-analyzer")
logging.getLogger().setLevel(logging.INFO)


@app.on_s3_event(
    bucket=BUCKET,
    events=["s3:ObjectCreated:*"],
    suffix=".txt"
)
def analyze_new_book(event):
    """Analyze a book when it is uploaded to S3."""

    analyze_book(event.bucket, event.key)# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
# Lab 10: API routes
BOOK_FIELDS = {"runs": 0, "llm_analysis.at": 0}


@app.route("/")
def index():
    """Return the number of books in the collection."""
    client = connect()
    try:
        count = client[DATABASE][COLLECTION].count_documents({})
    finally:
        client.close()
    return {"books": count}


@app.route("/books")
def list_books():
    """Return books sorted by title, optionally filtered by author."""
    params = app.current_request.query_params or {}
    query = {}

    if "author" in params:
        query["author"] = params["author"]

    client = connect()
    try:
        books = client[DATABASE][COLLECTION]
        cursor = books.find(query, {"title": 1, "author": 1})
        result = list(cursor.sort("title", 1))
        return result
    finally:
        client.close()


@app.route("/books/{key}")
def get_book(key):
    """Return one book or a 404 if it doesn't exist."""
    client = connect()
    try:
        book = client[DATABASE][COLLECTION].find_one(
            {"_id": key},
            BOOK_FIELDS
        )
    finally:
        client.close()

    if book is None:
        raise NotFoundError(f"No book with key {key}")

    return book


@app.route("/page")
def page():
    """Display the book list as a web page."""
    rows = []
    for book in list_books():
        key = html.escape(book["_id"])
        title = html.escape(book.get("title", "(no title)"))
        author = html.escape(book.get("author", "(unknown author)"))
        rows.append(f'<li><a href="books/{key}">{title}</a> by {author}</li>')
    body = "<!doctype html><title>My books</title><h1>My books</h1><ul>" + "".join(rows) + "</ul>"
    return Response(body=body, status_code=200, headers={"Content-Type": "text/html"})
