import flask
import flask_assets

import argparse
import os
import os.path
import json

import backend

app = flask.Flask('app')

sites_container = None

assets = flask_assets.Environment(app)

css_bundle = flask_assets.Bundle('css/')
js_bundle = flask_assets.Bundle('js/')
assets.register('js_all', js_bundle)
assets.register('css_all', css_bundle)

@app.route("/<site>")
@app.route("/<site>/")
def post_redirect(site):
    return flask.redirect(f"/{site}/post/1")

@app.route("/<site>/post")
@app.route("/<site>/post/")
@app.route("/<site>/post/<pn>")
def post(site, pn = None):
    print(pn)
    if pn is None:
        pn = 1
    else:
        pn = int(pn)
    if pn < 1:
        return flask.redirect(f"/{site}/post/{sites_container[site].last}")
    try:
        return sites_container[site].render_post(pn)
    except IndexError:
        if pn != 1:
            return flask.redirect(f"/{site}/post/1")
        else:
            raise

@app.route("/<site>/tag/<tag>")
@app.route("/<site>/tag/<tag>/")
@app.route("/<site>/tag/<tag>/<pn>")
def tag_post(site, tag, pn = None):
    if pn is None:
        pn = 1
    else:
        pn = int(pn)
    print(site, tag, pn)
    tags_lst = sites_container[site].tags[tag]
    if pn < 1:
        return flask.redirect(f"/{site}/tag/{tag}/{max(len(tags_lst) - 1, 1)}")
    try:
        return sites_container[site].render_tag_post(tag, pn)
    except IndexError:
        if pn != 1:
            return flask.redirect(f"/{site}/tag/{tag}/1")
        else:
            raise

@app.route("/<site>/post_raw/<pn>")
def post_raw(site, pn):
    return flask.jsonify(sites_container[site][int(pn)])

@app.route("/<site>/list")
@app.route("/<site>/list/")
def site_list(site):
    return sites_container[site].render_list()

@app.route("/<site>/tag_list")
@app.route("/<site>/tag_list/")
def tag_list(site):
    return sites_container[site].render_tag_list()

@app.route("/")
#@app.route("/post")
def index():
    return sites_container.render_sites_page()
    return flask.render_template("index.html")
    return flask.redirect("/post/1")


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start the server', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--sites', default = 'sites/', help='port to run on')

    parser.add_argument('--port', default = 8805, help='port to run on')
    args = parser.parse_args()

    sites_container = backend.Sites_Manager(args.sites)

    app.run(host='0.0.0.0', debug=True, port=args.port)
