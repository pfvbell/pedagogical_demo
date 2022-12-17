import streamlit as st
import openai as ai
import numpy as np
import pandas as pd
# import aspose.words as aw
from htmldocx import HtmlToDocx
from bing_image_downloader import downloader
import os
from PIL import Image
import base64
import os
import json
import pickle
import uuid
import re
import shutil
from streamlit_login_auth_ui.widgets import __login__
import requests

# Add sidebar stuff and on_submit button stuff.

# Config
MODEL = 'text-davinci-003'
ai.api_key = st.secrets["openai_api_key"]

# Helper function to call GPT
def generate_response(MODEL, PROMPT, MAX_TOKENS=750, TEMP=0.99, TOP_P=0.5, N=1, FREQ_PEN=0.3, PRES_PEN = 0.9):
  response = ai.Completion.create(
          engine = MODEL,
          # engine="text-davinci-002", # OpenAI has made four text completion engines available, named davinci, ada, babbage and curie. We are using davinci, which is the most capable of the four.
          prompt=PROMPT, # The text file we use as input (step 3)
          max_tokens=MAX_TOKENS, # how many maximum characters the text will consists of.
          temperature=TEMP,
          # temperature=int(temperature), # a number between 0 and 1 that determines how many creative risks the engine takes when generating text.,
          top_p=TOP_P, # an alternative way to control the originality and creativity of the generated text.
          n=N, # number of predictions to generate
          frequency_penalty=FREQ_PEN, # a number between 0 and 1. The higher this value the model will make a bigger effort in not repeating itself.
          presence_penalty=PRES_PEN # a number between 0 and 1. The higher this value the model will make a bigger effort in talking about new topics.
      )
  return response['choices'][0]['text']

def generate_image_response(IMG_PROMPT, SIZE):


