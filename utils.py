import sqlite3
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.sql_database import SQLDatabase
import os
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain import OpenAI, LLMChain, PromptTemplate
import pandas as pd
import matplotlib.pyplot as plt
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
import win32com.client as client
from langchain.cache import SQLiteCache
import langchain


server = 'field'
model = 'gpt-3.5-turbo'
# model = 'gpt-3.5-turbo-0301'
# database = 'field_data.db'
database = 'combined_data.db'
os.environ['OPENAI_API_KEY'] = "Your_API"

def csv_sqllite():
    # read the data from a CSV file
    df = pd.read_csv('Field_Data_All.csv',encoding= 'unicode_escape')

    # create a connection to the SQLite database
    conn = sqlite3.connect('field_data.db')

    # insert the data into the "field_data" table
    df.to_sql('field_data', conn, if_exists='replace', index=False)

    # commit the changes and close the connection
    conn.commit()
    conn.close()


classifier_prompt = """
Suppose you are a classifier model which understand the question and classify it into three different categories.

1. data query: where client is asking for some particular data.
Example: total number of producing fields in united states?, Top 10 producing wells in Permian basin?.

2. process query: Where client is asking for the methodology of any calculation or assumption or definition of 
any parameter or documentation link.
Example: How did you calculate fields production forecast?, where can I find block status in live site?, what is proppant?

3. research query: Client is asking for a reason for change in data or trend. 
Example: Why field production of 2021 is 50% less compared to 2022? 

Answer only the type of query('data query' or 'process query' or 'research query') client is asking without any explanation. 
Remember to double-check your answer for accuracy and completeness before providing the final results.
client question: {query}
Your Answer:  
"""


def query_classifire(query=""):
    prompt = PromptTemplate(input_variables=["query"], template=classifier_prompt)
    query_classifier = LLMChain(llm=OpenAI(temperature=0), prompt=prompt, verbose=True)
    query_type = query_classifier.predict(query=query)
    # print(query_type.lower())
    return query_type.lower()


def metadat_search(query=''):
    loader = TextLoader('static/metadata.txt')
    index = VectorstoreIndexCreator().from_loaders([loader])
    print(index.query(query))
    return index.query(query)


