from flask import Flask, request, render_template

from whoosh.qparser import *
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.analysis import STOP_WORDS

from database import create_connection, get_row
from page_ranking import rank_pages
import config

from spellchecker import SpellChecker

app = Flask(__name__)


@app.route("/")
def search_page():
    return render_template('start.html')

@app.route("/search")
def results_page():
    spell = SpellChecker()
    search_text = request.args.get('q')
    search_website = request.args.get('website')

    spell_checked_text = " ".join([spell.correction(word) if spell.correction(word) else word for word in search_text.split()])
    if spell_checked_text==search_text:
        is_spelling_correct = True
    else:
        is_spelling_correct = False


    ix = open_dir(config.idxdir)
    with ix.searcher() as searcher:
        parser = QueryParser("link", ix.schema)
        parser.add_plugin(FuzzyTermPlugin())
        #remove the ability to specify phrase queries inside double quotes.
        parser.remove_plugin_class(PhrasePlugin)
        #Adds the ability to group arbitrary queries inside double quotes,
        #to produce a query matching the individual sub-queries in sequence.
        parser.add_plugin(SequencePlugin())

        search_words = search_text.split()
        search_query = u'content:(' + u' OR '.join(search_words) + u')'
        #return search_query
        query = parser.parse(search_query)
        hits = searcher.search(query, limit = 20)
        id_list = '('+ ', '.join([str(result.get('id')) for result in hits])+')'
        connection = create_connection(config.database_file)
        if search_website:
            results = get_row(connection, 'sites', str(id_list), search_website)
        else:
            results = get_row(connection, 'sites', str(id_list))

        
        page_rankings = rank_pages(search_text, [result[-1] for result in results])
        page_rankings = [x/sum(page_rankings)*len(page_rankings) for x in page_rankings]

        title_rankings = rank_pages(search_text, [result[1] for result in results])
        title_rankings = [x/sum(title_rankings)*len(title_rankings) for x in title_rankings]

        page_rankings = [page_rankings[i]+title_rankings[i] for i in range(len(page_rankings))]

        results = [list(x) for _, x in sorted(zip(page_rankings, results))][::-1]
        hits = [x for _, x in sorted(zip(page_rankings, hits), key=lambda x: x[0])][::-1]

        for i in range(len(hits)):
            content = results[i][-1]
            hit = hits[i]
            results[i][-1] = hit.highlights("content", text=content)
        

        return render_template('results.html', results=results, is_spelling_correct=is_spelling_correct,
                                 spell_checked_text=spell_checked_text, website=search_website)

        