__login__obj = __login__(auth_token = "courier_auth_token", 
                    company_name = "Shims",
                    width = 200, height = 250, 
                    logout_button_name = 'Logout', hide_menu_bool = False, 
                    hide_footer_bool = False, 
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN == True:
    

    ### TOP OF PAGE ###
    st.title("Automatic Worksheet Generator 🎈 (Beta)")
    st.markdown("## By Pedagogical 🧠")
    st.sidebar.markdown("# Automatic Worksheet Generator 🎈")
    st.sidebar.markdown("This worksheet generator was created using GPT-3. Please use it carefully and check any output before using it with learners as it could be biased or wrong.")
    st.sidebar.markdown("Please give us feedback by [completing this form](https://forms.gle/RpgWtdKJonN75Ga18), scheduling [a call with me](https://calendly.com/philipfvbell), emailing philipfvbell@gmail.com or tweeting @philipfvbell !!")
    st.sidebar.markdown("As a former teacher who found resource creation time-consuming I made this tool to help teachers quickly make resources that are differentiable to their classes and can be on quite specific topics. I hope it helps!")
    st.sidebar.markdown("[Here](https://docs.google.com/document/d/1rHJIG4ZkCzkZFTD3CHWSpKtKtzVsfyaSMo6SgQddfOc/edit) is a list of examples of great resources which have been made using this tool. If you have any examples to add please add them [here](https://forms.gle/TfLKWvsCxeKaLYxc9).")
    ### Content ### - Either User-generated or from OpenAI. Alternative is to get it from Wikipedia.
    st.markdown("### Title/ Topic of worksheet")
    title = st.text_input('Title and topic of worksheet. For example: "The impact of the Industrial Revolution on the climate", "How to write a Python list comprehension", "What happens during Electrolysis?" or "The use of metaphor in Shakespeare\'s The Tempest Act 1"')
    title = title.rstrip() # Remove trailing whitespace in order to prevent image download recursion error.
    st.markdown("### Content")
    # content = st.text_input('Add the text you want your students to learn here')
    # st.markdown(" OR ")
    st.text('The Worksheet will include a text for students to read which you can adapt:')
    content_topic = title #st.text_input('Add a topic to autogenerate reading text: e.g. "The Causes of The Korean War"')
    content_length = st.slider('Number of Words for text', 0, 400)
    reading_age = st.slider('Reading Age (These are approximate)', 0, 18)
    if reading_age ==0:
        st.error('Please choose a reading age')
    # Add how long it should take a student of that age to read the text and answer the qs.

    st.markdown("### Worksheet Configuration")
    st.text('Alongside the text you can also customise the worksheet')
    st.text('with scaffoling or activities below.')
    # q_type = st.radio('Questioning Type', ['Questions', 'Questions & Answers']) #, 'Cloze Exercise', 'Image tester'
    qs = st.checkbox('Questions about the text')
    answers = st.checkbox('Answers')
    key_words_definitions = st.checkbox('Key words with definitions')
    because_but_so = st.checkbox('Because, but, so writing exercise')
    #cloze = st.checkbox('Cloze Exercise') - GPT Prompt: Summarize text, remove key words and provide the key words to insert.
    thesaurus_paragraph_writing = st.checkbox('Paragraph Writing exercise based on alternative key words')
    # key_image_explanation = st.checkbox('Image explanation')
    # Make it colourful

    # if content and content_prompt:
    #   st.error('You need to choose between providing your own content or autogenerated content')
    worksheet_button = st.button('Generate Worksheet')
    if worksheet_button:
    ### Worksheet Options ###

        with st.spinner(text='Your worksheet is in the oven 🧠'):

            # st.markdown(f"# {title} ✍")
            components = []
            content_prompt = (f'Write {str(content_length)} words about ' + content_topic + ' so that a ' + str(reading_age) + ' year old could understand it.')
            content = generate_response(MODEL, content_prompt)
            
            if qs and answers:
                q_prompt = (f'write 5 questions and answers about the following text: {content}')
            else:
                q_prompt = (f'write 5 questions about the following text: {content}')
            q_and_or_a = generate_response(MODEL, q_prompt, MAX_TOKENS=250)
            q_and_or_a_list = q_and_or_a.splitlines()
            print(q_and_or_a_list)

            if key_words_definitions:
                key_words_prompt = (f'Extract key words from this text and provide definitions of the words not using words from the text itself: {content}')
                key_words = generate_response(MODEL, key_words_prompt, MAX_TOKENS=600)
            # st.text(key_words)
            if thesaurus_paragraph_writing:
                thesaurus_prompt = (f'Extract key words from this text and provide words with similar semantic meaning for each word: {content}')
                thesaurus_words = generate_response(MODEL, thesaurus_prompt, MAX_TOKENS=500)
                #Find the most important words used in connection with the American Civil War and explain what they mean
            # st.text(thesaurus_words)
            # st.text(content)

            # st.text(q_and_or_a)
            try:
                query_string = title
                downloader.download(query_string, limit=1,  output_dir='images', adult_filter_off=False, force_replace=False, timeout=60, verbose=True)
                # More options here: https://pypi.org/project/bing-image-downloader/

                ### Select word or PDF ###
                f = open('worksheet.html','w')

                # folder path
                dir_path = f'images/{query_string}'

                # list to store files
                res = []

                # Iterate directory
                for path in os.listdir(dir_path):
                    # check if current path is a file
                    if os.path.isfile(os.path.join(dir_path, path)):
                        res.append(path)
                print(res)

                image1 = Image.open(f'images/{query_string}/{res[0]}')
                image1 = image1.resize((80, 80))
                image1.save(f'images/{query_string}/{res[0]}')
            except Exception as e:
                print(e)
                st.text('No image found for this topic.')

            worksheet_head = f"""<html>
            <head>
            <style>
            </style>
            </head>
            <h1>{title}</h1>
            <body>
            <p>Name ......... </p>
            <p> <b> <br></b>
            <h2> Read the following text and underline any key words </h2>

            <p>{content}</p>"""
            if image1:
                image_component = f"""
                <img src="images/{query_string}/{res[0]}" alt="Image 1" style="float:left;width:15px;height:15px;"
                """
                components.append(image_component)


            if key_words_definitions:
                key_word_component = f"""<h3>Key Words</h3>
                <p>{key_words}</p>"""
                components.append(key_word_component)
            
            question_title =  f"""<h2> And now answer the following questions!</h2>
            <p> <b> <br></b>
            """
            components.append(question_title)
            #q_and_or_a_list = [question for question in q_and_or_a_list if '?' in question]
            q_and_or_a_list = q_and_or_a_list[2:] # Remove first two lines which are spaces
            question_component = [question + '<br> ................................................. </p>' for question in q_and_or_a_list]
            question_component = '<p>'.join(question_component)
            components.append(question_component)
            #✏️
            # 📖

            if because_but_so:
                because_but_so_component = """
                <h2> Because, But, So Writing Exercise </h2>
                <p> <b> Complete the following sentences! <br></b>
                1. Write a sentence about the text above using because <br>…………………………………………………………………<br>
                2. Write a sentence about the text above using but <br>…………………………………………………………………<br>
                3. Write a sentence about the text above using so <br>…………………………………………………………………<br>
                </p>
                """
                components.append(because_but_so_component)
            if thesaurus_paragraph_writing:
                thesaurus_paragraph_component = f"""<h2> Write a Paragraph about {content_topic} using these key words</h2>
                <p>{thesaurus_words}</p>"""
                components.append(thesaurus_paragraph_component)

            # qp = q_and_or_a#[question + '<br> ................................................. </p>' for question in q_and_or_a]
            # worksheet_questions = '<p>'.join(qp)

            worksheet_storyboard = """<p><b>Draw a picture of the text you have read below ... </b></p>
                    <svg width="400" height="180">
                    <rect x="50" y="20" width="300" height="150"
                    style="fill:blue;stroke:pink;stroke-width:5;fill-opacity:0.1;stroke-opacity:0.9" />
                    </svg>"""

            worksheet_end = """</body>
            </html>"""

            # Construct Worksheet from components
            full_worksheet = worksheet_head

            for component in components:
                if component:
                    full_worksheet += component

            full_worksheet += worksheet_end
            # full_worksheet = worksheet_head +  question_component + key_word_component + because_but_so_component +  thesaurus_paragraph_component + worksheet_end
            ##### ADD WORKSHEET TYPES #####
            # if ls_technique == 'Knowledge':
            #     full_worksheet = worksheet_head + worksheet_questions + worksheet_storyboard + worksheet_end
            # else: 
            #     full_worksheet = worksheet_head + worksheet_questions + worksheet_writing_rev + worksheet_end

            f.write(full_worksheet)
            f.close()

            new_parser = HtmlToDocx()
            new_parser.parse_html_file("worksheet.html", "worksheet")


            file_path = 'worksheet.docx'
            with open(file_path,"rb") as f:
                base64_word = base64.b64encode(f.read()).decode('utf-8')

            with open("worksheet.docx", "rb") as word_file:
                wordbyte = word_file.read()

            # Remove directory of images
            shutil.rmtree(dir_path) 

            downloaded = st.download_button(label="Download Word Document", 
            data=wordbyte,
            file_name="pedagogical_worksheet.docx",
            mime='application/octet-stream')

        
