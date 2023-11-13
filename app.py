from flask import Flask, request, render_template

from whoosh.qparser import *
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.analysis import STOP_WORDS

app = Flask(__name__)

@app.route("/")
def search_page():
    return render_template('start.html')

@app.route("/search")
def results_page():
    search_text = request.args.get('q')
    search_website = request.args.get('site')

    ix = open_dir("indexdir")
    with ix.searcher() as searcher:
        parser = QueryParser("link", ix.schema)
        parser.add_plugin(FuzzyTermPlugin())
        #remove the ability to specify phrase queries inside double quotes.
        parser.remove_plugin_class(PhrasePlugin)
        #Adds the ability to group arbitrary queries inside double quotes,
        #to produce a query matching the individual sub-queries in sequence.
        parser.add_plugin(SequencePlugin())

        search_words = search_text.split()
        search_words = ["*" + _ + "*" for _ in search_words if _ not in STOP_WORDS]
        if search_website:
            search_query = u'link:*'+search_website+u'* content:(' + u' OR '.join(search_words) + u')'
        else:
            search_query = u'content:(' + u' OR '.join(search_words) + u')'
        #return search_query
        query = parser.parse(search_query)
        results = searcher.search(query, limit = 20)
        
        return render_template('results.html', results=results)

        