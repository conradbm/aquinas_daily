#
#
#
# AquinasApp
#
#
#
# Heroku API
#  https://aquinasapp.herokuapp.com/
#
# Deployment Instructions Here ...
# https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app
#
# Build reset
# # Revert changes to modified files.
# git reset --hard
# Remove all untracked files and directories. (`-f` is `force`, `-d` is `remove directories`)
# git clean -fd
#
# Operation scanner failure. Timeouts are a thing. 12/2/2020
# https://devcenter.heroku.com/articles/request-timeout
#
#
# Deployment steps
# 1. copy all your crap into the python folder
# 2. git add .
# 3. git commit -m "updates"
# 4. git push heroku main
# 5. heroku ps:scale web=1
# 6. heroku open


#AquinasApp
import flask
import dash
import time
import os
import json

from datetime import datetime as dt
import datetime

import dash_auth
#from dash import html
#from dash import dcc
#import dash_core_components as dcc
import dash_bootstrap_components as dbc
#import dash_html_components as html
from dash.dependencies import Input, Output, State

from layout.layout import *
from layout.layout import X, vectorizer, df_aquinas
from gensim.summarization import keywords




"""
print(aquinas_corpus[0])
{'volume': 'Volume 1', 
 'volumeKey': 'v1', 
 'questionTitle': 'Question 1. The nature and extent of sacred doctrine',
 'question': 'Question 1.',
 'questionKey': 'q1', 
 'articleTitle': 'Article 1. Whether, besides philosophy, any further doctrine is required?',
 'article': 'Article 1.',
 'articleKey': 'a1',
 'articleObjections': ['Objection 1. It seems that, besides philosophical science, we have no need of any further knowledge. For man should not seek to know what is above reason: "Seek not the things that are too high for thee" (Sirach 3:22). But whatever is not above reason is fully treated of in philosophical science. Therefore any other knowledge besides philosophical science is superfluous.', 'Objection 2. Further, knowledge can be concerned only with being, for nothing can be known, save what is true; and all that is, is true. But everything that is, is treated of in philosophical science—even God Himself; so that there is a part of philosophy called theology, or the divine science, as Aristotle has proved (Metaph. vi). Therefore, besides philosophical science, there is no need of any further knowledge.'],
 'articleBody': ['On the contrary, It is written (2 Timothy 3:16): "All Scripture, inspired of God is profitable to teach, to reprove, to correct, to instruct in justice." Now Scripture, inspired of God, is no part of philosophical science, which has been built up by human reason. Therefore it is useful that besides philosophical science, there should be other knowledge, i.e. inspired of God.', 'I answer that, It was necessary for man\'s salvation that there should be a knowledge revealed by God besides philosophical science built up by human reason. Firstly, indeed, because man is directed to God, as to an end that surpasses the grasp of his reason: "The eye hath not seen, O God, besides Thee, what things Thou hast prepared for them that wait for Thee" (Isaiah 64:4). But the end must first be known by men who are to direct their thoughts and actions to the end. Hence it was necessary for the salvation of man that certain truths which exceed human reason should be made known to him by divine revelation. Even as regards those truths about God which human reason could have discovered, it was necessary that man should be taught by a divine revelation; because the truth about God such as reason could discover, would only be known by a few, and that after a long time, and with the admixture of many errors. Whereas man\'s whole salvation, which is in God, depends upon the knowledge of this truth. Therefore, in order that the salvation of men might be brought about more fitly and more surely, it was necessary that they should be taught divine truths by divine revelation. It was therefore necessary that besides philosophical science built up by reason, there should be a sacred science learned through revelation.'],
 'articleReplyToObjections': ['Reply to Objection 1. Although those things which are beyond man\'s knowledge may not be sought for by man through his reason, nevertheless, once they are revealed by God, they must be accepted by faith. Hence the sacred text continues, "For many things are shown to thee above the understanding of man" (Sirach 3:25). And in this, the sacred science consists.', 'Reply to Objection 2. Sciences are differentiated according to the various means through which knowledge is obtained. For the astronomer and the physicist both may prove the same conclusion: that the earth, for instance, is round: the astronomer by means of mathematics (i.e. abstracting from matter), but the physicist by means of matter itself. Hence there is no reason why those things which may be learned from philosophical science, so far as they can be known by natural reason, may not also be taught us by another science so far as they fall within revelation. Hence theology included in sacred doctrine differs in kind from that theology which is part of philosophy.']}
"""


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
       {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
server = app.server
app.layout = html.Div([dcc.Location(id="url"), navbar, content])
app.title = 'AquinasApp'

# Handle navbar and paging
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    global mainPage
    global searchPage

    if pathname in ["/", "/browse"]:
        return mainPage
    elif pathname in ["/search"]:
        return searchPage
    elif pathname in ["/artifacts"]:
        return artifactsPage
    elif pathname in ["/contacts"]:
        return contactsPage
    
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# Capture Volume Dropdown to Update Questions
@app.callback(
    dash.dependencies.Output('question-dropdown','options'),
    [dash.dependencies.Input('volume-dropdown', 'value')])
def update_questions_output(volumeKey):
    try:
        # Get the matching questions for this volume selected
        filtered_questions_by_volume_shell = list(filter(lambda x : x["volumeKey"] == volumeKey, aquinas_shell))
        uniqueQuestions = getUniqueFromJSONList(filtered_questions_by_volume_shell, thing = "questions")
    except Exception as e:
        print("volume update error: {}".format(e))
        uniqueArticles= [{}, {}]
    #print("Unique Questions")
    #print(uniqueQuestions)
    #reset("q1", mode = "question")
    #reset("a1", mode = "article")
    return uniqueQuestions

# Capture Questions Dropdown to Update Articles
@app.callback(
    dash.dependencies.Output('article-dropdown','options'),
    [dash.dependencies.Input('volume-dropdown', 'value'), dash.dependencies.Input('question-dropdown', 'value')])
def update_articles_output(volumeKey, questionKey):
    try:
        # Get the matching articles for this volume and question selected
        filtered_articles_by_questions_and_volume_shell = list(filter(lambda x : x["volumeKey"] == volumeKey and x["questionKey"] == questionKey, aquinas_shell))
        uniqueArticles = getUniqueFromJSONList(filtered_articles_by_questions_and_volume_shell, thing = "articles")
    except Exception as e:
        print("question and volume update error: {}".format(e))
        uniqueArticles= [{}, {}]

    #print("Unique Articles")
    #print(uniqueArticles)
    
    #reset("a1", mode = "article")
    return uniqueArticles

def get_keywords_div_helper(objections, body, replyToObjections):
    kwds = keywords("\n".join(objections) +"\n" + "\n".join(body) +"\n"+ "\n".join(replyToObjections), ratio=0.2, lemmatize=True)
    ls_kwds = [i for i in kwds.split("\n") if not i in ["objection", "reply", "objections", "replies"]]
    top_ls_kwds = ls_kwds[:25]
    str_top_ls_kwds = ", ".join(top_ls_kwds)
    keywordsDiv = html.Div([
                    html.P("Keywords: {}.".format(str_top_ls_kwds))
                ],
                style={"color":"blue"})
    return keywordsDiv, top_ls_kwds

# Capture All Three- Volume/Question/Article to Populate Text
# Capture Questions Dropdown to Update Articles
@app.callback(
    dash.dependencies.Output('results-container','children'),
    [dash.dependencies.Input('volume-dropdown', 'value'), dash.dependencies.Input('question-dropdown', 'value'),  dash.dependencies.Input('article-dropdown', 'value')])
def update_articles_output(volumeKey, questionKey, articleKey):
    try:

        # Get the matching article
        matchingArticle = list(filter(lambda x : x["volumeKey"] == volumeKey and x["questionKey"] == questionKey and x["articleKey"] == articleKey, aquinas_corpus))[0]
        
        # Get important information from the hit
        responseList = []
        volumeTitle = matchingArticle["volume"] #string
        questionTitle = matchingArticle["questionTitle"] #string
        articleTitle = matchingArticle["articleTitle"] #string
        objections = matchingArticle["articleObjections"] #list
        body = matchingArticle["articleBody"] #string
        replyToObjections = matchingArticle["articleReplyToObjections"] #list

        # Keywords for the body
        keywordsDiv, mainSelectionKeywords = get_keywords_div_helper(objections, body, replyToObjections)

        # Begin building content for output
        responseList.append(html.H2(volumeTitle))
        responseList.append(html.H3(questionTitle))
        responseList.append(html.H3(articleTitle))
        responseList.append(html.Br())
        responseList.append(keywordsDiv)
        responseList.append(html.Br())
        responseList.append(html.H5("Objections..."))
        for obj in objections:
            responseList.append(html.P(obj))
        responseList.append(html.Br())
        responseList.append(html.H5("Body..."))
        for b in body:
            responseList.append(html.P(b))
        responseList.append(html.Br())
        responseList.append(html.H5("Reply To Objections..."))
        for reply in replyToObjections:
            responseList.append(html.P(reply))
        responseList.append(html.Br())

        responseList.append(html.H5("Related Articles..."))
        # Get recommendations:
        matchingSimilarities = list(filter(lambda x : x["volumeKey"] == volumeKey and x["questionKey"] == questionKey and x["articleKey"] == articleKey, aquinas_similarity))[0]
        ranks = matchingSimilarities["ranks"] #skip the fisrt one, with 100% similarity to itself.
        #print(ranks)
        hitsList = []
        allKeywords = set()
        for r in sorted(ranks, key = lambda x : x["rank"]):
            
            # Keys
            v = r["volumeKey"]
            q = r["questionKey"]
            a = r["articleKey"]
            
            # Matching article
            match = list(filter(lambda x : x["volumeKey"] == v and x["questionKey"] == q and x["articleKey"] == a, aquinas_corpus))[0]
            
            # Topics
            refKeywordsDiv,listOfKeywords = get_keywords_div_helper(match['articleObjections'], match['articleBody'], match['articleReplyToObjections'])
            relevant = any([i in mainSelectionKeywords for i in listOfKeywords])
            [allKeywords.add(i) for i in listOfKeywords if not i in mainSelectionKeywords ]

            # Display guts
            titleStuff = html.P("{}. {} {}".format(match["volume"], match["questionTitle"], match["articleTitle"]))

            hitsList.append(html.Div([titleStuff, refKeywordsDiv], style={"border":"2px black solid", "margin":"10px"}))
        
        #hitsGroup = dbc.ListGroup(hitsList)
        commonKeywordsDiv = html.Div([html.P("Related Keywords: "+", ".join([str(i) for i in list(allKeywords)[:25]]) + ".")], style={"color":"red"})
        hitsGroup = html.Div(hitsList)

        responseList.append(commonKeywordsDiv)
        responseList.append(hitsGroup)

        #print(aquinas_similarity[0])

        return html.Div(responseList)
    except Exception as e:
        print("matching error: {}".format(e))
        return html.Div([html.Br(), html.H1("No results found."), html.P("Please try a valid selection")])

# For the search page when I get to it
@app.callback(
    Output("search-results-container", "children"),
    Input("search-input", "value"),
)
def update_search_output(text, n=15):
    if not text is None:
        exampleVec = vectorizer.transform([text])
        mapping = X.dot(exampleVec.T).todense().flatten()
        topIndices = (-mapping).argsort()[:n]

        contents = []

        for _, i in enumerate(np.squeeze(np.asarray(topIndices))):

            kwds = keywords(df_aquinas.articleObjections.iloc[i] +"\n" + df_aquinas.articleBody.iloc[i] +"\n"+ df_aquinas.articleReplyToObjections.iloc[i], ratio=0.2, lemmatize=True)
            ls_kwds = [i for i in kwds.split("\n") if not i in ["objection", "reply", "objections", "replies"]]
            top_ls_kwds = ls_kwds[:25]
            str_top_ls_kwds = ", ".join(top_ls_kwds)
            contents.append( html.Div([
                    html.H3("{}".format(df_aquinas.volume.iloc[i])),
                    html.H3("{} ".format(df_aquinas.questionTitle.iloc[i])),
                    html.H3("{}".format(df_aquinas.articleTitle.iloc[i])),
                    html.Div([
                            html.P("Keywords: {}.".format(str_top_ls_kwds))
                        ],
                        style={"color":"blue"}),
                    html.H3("Objections ..."),
                    html.P(df_aquinas.articleObjections.iloc[i]),
                    html.H3("Article Body ..."),
                    html.P(df_aquinas.articleBody.iloc[i]),
                    html.H3("Reply To Objections ..."),
                    html.P(df_aquinas.articleReplyToObjections.iloc[i]),
                    html.Hr()
                ], style={}))

            if _ > n:
                break

        
        return html.Div(contents)
    else:
        return html.Div([])
        

@app.callback(Output("download-all-works", "data"), [Input("btn-download-all-works", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasReaderOnAristotle.docx"))

@app.callback(Output("download-ethic", "data"), [Input("btn-download-ethic", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Ethic.docx"))

@app.callback(Output("download-soul", "data"), [Input("btn-download-soul", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_De Anima.docx"))

@app.callback(Output("download-metaphysics", "data"), [Input("btn-download-metaphysics", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Metaph.docx"))

@app.callback(Output("download-physics", "data"), [Input("btn-download-physics", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Phys.docx"))

@app.callback(Output("download-rhetoric", "data"), [Input("btn-download-rhetoric", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Rhet.docx"))

@app.callback(Output("download-heavens", "data"), [Input("btn-download-heavens", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_De Caelo.docx"))

@app.callback(Output("download-politics", "data"), [Input("btn-download-politics", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Polit.docx"))

@app.callback(Output("download-generation", "data"), [Input("btn-download-generation", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_De Gener.docx"))


@app.callback(Output("download-topics", "data"), [Input("btn-download-topics", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Topic.docx"))


@app.callback(Output("download-posterior", "data"), [Input("btn-download-posterior", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Poster.docx"))


@app.callback(Output("download-causes", "data"), [Input("btn-download-causes", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_De Causis.docx"))

@app.callback(Output("download-categories", "data"), [Input("btn-download-categories", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Categor.docx"))


@app.callback(Output("download-interpretation", "data"), [Input("btn-download-interpretation", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Peri Herm.docx"))


@app.callback(Output("download-animals", "data"), [Input("btn-download-animals", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_De Gener. Animal..docx"))


@app.callback(Output("download-memory", "data"), [Input("btn-download-memory", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_De Memor. et Remin..docx"))

@app.callback(Output("download-prior", "data"), [Input("btn-download-prior", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_Prior. Anal.docx"))


@app.callback(Output("download-animalparts", "data"), [Input("btn-download-animalparts", "n_clicks")])
def func(n_clicks):
    if n_clicks > 0:
        return send_file(os.path.join("data", "AquinasOn_De Partib. Animal..docx"))



"""

    html.Button("Categories", id="btn-download-categories"), 
    Download(id="download-categories"),



    html.Button("On Interpretations", id="btn-download-interpretation"), 
    Download(id="download-interpretation"),


    html.Button("On Generation of Animals.", id="btn-download-animals"), 
    Download(id="download-animals"),


    html.Button("On Memory and Reminiscence", id="btn-download-memory"), 
    Download(id="download-memory"),


    html.Button("Prior Analytics", id="btn-download-prior"), 
    Download(id="download-prior"),
    
    html.Button("On the Parts of the Animals", id="btn-download-animalparts"), 
    Download(id="download-animalparts"),
"""
if __name__ == "__main__":
    app.run_server(debug=True)