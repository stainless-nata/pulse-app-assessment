def makequery(query, filter={}):
    for q in query:
        filter[q]=query[q]
    return filter