# SELECT sql FROM sqlite_master WHERE type='table' AND name='field_data';
custom_table_info = {
    "refinery": """CREATE TABLE "refinery" ("Refinery" TEXT,  "Country" TEXT,  "Constituent_Entity" TEXT,  "Region" TEXT,  "Status" TEXT,  "Start_Year" REAL,  "Decommissioning_Year" REAL,  "Refinery_Type" TEXT,  "Integrated_Non Integrated" TEXT,  "Operator" TEXT,  "Total_Capital_Expenditure_USD_mil" REAL,  "Project_Stage" TEXT,  "City" TEXT,  "Number_of_Units" REAL,  "Contractor" TEXT,  "Total_Refining_Capacity_mbd" INTEGER
    )"
    /*
    2 rows from refinery table:
    Refinery    Country	  Constituent_Entity
   1 Paraguana	Venezuela	Falcon
   2 Ulsan	    South Korea	Ulsan
   */""",
    "blocks": """CREATE TABLE "blocks" ("Block_ID" TEXT,  "Block_Name" TEXT,  "Operator" TEXT,  "Block_Terrain" TEXT,  "Block_Status" TEXT,  "Acreage_Sq_Km" REAL,  "Max_Water_Depth_ft" REAL,  "Associated_Field" TEXT,  "Bid_Round" TEXT,  "Ministry" TEXT,  "Block_License_Number" TEXT,  "License_Status" TEXT,  "License_Type" TEXT,  "Royalty_Rate" REAL,  "License_Effective_Date" TEXT,  "License_Expiry_Date" TEXT,  "Contractor" TEXT
    )"
    /*
    2 rows from blocks table:
    Block_ID	Block_Name
      1       00-00-064-03W4
      2       00-00-081-15W5
    */""",
    "wells": """ CREATE TABLE "wells" ("Well_Name" TEXT,  "Region" TEXT,  "Country" TEXT,  "Constituent_Entity" TEXT,  "Well_Terrain" TEXT,  "Well_Type" TEXT,  "Status" TEXT,  "Resource_Type" TEXT,  "Operator" TEXT,  "Spud_Date" TEXT,  "Completion_Date" TEXT,  "Discovery_Date" TEXT,  "Well_Direction" TEXT,  "Basin" TEXT,  "Formation" TEXT,  "Block_ID" TEXT,  "Block" TEXT,  "Well_License_Number" TEXT,  "Field_ID" REAL,  "Field" TEXT,  "Measured_Depth_ ft" REAL,  "True_Vertical_Depth_ft" REAL,  "Water_Depth_ft" REAL,  "Associated_Field_Reserves_boe" REAL,  "Well_Cost_USD_mil" REAL,  "Net_pay_thickness_ft" REAL
    )"
    /*
    2 rows from wells table:
    Well_Name	                               Region	               Country
    Zyuzeyevskoye West (Zapadno-Zyuzeyevskoye)	Former Soviet Union	    Russia
    Zyuzeyevskoye North (Severo-Zyuzeyevskoye)	Former Soviet Union	    Russia
    */""",
    "fields": """CREATE TABLE "fields" ("Field_ID" TEXT,  "Field_Name" TEXT,  "Region" TEXT,  "Country" TEXT,  "Constituent_Entity" TEXT,  "Field_Terrain" TEXT,  "Field_Status" TEXT,  "Resource_Type" TEXT,  "Basin" TEXT,  "Participants" TEXT,  "Operator" TEXT,  "Block" TEXT,  "License" TEXT,  "Recoverable_Reserves_boe" REAL,  "Remaining_Reserves_boe" REAL,  "Remaining_Crude_Oil_and_Condensate_Reserves_bbl" REAL,  "Recoverable_Crude_Oil_and_Condensate_Reserves_bbl" REAL,  "Remaining_Natural_Gas_Reserves_bcf" REAL,  "Recoverable_Natural_Gas_Reserves_bcf" REAL,  "1p_Reserves_boe" REAL,  "2p_Reserves_boe" REAL,  "3p_Reserves_boe" REAL,  "Oil_in_Place_bbl" REAL,  "Gas_in_Place_bcf" REAL,  "Gas_Oil_Ratio_mcf_per_bbl" REAL,  "Development_NPV_USD_mil" REAL,  "Remaining_NPV_USD_mil" REAL,  "Development_NPV_per_boe_USD" REAL,  "Remaining_NPV_per_boe_USD" REAL,  "IRR_Percentage" REAL,  "Development_Break_Even_Oil_Price_USD_per_bbl" REAL,  "Remaining_Break_Even_Oil_Price_USD_per_bbl" REAL,  "Development_Break_Even_Gas_Price_USD_per_mcf" REAL,  "Remaining_Break_Even_Gas_Price_USD_per_mcf" REAL,  "Payback_years" REAL,  "Capex_to_First_Production_USD_mil" REAL,  "Total_Capital_Expenditure_USD_mil" REAL,  "Total_Abandonment_Expenditure_USD_mil" REAL,  "Full_Cycle_Capex_per_boe_USD" REAL,  "Full_Cycle_Opex_per_boe_USD" REAL,  "Remaining_Opex_per_boe_USD" REAL,  "Remaining_Capex_per_boe_USD" REAL,  "Full_Cycle_Fiscal_Take_Percentage" REAL,  "Remaining_Fiscal_Take_Percentage" REAL,  "Development_Start_Year" REAL,  "Production_Start_Year" REAL,  "Production_End_Year" REAL,  "Development_Commerciality" TEXT,  "Production2010" REAL,  "Production2011" REAL,  "Production2012" REAL,  "Production2013" REAL,  "Production2014" REAL,  "Production2015" REAL,  "Production2016" REAL,  "Production2017" REAL,  "Production2018" REAL,  "Production2019" REAL,  "Production2020" REAL,  "Production2021" REAL,  "Production2022" REAL,  "Production2023" REAL,  "Production2024" REAL,  "Production2025" REAL,  "Production2026" REAL,  "Production2027" REAL,  "Production2028" REAL,  "Production2029" REAL,  "Production2030" REAL,  "Primary_Trap_Type" TEXT,  "Gravity" REAL,  "Sulphur_Content_Percentage" REAL,  "Hydrogen_Sulfide_Content_ppm" REAL,  "Carbon_Dioxide_Percentage" REAL,  "Facility_Type" TEXT,  "Formation" TEXT,  "Formation_Rock_Type" TEXT,  "Tertiary_Start_Year" REAL,  "Tertiary_Status" TEXT,  "Production_Phase" TEXT
    )"
    /*
    2 rows from fields table:
    Field_ID	Field_Name	Region
     1	        1103	    Oceania
     2	        113/01-A	Africa
    */"""
}

