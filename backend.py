import flask

import json
import os
import glob
import re
import bs4

tumbl_image_re = re.compile(r"https?://(\d+\.media|assets)\.tumblr\.com/.*")


def make_images(images_lst):
    imgs_str = []
    for img in images_lst:
        print(img)
        try:
            src = tumbl_image_re.search(img).group(0)
        except AttributeError:
            continue
        if src.endswith("pnj") or 'avatar_' in src or '_avatar' in src:
            continue
        else:
            imgs_str.append(f'<img class="img-responsive" src = "{src}">')
    return '\n'.join(imgs_str)



class Site(object):
    def __init__(self, path):
        self.path = path
        self.pages = glob.glob(os.path.join(self.path, 'page_*.json'))
        self.num_pages = len(self.pages)

        self.posts = []

        self.name = os.path.basename(path)
        self._last = None
        self._tags = None

    def __getitem__(self, key):
        try:
            return self.posts[key]
        except IndexError:
            self.load_next_page()
            return self[key]

    def __len__(self):
        return self.num_pages

    @property
    def tags(self):
        if self._tags is not None:
            return self._tags
        else:
            self._tags = {}
            for i in range(self.last):
                for t in self[i]['tags']:
                    try:
                        self._tags[t].append(i)
                    except KeyError:
                        self._tags[t] = [i]
            return self.tags

    @property
    def last(self):
        if self._last:
            return self._last
        else:
            try:
                while True:
                    self.load_next_page()
            except IndexError:
                self._last = len(self.posts) - 1
            self.tags
            return self.last

    def quick_tags(self):
        if len(self) < 3 or self._tags is not None:
            return sorted(self.tags.items(), key = lambda x: len(x[1]), reverse=True)
        else:
            tg_lst = {}
            for i in range(30):
                for t in self[i]['tags']:
                    try:
                        tg_lst[t].append(i)
                    except KeyError:
                        tg_lst[t] = [i]
            return sorted(tg_lst.items(), key = lambda x: len(x[1]), reverse=True)

    def load_next_page(self):
        with open(self.pages.pop(0)) as f:
            for line in f:
                self.posts.append(json.loads(line))

    def make_tag_a_str(self, tag, count = None):
        if count is not None:
            return f'<a href="/{self.name}/tag/{tag}""> ({count}) {tag} </a>'
        else:
            return f'<a href="/{self.name}/tag/{tag}""> {tag} </a>'

    def make_tags(self, tags_lst):
        tags_str = []
        for tag in tags_lst:
            tags_str.append(

                self.make_tag_a_str(
                    tag,
                    count = len(self.tags[tag]),
                     ))
        return '</p>' + '</p> \n <p>'.join(tags_str) + '</p>'

    def render_post(self, num):
        page_dict = self[num]
        return flask.render_template(
                "post.html",
                name=self.name,
                content='\n'.join(page_dict['text']),
                imgs=make_images(page_dict['images']),
                notes = page_dict['notes'][0] if isinstance(page_dict['notes'], list) else page_dict['notes'],
                date = page_dict['date'][0] if isinstance(page_dict['date'], list) else page_dict['date'],
                tags = self.make_tags(page_dict['tags']),
                post_num = num,
                )

    def render_tag_post(self, tag, num):
        print(tag, num, self.tags[tag])

        return self.render_post(self.tags[tag][num -1])

    def render_tag_list(self):
        return flask.render_template(
                "tag_list.html",
                name=self.name,
                tags_list='\n'.join([self.make_tag_list_entry(t) for t, _  in sorted(self.tags.items(), key =lambda  x: len(x[1]), reverse = True)])
         )

    def make_tag_list_entry(self, t):
        return f"""<tr class="d-flex">
          <th style="width:10em" > {len(self.tags[t])} </th>
          <th style="width:30em">{self.make_tag_a_str(t)}</th>
          </tr>
          """

    def render_list(self):
         return flask.render_template(
                "list.html",
                name=self.name,
                posts_lst='\n'.join([self.make_list_entry(i) for i in range(self.last)])
         )

    def make_list_entry(self, i):
        entry = self[i]
        if len(entry['text']) > 0:
            snippet = bs4.BeautifulSoup(' '.join(entry['text']), 'lxml').text[:60]
        else:
            snippet = 'no text'
        post_url = f"/{self.name}/post/{i + 1}"
        return f"""<tr class="d-flex">
          <th style="width:5em" > {i + 1} </th>

          <th style="width:10em"><a href="{post_url}"> {entry['id']} </a></th>

          <th style="width:30em"><a href="{post_url}"> {snippet} </a></th>

          <th style="width:20em"> {', '.join([self.make_tag_a_str(t) for t in entry['tags']])} </th>
          </tr>
          """


class Sites_Manager(object):
    def __init__(self, sites_dir):

        self.sites_dir = sites_dir
        self.sites = { p.name : Site(p.path) for p in os.scandir(sites_dir) if p.is_dir()}
        print(sites_dir, self.sites)
        self.loaded_sites = {}

    def __getitem__(self, key):
        return self.sites[key]

    def render_sites_page(self):
        table = []
        for _, site in self.sites.items():
            table.append(self.make_site_cell(site))
        return flask.render_template(
            "index.html",
            sites_lst = '\n'.join(table)
            )

    def make_site_cell(self, site):
        return f""" <tr class="d-flex">
                    <td style="width:5em">{len(site)}</td>
                    <td ><a href="/{site.name}/">{site.name}</a></td>
                    <td >{', '.join([site.make_tag_a_str(t, count = len(c)) for t, c in site.quick_tags()[:20]])}</td>
                    </tr>
        """


