from flask import Flask, render_template, redirect, url_for
import requests
from bs4 import BeautifulSoup
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = Flask(__name__,static_url_path='/static', static_folder='static')

def homeFetch():
    response = requests.get('https://www.shemaroome.com/')
    soup = BeautifulSoup(response.text,features="html5lib")

    # fetches all slider images
    slider = soup.find_all("div",{"class": "masthead-card"})
    sliderImages = []
    for element in slider:
        tempImage = element.find("img")
        sliderImages.append(tempImage['src'])

    # fetches all catagories with images
    catagory = soup.find_all("div",{"class": "float-left w-100 slick-container slick-gap"})
    catagoryObject =[]
    for element in catagory:
        tempTitle = element.find("h2")
        if tempTitle != None:
            tempTitle = str(tempTitle).split(">")[1].split("<")[0]
            tempImages = element.find_all("a")
            tempImagesArr = []
            for image in tempImages:
                try:
                    imgLink = image.find("img")["src"]
                except:
                    imgLink = ""
                tempImagesArr.append([image["href"],imgLink])
            catagoryObject.append([tempTitle,tempImagesArr])
    return sliderImages,catagoryObject

def movieDetailFetch(title):
    response = requests.get('https://www.shemaroome.com/'+title)
    soup = BeautifulSoup(response.text,features="html5lib")
    pathList = []
    pathsContainer = soup.find("section",{"class": "main-content"})
    paths = pathsContainer.find("ul").find_all("li")
    for path in paths:
        if path.find("a"):
            pathList.append([path.find("a")["href"],path.text.strip()])

    title = soup.find("h1",{"class": "float-left w-100 app-color1 font-black margin-bottom-10 section-title2"}).text

    catagoriesArr = []

    catagories = soup.find_all("li",{"class":"float-left font-regular app-color5 app-color1"})
    for catagory in catagories:
        catagoriesArr.append(catagory.text.strip())

    movieDataArr = []

    Synopsis = soup.find_all("p",{"class":"float-left w-100 app-color1 font-regular"})
    for data in Synopsis:
        movieDataArr.append(data.text.strip())

    youMayLikeArr = []

    youMayLikeContainer = soup.find("div",{"class":"float-left w-100 app-slick-slider-container"})
    youMayLike = youMayLikeContainer.find_all("a")
    for data in youMayLike:
        youMayLikeArr.append([data["href"],data.find("img")["src"]])

    return {"pathList":pathList,"title":title,"catagoriesArr":catagoriesArr,"movieDataArr":movieDataArr,"youMayLikeArr":youMayLikeArr}

def showDetailFetch(title):
    response = requests.get('https://www.shemaroome.com/'+title)
    soup = BeautifulSoup(response.text,features="html5lib")

    pathsContainer = soup.find("section",{"class": "main-content"})
    paths = pathsContainer.find("ul").find_all("li")
    pathList = []
    for path in paths:
        if path.find("a"):
            pathList.append([path.find("a")["href"],path.text.strip()])

    title = soup.find("h1",{"class": "float-left w-100 app-color1 font-black margin-bottom-10 section-title2"}).text.strip()

    catagories = soup.find_all("li",{"class":"float-left font-regular app-color5"})
    catagoriesArr = []
    for catagory in catagories:
        catagoriesArr.append(catagory.text.strip())

    Synopsis = soup.find_all("p",{"class":"float-left w-100 app-color1 font-regular"})
    movieDataArr = []
    for data in Synopsis:
        movieDataArr.append(data.text.strip())

    episodeContainer = soup.find_all("div",{"class":"float-left w-100 app-slick-slider-container"})[0]
    episodes = episodeContainer.find_all("a")
    episodesArr = []
    for episode in episodes:
        episodesArr.append([episode["href"],episode.find("img")["src"]])

    youMayLikeContainer = soup.find_all("div",{"class":"float-left w-100 app-slick-slider-container"})[1]
    youMayLike = youMayLikeContainer.find_all("a")
    youMayLikeArr = []
    for data in youMayLike:
        youMayLikeArr.append([data["href"],data.find("img")["src"]])
    
    poster = soup.find("div",{"class":"player_section w-100 embed-responsive embed-responsive-16by9"}).find("img")["src"]
    return {"pathList":pathList,"title":title,"catagoriesArr":catagoriesArr,"movieDataArr":movieDataArr,"episodesArr":episodesArr,"youMayLikeArr":youMayLikeArr,"poster":poster}

