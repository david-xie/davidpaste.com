#-*-coding:utf-8-*-

from models import *
from database import db_session
import Image,ImageDraw,ImageFont,os,string,random,ImageFilter,cStringIO

__all__ = ['getTags', 'getSyntaxList', 'updateTags', 'getCaptcha']

def getCaptcha():
    charactors = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string = ''
    size = (90, 22)
    for i in range(5):
        string += charactors[random.randint(0,61)]
    im = Image.new('RGB', size, (255,255,255))
    draw = ImageDraw.Draw(im)
    for i, s in enumerate(string):
        draw.text((10 + i * 15, random.randint(0, 4)), s, font=ImageFont.truetype('Monaco.ttf', 16), fill=(0,0,255))
    for x in range(size[0]):
        for y in range(size[1]):
            if random.randint(0, 50) > 48:
                draw.point((x,y), fill = (0,0,0))
    f = cStringIO.StringIO()
    im.save(f, 'GIF')
    f.seek(0)
    return [string, f]

def getTags():
    tags = db_session.query(Tag).all()[:10]
    return [tag.name for tag in tags]

def getSyntaxList():
    syntax = db_session.query(Syntax).order_by('name').all()
    return [(one.id, one.name) for one in syntax]

def updateTags(db_session, model, tags=[]):
    old_tags = [tag.name for tag in model.tags]
    tags_to_add = set(tags) - set(old_tags)
    tags_to_del = set(old_tags) - set(tags)
    if len(tags_to_add):
        for tag in tags_to_add:
            t = db_session.query(Tag).filter("LOWER(name)='%s'" % tag.strip().lower()).first()
            if not t:
                t = Tag(tag.strip("'\", ").lower().replace(",", '').replace("_", '-'))
            else:
                t.times = t.times + 1
            model.tags.append(t)
            db_session.add(model)
    for tag in tags_to_del:
        t = db_session.query(Tag).filter("LOWER(name)='%s'" % tag.strip().lower()).first()
        if t:
            model.tags.remove(t)
            t.times = t.times - 1
            db_session.add(model)
    if tags_to_add or tags_to_del:
        db_session.commit()
