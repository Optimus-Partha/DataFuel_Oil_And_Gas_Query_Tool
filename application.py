from flask import Flask, redirect, render_template, request, url_for
from utils import *


with open('.//static/Conversation.txt', 'w') as f:
    f.write('')

application = Flask(__name__)
list_of_question = []
conv_history = {'Question 1':'','Answer 1':''}
process_query_keywords = ["analytic", "process", "methodology","methodologys"]



@application.route("/", methods=("GET", "POST"))
def index():
    global graph_msg
    if request.method == "POST":
        query = request.form["query"]
        print(query)
        # openAI_API = request.form["openAI_API"]
        # os.environ['OPENAI_API_KEY'] = openAI_API

        query_type = query_classifire(query=query)
        print(query_type)
        # pattern = "|".join(process_query_keywords)
        # matches = re.findall(pattern.upper(), query.upper())
        # process query

        if query_type == "process query":
            process_query_result = metadat_search(query)
            result = process_query_result + \
                     " For more information please reffer to our methodology document at the following weblinkn: 'https://oilgas.globaldata.com/Methodology/Details."

        # data query
        elif query_type == 'data query':
            list_of_question.append(query)
            result,sql_query = llm_query(query=query,history=str(conv_history))

            conv_history["Question "+ str(len(list_of_question))] = query
            conv_history["Answer " + str(len(list_of_question))] = sql_query

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

        elif query_type == 'research query':
            result_defult = """Thank you for your query. Unfortunately, I am not able to possess the information which 
            required to address your question adequately. However, I would be happy to connect you with an experienced 
            analyst who can conduct the necessary research and provide you with the desired insights. """
            # mail_to_cs(str(query))
            print("Email sent successfully!")
            result = str(result_defult) \
                     + "Query send to Customer Success Team."


        else:
            result = "Thank you for your query. Unfortunately, I do not possess the information required to " \
                     "address your question adequately. Please connect with CS Team."

        with open('.//static/Conversation.txt', 'a') as f:
            f.write('User: '+ query + '\n')
            f.write("DataFuel: " + result + '\n\n')

        return redirect(url_for("index", result=result))

    result = request.args.get("result")
    return render_template("index.html", result=result)


if __name__ == '__main__':
    application.run(debug=False)

