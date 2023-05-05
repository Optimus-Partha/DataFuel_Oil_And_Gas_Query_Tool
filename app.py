import re
from flask import Flask, redirect, render_template, request, url_for
from utils import *


with open('.//static/Conversation.txt', 'w') as f:
    f.write('')

app = Flask(__name__)
list_of_question = []
conv_history = {'Qn:1':'','Ans:1':''}
process_query_keywords = ["analytic", "process", "methodology","methodologys"]


@app.route("/", methods=("GET", "POST"))
def index():
    global graph_msg
    if request.method == "POST":
        query = request.form["query"]
        pattern = "|".join(process_query_keywords)
        matches = re.findall(pattern.upper(), query.upper())
        # process query
        if matches !=[]:
            result = "Please reffer to our methodology document at the following weblinkn: 'https://oilgas.globaldata.com/Methodology/Details "
        # data query
        else:
            list_of_question.append(query)
            result,sql_query = llm_query(query=query,history=str(conv_history))

            conv_history["Qn:"+ str(len(list_of_question))] = query
            conv_history["Ans:" + str(len(list_of_question))] = sql_query

            # keep three latest conversation
            if len(conv_history) > 6:
                del conv_history[list(conv_history.keys())[0]]
                del conv_history[list(conv_history.keys())[0]]
            print(str(conv_history))

            try:
                graphs(sql_query=sql_query)
                graph_msg= " Graphs Available for this data."
                print("Graph has been created based on the data")
            except:
                graph_msg = ''
                pass
            result = result + graph_msg
        with open('.//static/Conversation.txt', 'a') as f:
            f.write('User: '+ query + '\n')
            f.write("DataFuel: " + result + '\n\n')

        return redirect(url_for("index", result=result))

    result = request.args.get("result")
    return render_template("index.html", result=result)


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')

