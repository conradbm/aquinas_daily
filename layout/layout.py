# layout.py

from . import *

from dash_extensions import Download
from dash_extensions.snippets import send_file

with open(os.path.join("data","aquinas_new.json"), "rb") as handle:
    aquinas_corpus = json.load(handle)
with open(os.path.join("data","aquinas_shell.json"), "rb") as handle:
    aquinas_shell = json.load(handle)
with open(os.path.join("data","aquinas_similarity.json"), "rb") as handle:
    aquinas_similarity = json.load(handle)


df_aquinas = pd.DataFrame(aquinas_corpus)
df_aquinas.articleObjections = df_aquinas.articleObjections.apply(lambda x: "\n".join([i for i in ast.literal_eval(str(x))]))
df_aquinas.articleBody = df_aquinas.articleBody.apply(lambda x: "\n".join([i for i in ast.literal_eval(str(x))]))
df_aquinas.articleReplyToObjections = df_aquinas.articleReplyToObjections.apply(lambda x: "\n".join([i for i in ast.literal_eval(str(x))]))

"""
def searchText(query):
    flag = df_aquinas.articleBody.str.contains(query, case=False, flags=re.IGNORECASE, regex=True)
    aquinas_match = df_aquinas[flag]
    return aquinas_match
"""

from sklearn.feature_extraction.text import TfidfVectorizer
corpus = [x+"\n"+y for x,y in zip(df_aquinas.articleTitle.tolist(), df_aquinas.articleBody.tolist())]
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)

#print(len(corpus))
#print(df_aquinas.shape)
#print(vectorizer.get_feature_names())


# Simple search for exact match

#print(aquinas_corpus[0])
#print(aquinas_shell[0])


_defaultVolume = "v1"
_defaultQuestion = "q1"
_defaultArticle = "a1"

def reset(x, mode="volume"):
    if mode == "volume":
        _defaultVolume = x
    elif mode == "question":
        _defaultQuestion = x
    elif mode == "article":
        _defaultArticle = x 


def getUniqueFromJSONList(shell, thing = "volumes"):
    if thing == "volumes":
        res = [{"label": x[0], "value":x[1]} for x in dict(map(lambda x :(x["volume"], x["volumeKey"]), shell)).items()]
    elif thing == "questions":
        res = [{"label": x[0], "value":x[1]} for x in dict(map(lambda x :(x["questionTitle"], x["questionKey"]), shell)).items()]
    elif thing == "articles":
        res = [{"label": x[0], "value":x[1]} for x in dict(map(lambda x :(x["articleTitle"], x["articleKey"]), shell)).items()]
    return sorted(res, key = lambda x:int(x["value"][1:]))

uniqueVolumes = getUniqueFromJSONList(aquinas_shell, thing = "volumes")

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem"
}

navbar = dbc.NavbarSimple(
    className="text-white",
    children=[
        dbc.NavLink("Home", href="/browse", id="home-link", className="text-white", active=True),
        dbc.NavLink("Login", href="/login", id="login-link", className="bg-primary text-white rounded"),
        dbc.DropdownMenu(
            className = "text-white",
            children=[
                dbc.DropdownMenuItem("More services", header=True),
                dbc.DropdownMenuItem("Browse the Summa Theologica", href="/browse", id="browse-link"),
                dbc.DropdownMenuItem("Search the Summa Theologica", href="/search", id="search-link"),
                dbc.DropdownMenuItem("Aquinas On Aristotle", href="/artifacts", id="download-aristotle"),
                dbc.DropdownMenuItem("Contact Us", href="/contacts", id="contacts-link")
                #dbc.DropdownMenuItem("Technical Scanning", href="/scan", id="scan-link"),
                #dbc.DropdownMenuItem("Portfolio Allocation", href="/allocate", id="allocate-link"),
            ],
            nav=True,
            in_navbar=True,
            label="Services",
        ),
    ],
    brand="AquinasApp",
    brand_href="#",
    color="dark",
    dark=True,
)

