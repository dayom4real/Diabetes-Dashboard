import gspread
from dash import Dash, dcc, Output, Input, html  # pip install dash
import dash_bootstrap_components as dbc    # pip install dash-bootstrap-components
import plotly.express as px
import pandas as pd                        # pip install pandas
import numpy as np
#from flask import Flask, send_file
#import os
#from xhtml2pdf import pisa
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

service_account_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Check if the environment variable is set and contains valid JSON
if not service_account_key:
    raise ValueError("Google application credentials not set. Please set the 'GOOGLE_APPLICATION_CREDENTIALS' environment variable.")

# Parse the JSON string into a dictionary
credentials_info = json.loads(service_account_key)

# Use credentials_info to authenticate via gspread
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scopes)

# Authorize and open the Google Sheet
file = gspread.authorize(credentials)

workbook = file.open("Diabetes")
sheet = workbook.sheet1

df = pd.DataFrame(sheet.get_all_records())



def Age_Grouping(x):
  if (x >= 0 and x <= 25):
    return "Less than 25 Years"
  elif (x > 25 and x <= 50):
    return "26-50 Years"
  elif (x > 50 and x <= 75):
    return "51-75 Years"
  elif (x > 75):
    return "76 Years & Above"
df['Age Group'] = df['Age'].apply(Age_Grouping)

def BMI_Grouping(x):
  if (x >= 0 and x <= 18.5):
    return "Underweight"
  else:
    return "Overweight"
df['BMI Group'] = df['BMI'].apply(BMI_Grouping)


df['Outcome'] = df['Outcome'].astype('category')
df['Gender'] = df['Outcome'].astype('category')
dict1 = { 1: "Yes", 0: "No"}
dict2 = { 1: "Male", 0: "Female"}
df['Outcome'] = df['Outcome'].map(dict1)
df['Gender'] = df['Gender'].map(dict2)
  
#print(df.head())  
num_of_records = len(df)
average_Age = np.round(df["Age"].mean(),2)
average_Glucose = np.round(df["Glucose"].mean(),2)
#print(df.Gender.unique())

# def NFilter(x):
#  filtereddf = df[df["Age Group"] == x] if x else df
#  return len(filtereddf)



