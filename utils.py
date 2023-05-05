import sqlite3
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.sql_database import SQLDatabase
import os
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain import OpenAI, LLMChain, PromptTemplate
import pandas as pd
import matplotlib.pyplot as plt


server = 'field'
database = 'field_data.db'
model = 'gpt-3.5-turbo-0301'

os.environ['OPENAI_API_KEY'] = "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" # Tirath

custom_table_info = {
    "field_data": """CREATE TABLE field_data" (
  "Field_Name" TEXT,
  "Region" TEXT,
  "Country" TEXT,
  "Constituent_Entity" TEXT,
  "Field_Terrain" TEXT,
  "Field_Status" TEXT,
  "Resource_Type" TEXT,
  "Basin" TEXT,
  "Participants" TEXT,
  "Operator" TEXT,
  "Block" TEXT,
  "License" TEXT,
  "Recoverable_Reserves_boe" TEXT,
  "Remaining_Reserves_boe" TEXT,
  "Remaining_Crude_Oil_and_Condensate_Reserves_bbl" TEXT,
  "Recoverable_Crude_Oil_and_Condensate_Reserves_bbl" TEXT,
  "Remaining_Natural_Gas_Reserves_bcf" TEXT,
  "Recoverable_Natural_Gas_Reserves_bcf" TEXT,
  "Oil_in_Place_bbl" TEXT,
  "Gas_in_Place_bcf" TEXT,
  "Gas_Oil_Ratio_mcf_per_bbl" TEXT,
  "Development_NPV_US$_mil" TEXT,
  "Remaining_NPV_US$_mil" TEXT,
  "Development_NPV/boe_US$" TEXT,
  "Remaining_NPV/boe_US$" TEXT,
  "IRR_%" TEXT,
  "Development_Break-Even_Oil_Price_US$/bbl" REAL,
  "Remaining_Break-Even_Oil_Price_US$/bbl" REAL,
  "Development_Break-Even_Gas_Price_US$/mcf" REAL,
  "Remaining_Break-Even_Gas_Price_US$/mcf" REAL,
  "Payback_years" REAL,
  "Capex_to_First_Production_US$_mil" TEXT,
  "Total_Capital_Expenditure_US$_mil" TEXT,
  "Total_Abandonment_Expenditure_US$_mil" TEXT,
  "Full_Cycle_Capex/boe_US$" TEXT,
  "Full_Cycle_Opex/boe_US$" TEXT,
  "Remaining_Opex/boe_US$" TEXT,
  "Remaining_Capex/boe_US$" TEXT,
  "Full_Cycle_Fiscal_Take_%" TEXT,
  "Remaining_Fiscal_Take_%" TEXT,
  "Development_Start_Year" REAL,
  "Production_Start_Year" REAL,
  "Production_End_Year" REAL,
  "Development_Commerciality" TEXT,
  "Production2010" TEXT,
  "Production2011" TEXT,
  "Production2012" TEXT,
  "Production2013" TEXT,
  "Production2014" TEXT,
  "Production2015" TEXT,
  "Production2016" TEXT,
  "Production2017" TEXT,
  "Production2018" TEXT,
  "Production2019" TEXT,
  "Production2020" TEXT,
  "Production2021" TEXT,
  "Production2022" TEXT,
  "Production2023" TEXT,
  "Production2024" TEXT,
  "Production2025" TEXT,
  "Production2026" TEXT,
  "Production2027" TEXT,
  "Production2028" TEXT,
  "Production2029" TEXT,
  "Production2030" TEXT,
)"
/*
2 rows from field_data table:
Field_Name	Field_Status
1	Ghawar  Producing
2	Zuluf   Producing
*/"""
}


template_1 = """
You are a chatbot expert in converting text into SQLlite queries, your goal is to provide accurate and
efficient results without any additional comments or explanations.
You must have a strong understanding of SQL syntax and database structures to successfully complete this task.

Use previous conversation to answer new query: {history}

Given an input question, first create a syntactically correct query to run,ensure that your results are
relevant and useful. Remember to double-check your queries for accuracy and completeness before providing the final results.

Use the following format for result:

Question: "Question here"
SQLQuery: "SQL Query to run"

use tables {table_info}

Question: {input}
"""

template_2 = """
You are a chatbot expert in converting text into SQLlite queries, your goal is to provide accurate and
efficient results without any additional comments or explanations.


Use previous conversation answer new query: {chat_history}

Remember to double-check your queries for accuracy and completeness before providing the final results.

Use the following format for result:

Question: "Question here"
SQLQuery: "SQL Query to run"

Question: {input}
"""

db = SQLDatabase.from_uri("sqlite:///./static/" + database,
                          include_tables=['field_data'],
                          # include_tables=['Field_Data', 'Block_Data', 'Pipeline_Data', 'Refinery_Data','Wells_Data'],
                          sample_rows_in_table_info=2,
                          custom_table_info=custom_table_info
                          )
memory = ConversationBufferMemory(memory_key="chat_history")
memory.save_context({"input": "How many fields are producing?"},
                    {"ouput": "SELECT COUNT(*) FROM Field_Data WHERE Field_Status = 'Producing'"})


def llm_query(query='',history=''):
    prompt_1 = PromptTemplate(input_variables=["input", "table_info","history"], template=template_1)
    print(prompt_1.format(input=query,table_info='field_data',history=history))
    chain = SQLDatabaseChain(llm=ChatOpenAI(model_name=model, temperature=0),
                             # prompt=prompt_1,
                             database=db,
                             # memory=memory,
                             verbose=True,
                             return_direct=False,
                             return_intermediate_steps=True,
                             top_k=2)

    result = chain(prompt_1.format(input=query,table_info='field_data',history=history))
    return result.get('result').strip(), result.get('intermediate_steps')[0].strip()


def graphs(sql_query="SELECT  Operator,COUNT(*) FROM field_data WHERE Country = 'United States' group by Operator limit 5",database='field_data.db'):
    df = pd.read_sql(sql_query, con=sqlite3.connect("./static/" + database))
    # print(df)
    # print(df.iloc[:,0],df.iloc[:,1:])
    # Set the figure size
    fig, ax = plt.subplots(figsize=(16, 8))
    # Create a bar chart
    ax.bar(df.iloc[:, 0], df.iloc[:, 1].values,color=(54/255, 195/255, 255/255))
    ax.set_title('Bar Graph')
    ax.set_xlabel(df.columns[0])
    ax.set_ylabel(df.columns[1])
    plt.savefig('./static/' + 'bar_graph_line.png',dpi=300, bbox_inches='tight', pad_inches=0.2)
    # plt.show()


def sqllite_connection_testing():
    # Connect to an existing database file
    conn = sqlite3.connect('./static/field_data.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute a SELECT query
    query = """
    SELECT COUNT(DISTINCT Field_Name) AS "Producing Fields", COUNT(DISTINCT Well_Name) AS "Producing Wells"
    FROM Field_Data
    INNER JOIN Wells_Data ON Field_Data.Field_Name = Wells_Data.Field_Name
    WHERE Wells_Data.Operator = 'Exxon Mobil Corp' AND Field_Data.Field_Status = 'Producing'
    '"""
    cursor.execute(query)

    # Fetch the query results
    rows = cursor.fetchall()
    print(rows)

    # Print the results
    # for row in rows:
    #     print(row)

    # Close the cursor and database connection
    cursor.close()
    conn.close()


if __name__ == '__main__':
    # sqllite_connection_testing()
    graphs()
