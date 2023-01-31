from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import csv

app = Flask(__name__)

#route to display the homepage
@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")


#route to show the reviews in the webpage
@app.route('/review',methods=['POST','GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkart_page, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class":"_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {"class":"_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, 'w', encoding='utf-8')
            headers = ["Product", "Name", "Rating", "CommentHead", "Comment"]
            writer = csv.DictWriter(fw, fieldnames=headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {"class":"_2sc7ZR _2V5EHH"})[0].text
                    name.encode(encoding='utf-8')

                except:
                    name = "No Name"

                try:
                    rating = commentbox.div.div.div.div.text
                    rating.encode(encoding='utf-8')

                except:
                    rating = "No Rating"

                try:
                    commentHead = commentbox.div.div.div.p.text
                    commentHead.encode(encoding='utf-8')

                except:
                    commentHead = "No Comment Heading"

                try:
                    comtag = commentbox.div.div.find_all('div', {"class":""})
                    custComment = comtag[0].div.text
                    custComment.encode(encoding='utf-8')

                except Exception as e:
                    print("Exception while creating dictionary: ", e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
                writer.writerow(mydict)


            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])

        except Exception as e:
            print("There is an excpetion,", e)
            return "Something is wrong"

    else:
        return render_template("index.html")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8001, debug=True)