app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
#card_body_style = {"height": "200px"}
server = app.server
app.layout = dbc.Container([

dbc.Row([
dbc.Col(html.H1("DIABETES ANALYTICS & DASHBOARD"), width= 12, className= "text-center my-5")
]),

# Summary & Statistics

dbc.Row([
dbc.Col(html.Div(f"Total Patients: {num_of_records}", className= "text-left my-3 top-text"), width =4),
dbc.Col(html.Div(f"Average Age: {average_Age }", className= "text-center my-3 top-text"), width =4),
dbc.Col(html.Div(f"Average Glucose level: {average_Glucose }", className= "text-right my-3 top-text"), width =4)
], className= "mb-5"),


#Patient Demographics

dbc.Row([
  
 dbc.Col([
  dbc.Card([
   dbc.CardBody([
     html.H4("Patients Demographics: ", className= "card-title"),
     dcc.Dropdown(id= "gender_filter", options= [{"label": Gender, "value": Gender} for Gender in df["Gender"].unique()]
     , value= None, placeholder= "Filter by Gender"),
     dcc.Graph(id ="age-distibustion", className="graph-container")
  
   ])
  ])
], width = 6),


dbc.Col([
  dbc.Card([
   dbc.CardBody([
     html.H4("BMI Distribution: ", className= "card-title"),
      dcc.Dropdown(id= "gender_filter2", options= [{"label": Gender, "value": Gender} for Gender in df["Gender"].unique()]
     , value= None, placeholder= "Filter by Gender"),
     dcc.Graph(id ="BMI-distribution", className="graph-container")
  
   ])
  ])
], width = 6)




]),

#Insulin level by Age group
dbc.Row([
  dbc.Col([
    dbc.Card([
     dbc.CardBody([
      html.H4("Insulin Level Distribution: ", className= "card-title"),
      dcc.Dropdown(id= "gender_filter3", options= [{"label": Gender, "value": Gender} for Gender in df["Gender"].unique()], placeholder= "Filter by Gender"),
      dcc.Graph(id ="insulin-Age-group", className="graph-container")

     ]) 
    ])
  ], width = 12)
]),

#Blood Glucose Distibution
dbc.Row([
  dbc.Col([
    dbc.Card([
     dbc.CardBody([
      html.H4("Blood Glucose Distribution: ", className= "card-title"),
      dcc.Slider(id = "BG-Slider", 
                 min= df["Glucose"].min(),
                 max = df["Glucose"].max(),
                 value = df["Glucose"].median(),
                 marks = {int(i): f"{int(i):,}" for i in df["Glucose"].quantile([0.25, 0.50, 0.75, 1.0]).values},
                 step= 25
                 ),
      dcc.Dropdown(id= "gender_filter4", options= [{"label": Gender, "value": Gender} for Gender in df["Gender"].unique()], placeholder= 'Filter by Gender'),
      dcc.Graph(id = "BG-Distribution", className="graph-container")
    

     ]) 
    ])
  ], width = 12)
]),

#Pregnancies vs Outcome correlation


dbc.Row([
  dbc.Col([
    dbc.Card([
     dbc.CardBody([
      html.H4("Number of Pregnancies vs Diabetes Outcome: ", className= "card-title"),
      dcc.RadioItems(id = "chart-type", options= [{ "label":"Line Chart", "value": "Line" },{ "label":"Bar Chart", "value": "Bar" } ],
                     
                     value= "Line", inline= True, className= 'mb-4'),
     dcc.Dropdown(id = "Outcome-filter", options= [{"label": i, "value": i} for i in df["Outcome"].unique()]
     , value= None, placeholder= "Filter by Diabetes Outcome"),
      dcc.Graph(id = "Pregnancies-Outcome",  className="graph-container")

     ]) 
    ])
  ], width = 12)
]),

# dbc.Row([
#         dbc.Button("Download Dashboard as PDF", id="download-btn", color="primary", className="mt-3"),
#         dcc.Download(id="download")
#   ]),
# Footer
#html.Footer("Built with Dash and Plotly", className="footer")


], fluid= True)



# # PDF Export Functionality
# @app.server.route("/download_pdf")
# def download_pdf():
#     # Create HTML content for the PDF
#     html_content = f"""
#     <html>
#     <head>
#         <style>
#             body {{
#                 font-family: Arial, sans-serif;
#                 margin: 20px;
#                 padding: 0;
#                 font-size: 14px;
#             }}
#             h1 {{
#                 color: #ff5722;
#                 text-align: center;
#                 font-size: 24px;
#             }}
#             .highlight-card {{
#                 margin: 10px 0;
#                 padding: 10px;
#                 background-color: #ffecb3;
#                 border: 1px solid #ff5722;
#                 border-radius: 8px;
#                 font-weight: bold;
#             }}
#         </style>
#     </head>
#     <body>
#         <h1>Diabetes Analytics Dashboard</h1>
#         <div class="highlight-card">Total Patients: {len(df)}</div>
#         <div class="highlight-card">Average Age: {np.round(df['Age'].mean(), 2)}</div>
#         <div class="highlight-card">Average Glucose Level: {np.round(df['Glucose'].mean(), 2)}</div>
#     </body>
#     </html>
#     """

#     # Convert HTML to PDF
#     pdf_file = "dashboard.pdf"
#     with open(pdf_file, "w+b") as pdf:
#         pisa_status = pisa.CreatePDF(html_content, dest=pdf)
#         if pisa_status.err:
#             return f"Error generating PDF: {pisa_status.err}"