sql_query_prompt = """
You are a chatbot expert in converting text into SQLlite queries, your goal is to provide accurate and
efficient results without any additional comments or explanations.
You must have a strong understanding of SQL syntax and database structures to successfully complete this task.

Use previous conversation to construct new query: {history}

Given an input question, first create a syntactically correct query to run,ensure that your results are
relevant and useful. Remember to double-check your queries for accuracy and completeness before providing the final results.

Use the following format for result:

Question: "Question here"
SQLQuery: "SQL Query to run"

use tables {table_info}

Question: {input}
"""

db = SQLDatabase.from_uri("sqlite:///./static/" + database,
                          # include_tables=['field_data'],
                          include_tables=['fields', 'wells', 'blocks', 'refinery'],
                          sample_rows_in_table_info=2,
                          custom_table_info=custom_table_info
                          )
langchain.llm_cache = SQLiteCache(database_path="./static/" + database)
memory = ConversationBufferMemory(memory_key="chat_history")
memory.save_context({"input": "How many fields are producing?"},
                    {"ouput": "SELECT COUNT(*) FROM Field_Data WHERE Field_Status = 'Producing'"})


def llm_query(query='',history=''):
    prompt_1 = PromptTemplate(input_variables=["input", "table_info","history"], template=sql_query_prompt)
    print(prompt_1.format(input=query,table_info=['fields', 'wells', 'blocks', 'refinery'],history=history))
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


def graphs(sql_query="SELECT  Operator,COUNT(*) FROM field_data WHERE Country = 'United States' group by Operator limit 5",database=database):
    sql_query = """
    SELECT "Field_Name", "Remaining_Reserves_boe" 
    FROM "fields" 
    ORDER BY "Remaining_Reserves_boe" DESC 
    LIMIT 5
    """
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
    SELECT "Field_Name", "Remaining_Reserves_boe" 
FROM field_data 
ORDER BY "Remaining_Reserves_boe" DESC 
LIMIT 1
    
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(rows)
    cursor.close()
    conn.close()


def mail_to_cs(query=""):
    # Create an instance of the Outlook application
    outlook = client.Dispatch("Outlook.Application")

    # Create a new email message
    mail = outlook.CreateItem(0)

    # Set the recipient email address
    mail.To = "Sunil.Lanke@globaldata.com"

    # Set the email subject
    mail.Subject = "Analyst Attention Required to Resolve Client Query"

    # Set the email body
    mail.Body = \
        """Dear Customer Support Team,

I am writing to bring to your attention a question raised by one of our clients which requires the attention of one of our analysts to resolve. The client has reported an issue with their account and has requested that an analyst investigate and provide a resolution."

The details of the client query are as follows:

Client name: WF
Query type: [Research query]
Query description: {query}
As this issue requires the expertise of one of our analysts, I would appreciate it if you could escalate this to the relevant team member and ensure that the client is updated on the progress of their query.

Please let me know if you require any further information or if you have any questions regarding this matter.

Thank you for your attention to this matter.

Regards,
DataFuel""".format(query=query)
    # Set the attachment path (optional)
    # attachment = "C:/Users/User/Documents/test.txt"
    # mail.Attachments.Add(attachment)
    # Send the email
    mail.Send()


if __name__ == '__main__':
    # sqllite_connection_testing()
    # graphs()
    # metadat_search("what is proppent?")
    mail_to_cs("Why there is an change in wells production between 2021 and 2022?")