def decryptLink(encrypted,key,type):
    key = b64decode(key)
    iv = b'0000000000000000'
    ct = b64decode(encrypted)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    link = pt.decode()
    tempUrl =  "https://d1fcqrzxghru70.cloudfront.net/"+link.split("cloudfront.net/")[1]
    response = requests.request("GET", tempUrl)
    tempArr = response.text.split("RESOLUTION=")
    tempArr.pop(0)
    tempUrl2 = '/'.join(tempUrl.split("/")[:-1])
    if type == "movie":
        resolutionLink = tempUrl2+"/"+tempArr[0].split("\n")[-2]
    else:
        resolutionLink = tempUrl2+"/"+tempArr[0].split("\n")[-2]
    return resolutionLink

def stremKeyAPI(catalog_id,content_id,item_category,content_definition):
    url = "https://www.shemaroome.com/users/user_all_lists"
    payload = 'catalog_id='+catalog_id+'&content_id='+content_id + \
        '&category='+item_category+'&content_def='+content_definition
    response = requests.request("POST", url, data=payload)
    try:
        return {"streamKey":response.json()['stream_key'],"key":response.json()['key'],"newPlayUrl":response.json()['new_play_url'],"ios_key":response.json()['ios_key'],"ios_play_url":response.json()['ios_play_url'],"subtitle":response.json()['subtitle']}
    except:
        return {"error":"There's an error in data."}

def pageLoderAPI(title):
    response = requests.request("GET", "https://www.shemaroome.com/"+title)
    soup = BeautifulSoup(response.text, features="html5lib")
    catalog_id = soup.find("input", {"id": "catalog_id"})['value']
    content_id = soup.find("input", {"id": "content_id"})['value']
    item_category = soup.find("input", {"id": "item_category"})['value']
    content_definition = soup.find("input", {"id": "content_definition"})['value']
    try:
        return {"catalog_id":catalog_id,"content_id":content_id,"item_category":item_category,"content_definition":content_definition}
    except:
        return {"error":"There's an error in URL."}

@app.route('/')
def home():
    sliderImages,catagoryObject = homeFetch()
    return render_template('home.html',sliderImages=sliderImages,catagoryObject=catagoryObject)

@app.route('/movies/<title>')
def movieDetail(title):
    try:
        dataObj = movieDetailFetch("movies/"+title)
        contentObj = pageLoderAPI("movies/"+title)
        keyData = stremKeyAPI(contentObj["catalog_id"],contentObj["content_id"],contentObj["item_category"],"AVOD")
        movieUrl = decryptLink(keyData["ios_play_url"],keyData["ios_key"],"movie")
        return render_template('detailMovie.html',dataObj=dataObj,movieUrl=movieUrl)
    except:
        return redirect(url_for('home'))

@app.route('/gujarati-plays/<title>')
def detailsGujaratiPlays(title):
    try:
        dataObj = movieDetailFetch("gujarati-plays/"+title)
        contentObj = pageLoderAPI("gujarati-plays/"+title)
        keyData = stremKeyAPI(contentObj["catalog_id"],contentObj["content_id"],contentObj["item_category"],"AVOD")
        movieUrl = decryptLink(keyData["ios_play_url"],keyData["ios_key"],"movie")
        return render_template('detailsGujaratiPlays.html',dataObj=dataObj,movieUrl=movieUrl)
    except:
        return redirect(url_for('home'))

@app.route('/shows/<title>')
def detailShowHome(title):
    try:
        dataObj = showDetailFetch("shows/"+title)
        return render_template('detailShowHome.html',dataObj=dataObj)
    except:
        return redirect(url_for('home'))

@app.route('/shows/<title>/<episode>')
def detailShowEpisode(title,episode):
    try:
        dataObj = showDetailFetch("shows/"+title+"/"+episode)
        contentObj = pageLoderAPI("shows/"+title+"/"+episode)
        keyData = stremKeyAPI(contentObj["catalog_id"],contentObj["content_id"],contentObj["item_category"],"AVOD")
        movieUrl = decryptLink(keyData["ios_play_url"],keyData["ios_key"],"show")
        return render_template('detailShowEpisode.html',dataObj=dataObj,movieUrl=movieUrl)
    except:
        return redirect(url_for('home'))

app.run(host="0.0.0.0",port="8080",debug="true")