#     # Send the PDF file as a response
#     return send_file(pdf_file, as_attachment=True, download_name="dashboard.pdf")


# # Callback to trigger PDF download
# @app.callback(
#     Output("download", "data"),
#     Input("download-btn", "n_clicks"),
#     prevent_initial_call=True
# )
# def trigger_download(n_clicks):
#     if n_clicks:
#      return dcc.send_file("C:/Users/oludare.alatise/Desktop/2024/DR/Machine Learning/Web development") 





@app.callback(
  Output("age-distibustion", "figure"), 
  Input("gender_filter", "value")

)

def update_age_dist(selected_gender):
  if selected_gender:
    df_filtered = df[df["Gender"] == selected_gender]
  else:
   df_filtered = df
  if df_filtered.empty:
    return {}
  fig = px.histogram(df_filtered, x = "Age", nbins= 20, color= "Age Group",
      title= "Diabetes Patient Age Distibution")
  return fig

@app.callback(
  Output("BMI-distribution", "figure"), 
  Input("gender_filter2", "value")

)

def update_BMI_dist(selected_gender):
  if selected_gender:
    df_filtered = df[df["Gender"] == selected_gender]
  else:
   df_filtered = df
  if df_filtered.empty:
    return {}
  fig = px.histogram(df_filtered, x = "BMI", nbins= 20, color= "BMI Group",
      title= "BMI Distribution")
  return fig




@app.callback(
  Output("insulin-Age-group", "figure"), 
  Input("gender_filter3", "value")

)

def update_Insulin_dist(selected_gender):
    df_filtered = df[df["Gender"] == selected_gender] if selected_gender else df
    df_group = df_filtered.groupby("Age Group")["Insulin"].mean().reset_index(name = " Average Insulin")
    fig = px.bar(df_group, x = "Age Group", y = " Average Insulin", color= "Age Group", barmode = "group", title = "BMI Vs Age Group", category_orders={
        "Age Group": ["Less than 25 Years", "26-50 Years", "51-75 Years", "76 Years & Above"]
    }  ) 
    return fig





@app.callback(
  Output("BG-Distribution", "figure"), 
  Input("gender_filter4", "value"),
  Input("BG-Slider", "value"),


)

def update_BG_dist(selected_gender, Slider_Value):
    df_filtered = df[df["Gender"] == selected_gender] if selected_gender else df
    df_filtered = df_filtered[df_filtered["Glucose"] <= Slider_Value ]
    fig = px.histogram(df_filtered, x = "Glucose", nbins= 30, color= "Age Group",
      title= "Blood Glucose Distibution")
    return fig



@app.callback(
  Output("Pregnancies-Outcome", "figure"), 
  Input("chart-type", "value"),
  Input("Outcome-filter", "value"),


)

def update_BG_dist(selected_chart, Outcome_Value):
    df_filtered = df[df["Outcome"] == Outcome_Value] if Outcome_Value else df
    #df_group = df_filtered.groupby("Age Group").size().reset_index(name="count")
    df_group = df_filtered.groupby("Age Group")["Pregnancies"].mean().reset_index(name="Mean")

    if selected_chart == "Line":
     fig = px.line(df_group, x = "Age Group", y = "Mean", title = "Pregnancies Trend", category_orders={
        "Age Group": ["Less than 25 Years", "26-50 Years", "51-75 Years", "76 Years & Above"]
    } )
     #fig = px.line(df_filtered, x = "Age Group", y = "Pregnancies", title = "Pregnancies Trend")

    else:
     fig = px.bar(df_group, x = "Age Group", y = "Mean", title = "Pregnancies Trend", category_orders={
        "Age Group": ["Less than 25 Years", "26-50 Years", "51-75 Years", "76 Years & Above"]
    } )
     #fig = px.bar(df_filtered, x = "Age Group", y = "Pregnancies", title = "Pregnancies Trend")
    
    return fig



if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8080)

 
