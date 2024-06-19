from flask import Flask,render_template,request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pandas as pd
import pymongo

app = Flask(__name__)
@app.route('/',methods=['GET'])#display homepage
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['GET','POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:


            searchString=request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()

            flipkart_html = bs(flipkartPage, 'html.parser')

            try:
                bigboxes = flipkart_html.find(
                    "a", {"class": "CGtC98"}).get("href")
            except:
                return "No results found on site!"

            if len(bigboxes)==0:
                return "No results found on site!"

            productLink = "https://www.flipkart.com" + \
                          bigboxes

            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")

            print(prod_html)

            try:
                commentboxes = prod_html.find_all('div', {'class': "RcXBOT"})
            except:
                return "No reviews found on site!"

            if len(commentboxes)==0:
                return "No reviews found on site!"

            reviews = []


            for comment in commentboxes:
                try:
                    name=comment.find("p", {"class":"_2NsDsF AwS1CA"})
                    name=name.text
                except:
                    name="No name"

                try:
                    rating=comment.find("div", {"class":"XQDdHH Ga3i8K"})
                    rating=pd.to_numeric(rating.text)
                except:
                    rating="No rating"

                try:
                    heading=comment.find("p", {"class":"z9E0IG"})
                    heading=heading.text
                except:
                    heading="No heading"

                try:
                    commentc=comment.find("div", {"class":"ZmyHeo"})
                    commentc=commentc.text.replace("READ MORE","")
                    print(commentc)
                except:
                    commentc="No comment"

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": heading,
                          "Comment": commentc}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
        # return render_template('results.html')

    else:
        return render_template('index.html')


'''
            

    dbConn=pymongo.MongoClient('mongodb://localhost:27017')

    db=dbConn['reviewScrapper']
    reviews=db[searchString].find({})
    if reviews.count()>0:
        return render_template('results.html',reviews=reviews)
'''

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
    app.run()