mainPage = html.Div([
                        html.Br(),
                        html.H1("Browse the Summa Theologica"),
                        html.Br(),
                        # Drop down selector for Volume
                        html.P("Volume selection:"),
                        dcc.Dropdown(
                            id='volume-dropdown',
                            options=uniqueVolumes,
                            value=_defaultVolume
                        ),

                        # Drop down selector for Question
                        html.P("Question selection:"),
                        dcc.Dropdown(
                            id='question-dropdown',
                            value = _defaultQuestion
                        ),

                        # Drop down selector for Article
                        html.P("Article selection:"),
                        dcc.Dropdown(
                            id='article-dropdown',
                            value = _defaultArticle
                        ),
                            #style={'width': '20%', 'display': 'inline-block'}

                        # Container for returned response
                            # Return the formatted HTML, and
                            # the related articles
                        html.Br(),
                        html.Div(id = "results-container"),
                        html.Br()
                    ])

searchPage = html.Div([
    html.Br(),
    html.H1("Search the Summa Theologica"),
    html.Br(),
    dcc.Input(id="search-input", type="text", placeholder="What are the parts of the soul?", debounce=True, style = {"width":"100%"}),
    html.Br(),
    html.Br(),
    html.Div(id = "search-results-container"),
    html.Br()
])

artifactsPage = html.Div([
    html.Br(),
    html.H1("Aquinas On Aristotle"),
    html.Br(),
    html.P("""St. Thomas Aquinas is often referred to as one of the greatest commentators of Aristotle.
              The principle aim of this work is to make accessible only the sections that St. Thomas Summa' Theologica reference to 'Aristotle' or 'The Philosopher'. 
              The following documents are an arragement of all of these found in the Summa. 
              The first contains all references, each subordinate contains a specific book of interest. 
              The intent is to make St. Thomas the philosopher, in so far as he references Aristotle, more accessible for concentrated study."""),
    html.P("We hope you enjoy this study of Aristotle as he is depicted through the lens of St. Thomas."),
    html.Br(),
    html.Br(),
    html.Br(),

    html.Button("Aquinas On Aristotle (Complete References)", id="btn-download-all-works"), 
    Download(id="download-all-works"),
    html.Br(),
    html.Button("Ethics", id="btn-download-ethic"), 
    Download(id="download-ethic"),
    html.Br(),

    html.Button("On the Soul", id="btn-download-soul"), 
    Download(id="download-soul"),
    html.Br(),

    html.Button("Metaphysics", id="btn-download-metaphysics"), 
    Download(id="download-metaphysics"),
    html.Br(),

    html.Button("Physics", id="btn-download-physics"), 
    Download(id="download-physics"),
    html.Br(),

    html.Button("Rhetoric", id="btn-download-rhetoric"), 
    Download(id="download-rhetoric"),
    html.Br(),

    html.Button("On the Heavens", id="btn-download-heavens"), 
    Download(id="download-heavens"),
    html.Br(),

    html.Button("Politics", id="btn-download-politics"), 
    Download(id="download-politics"),
    html.Br(),

    html.Button("On Generation and Corruption", id="btn-download-generation"), 
    Download(id="download-generation"),
    html.Br(),

    html.Button("Topics", id="btn-download-topics"), 
    Download(id="download-topics"),
    html.Br(),

    html.Button("Posterior Analytics", id="btn-download-posterior"), 
    Download(id="download-posterior"),
    html.Br(),

    html.Button("On the Causes", id="btn-download-causes"), 
    Download(id="download-causes"),
    html.Br(),

    html.Button("Categories", id="btn-download-categories"), 
    Download(id="download-categories"),
    html.Br(),

    html.Button("On Interpretations", id="btn-download-interpretation"), 
    Download(id="download-interpretation"),
    html.Br(),

    html.Button("On Generation of Animals.", id="btn-download-animals"), 
    Download(id="download-animals"),
    html.Br(),

    html.Button("On Memory and Reminiscence", id="btn-download-memory"), 
    Download(id="download-memory"),
    html.Br(),

    html.Button("Prior Analytics", id="btn-download-prior"), 
    Download(id="download-prior"),
    html.Br(),

    html.Button("On the Parts of the Animals", id="btn-download-animalparts"), 
    Download(id="download-animalparts")
    
    

])

contactsPage = html.Div([
    html.Div([
        html.P("Author: Blake Conrad"), 
        html.P("Contact: blake.cs.ml@gmail.com")
        ],
        style={"margin":"10px", "align":"center"})
    ])

content = html.Div([mainPage,searchPage], id="page-content", style=CONTENT_STYLE)