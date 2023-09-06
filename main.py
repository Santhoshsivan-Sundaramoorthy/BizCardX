import os
import re
import sqlite3
import easyocr
import pandas as pd
import streamlit as st
import ssl
import cv2
import matplotlib.pyplot as plt

ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(
    page_title="BizCardX",
    page_icon="id-card.png",
    layout="wide"
)


def extract_data(input_data, Card_Image):
    data = {
        "Name": [],
        "Designation": [],
        "Mobile": [],
        "Email": [],
        "Company": [],
        "Area": [],
        "City": [],
        "State": [],
        "Pincode": [],
        "Website": [],
        "Image": imagetoBinary(Card_Image)
    }
    for index, item in enumerate(input_data):
        if index == 0:
            data["Name"].append(item)
        elif index == 1:
            data["Designation"].append(item)
        elif "-" in item:
            data["Mobile"].append(item)
            if len(data["Mobile"]) == 2:
                data["Mobile"] = " & ".join(data["Mobile"])
        elif "@" in item:
            data["Email"].append(item)
        elif index == len(input_data) - 1:
            data["Company"].append(item)

        if re.findall('^[0-9].+, [a-zA-Z]+', item):
            data["Area"].append(item.split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+', item):
            data["Area"].append(item)
        match1 = re.findall('.+St , ([a-zA-Z]+).+', item)
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', item)
        match3 = re.findall('^[E].*', item)
        if match1:
            data["City"].append(match1[0])
        elif match2:
            data["City"].append(match2[0])
        elif match3:
            data["City"].append(match3[0])
        state_match = re.findall('[a-zA-Z]{9} +[0-9]', item)
        if state_match:
            data["State"].append(item[:9])
        elif re.findall('^[0-9].+, ([a-zA-Z]+);', item):
            data["State"].append(item.split()[-1])
        if len(data["State"]) == 2:
            data["State"].pop(0)
        if len(item) >= 6 and item.isdigit():
            data["Pincode"].append(item)
        elif re.findall('[a-zA-Z]{9} +[0-9]', item):
            data["Pincode"].append(item[10:])
        if "www " in item.lower() or "www." in item.lower():
            data["Website"].append(item)
        elif "WWW" in item:
            data["Website"] = input_data[4] + "." + input_data[5]

    df = pd.DataFrame(data)
    return df


def imagetoBinary(Image):
    # Convert image data to binary format
    with open(Image, 'rb') as file:
        binary_data = file.read()
    return binary_data


def runfetch():
    createTable = '''
    CREATE TABLE IF NOT EXISTS Card_Information (
    Name TEXT ,
    Designation TEXT,
    Mobile VARCHAR(50),
    Email TEXT,
    Company TEXT,
    Area TEXT,
    City TEXT,
    State TEXT,
    Pincode VARCHAR(10),
    Website TEXT,
    Image BLOB UNIQUE
    )
    '''
    mydb = sqlite3.connect('BizCardX.db')
    mycursor = mydb.cursor()
    mycursor.execute(createTable)
    mydb.commit()
    mydb.close()


def saveTheCard(uploaded_card):
    cardDirectory = os.path.join(os.getcwd(), "Uploaded_Cards")

    # Create the directory if it doesn't exist
    os.makedirs(cardDirectory, exist_ok=True)

    with open(os.path.join(cardDirectory, uploaded_card.name), "wb") as f:
        f.write(uploaded_card.getbuffer())
    st.write('Upload Successful')


def visualize_text_detection(image, detection_results):
    for (bounding_box, detected_text, confidence) in detection_results:
        # Unpack the bounding box
        (top_left, top_right, bottom_right, bottom_left) = bounding_box
        top_left = (int(top_left[0]), int(top_left[1]))
        top_right = (int(top_right[0]), int(top_right[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
        bottom_left = (int(bottom_left[0]), int(bottom_left[1]))

        # Draw a green rectangle around the detected text
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

        # Add text annotation above the bounding box
        cv2.putText(image, detected_text, (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Set the figure size for the plot
    plt.rcParams['figure.figsize'] = (15, 15)

    # Turn off axis labels and ticks
    plt.axis('off')

    # Display the modified image with annotations
    plt.imshow(image)


runfetch()

reader = easyocr.Reader(['en'])

conn = sqlite3.connect('BizCardX.db')
cursor = conn.cursor()
ca, cb, cc = st.columns(3)
ccc = st.columns(1)
st.write("----------------------------------------------------------------------------------------")
c1, c2, c3 = st.columns(3)

with cb:
    entered_heading = """
    <div class="xbox" data-char="X">
  X
  <div class="inside">BizCard</div>
  <div class="inside"></div>
  
</div>

<style>
.xbox {
  font-family: "Roboto", sans-serif;
  font-size: 100px;
  font-weight: bold;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -51%);
  text-shadow: 0px 0px 4px #009432;
  color: #22222a;
}
.xbox .inside {
  font-family: "Roboto", sans-serif;
  font-size: 50px;
  font-weight: bold;
  background-image: linear-gradient(180deg, #999999, #171717 100%);
  background-clip: text;
  -webkit-background-clip: text;
  text-fill-color: transparent;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow: none;
  top: 50%;
  left: 50%;
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 99;
}
.xbox:before {
  font-family: "Roboto", sans-serif;
  content: attr(data-char);
  font-size: 100px;
  font-weight: bold;
  position: absolute;
  text-shadow: 0px 0px 5px #00ff56;
  clip-path: polygon(
    0% 100%,
    0% 0%,
    100% 0%,
    100% 50%,
    50% 50%,
    100% 50%,
    100% 100%
  );
  animation-name: loading;
  animation-duration: 10s;
  animation-delay: -0.1s;
  animation-timing-function: cubic-bezier(0, 0.1, 0.9, 0.81);
  animation-direction: reverse;
  mix-blend-mode: color;
}
.xbox:after {
  font-family: "Roboto", sans-serif;
  content: attr(data-char);
  font-size: 100px;
  font-weight: bold;
  position: absolute;
  text-shadow: 0px 0px 5px black;
  clip-path: polygon(
    0% 100%,
    0% 0%,
    100% 0%,
    100% 50%,
    50% 50%,
    100% 50%,
    100% 100%
  );
  animation-name: loading;
  animation-duration: 10s;
  animation-timing-function: cubic-bezier(0, 0.1, 0.9, 0.81);
  animation-direction: reverse;
  mix-blend-mode: color;
  left: 0;
  top: 0;
}
@keyframes loading {
  0% {
    clip-path: polygon(
      0% 100%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      100% 50%,
      100% 100%
    );
  }
  12.5% {
    clip-path: polygon(
      0% 100%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      100% 100%,
      100% 100%
    );
  }
  25% {
    clip-path: polygon(
      0% 100%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      50% 100%,
      50% 100%
    );
  }
  37.5% {
    clip-path: polygon(
      0% 100%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      0% 100%,
      0% 100%
    );
  }
  50% {
    clip-path: polygon(
      0% 50%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      0% 50%,
      0% 50%
    );
  }
  62.5% {
    clip-path: polygon(0% 0%, 0% 0%, 100% 0%, 100% 50%, 50% 50%, 0% 0%, 0% 0%);
  }
  75% {
    clip-path: polygon(
      50% 0%,
      50% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      50% 0%,
      50% 0%
    );
  }
  87.5% {
    clip-path: polygon(
      100% 0%,
      100% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      100% 0%,
      100% 0%
    );
  }
  100% {
    clip-path: polygon(
      100% 50%,
      100% 50%,
      100% 50%,
      100% 50%,
      50% 50%,
      100% 50%,
      100% 50%
    );
  }
}
@keyframes loading2 {
  0% {
    clip-path: polygon(
      0% 100%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      100% 50%,
      100% 100%
    );
  }
  12.5% {
    clip-path: polygon(
      0% 100%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      100% 100%,
      100% 100%
    );
  }
  25% {
    clip-path: polygon(
      0% 100%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      50% 100%,
      50% 100%
    );
  }
  37.5% {
    clip-path: polygon(
      0% 100%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      0% 100%,
      0% 100%
    );
  }
  50% {
    clip-path: polygon(
      0% 50%,
      0% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      0% 50%,
      0% 50%
    );
  }
  62.5% {
    clip-path: polygon(0% 0%, 0% 0%, 100% 0%, 100% 50%, 50% 50%, 0% 0%, 0% 0%);
  }
  75% {
    clip-path: polygon(
      50% 0%,
      50% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      50% 0%,
      50% 0%
    );
  }
  87.5% {
    clip-path: polygon(
      100% 0%,
      100% 0%,
      100% 0%,
      100% 50%,
      50% 50%,
      100% 0%,
      100% 0%
    );
  }
  100% {
    clip-path: polygon(
      100% 50%,
      100% 50%,
      100% 50%,
      100% 50%,
      50% 50%,
      100% 50%,
      100% 50%
    );
  }
}

</style>
    """

    st.markdown(entered_heading, unsafe_allow_html=True)

with c1:
    st.write('Upload your file here')
    uploaded_Image = st.file_uploader("Upload here", label_visibility="collapsed", type=["png", "jpeg", "jpg"])

if uploaded_Image is not None:
    saveTheCard(uploaded_Image)

image_folder = os.path.join(os.getcwd(), "Uploaded_Cards")

if os.path.exists(image_folder):
    query = 'SELECT Name, Designation, Mobile, Email, Company, Area, City, State, Pincode, Website FROM Card_Information'
    cursor.execute(query)
    data = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    df = pd.DataFrame(data, columns=column_names)


    image_names = [filename for filename in os.listdir(image_folder) if filename.endswith((".png", ".jpg", ".jpeg"))]

    with c2:
        selected_image_name = st.selectbox("Select a card from the uploads", image_names)
    if selected_image_name:
        saved_Card = os.path.join(image_folder, selected_image_name)

        with c2:
            st.image(saved_Card, width=300)
            image = cv2.imread(saved_Card)
            result = reader.readtext(saved_Card)
            with c2:
                if st.button("Process Image"):
                    with st.spinner("Please wait processing image..."):
                        column1, column2 = st.columns(2)
                        with column1:
                            st.image(saved_Card)
                        with column2:
                            st.set_option('deprecation.showPyplotGlobalUse', False)
                            st.pyplot(visualize_text_detection(image, result))
                    result = reader.readtext(saved_Card, detail=0, paragraph=False)

                    extracted_data = extract_data(result, saved_Card)

                    command = '''INSERT OR REPLACE INTO Card_Information (Name, Designation, Mobile, Email, Company, Area, City,
                               State, Pincode, Website, Image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

                    for index, row in extracted_data.iterrows():
                        name = row['Name']
                        print(name)
                        designation = row['Designation']
                        mobile = row['Mobile']
                        email = row['Email']
                        company = row['Company']
                        area = row['Area']
                        city = row['City']
                        state = row['State']
                        pincode = row['Pincode']
                        website = row['Website']
                        image = row['Image']

                        cursor.execute(command, (
                            name, designation, mobile, email, company, area, city, state, pincode, website,
                            sqlite3.Binary(image)))
                    conn.commit()
                if st.button(":red[Delete Image]"):
                    os.remove(saved_Card)



cursor.execute("SELECT Name FROM Card_Information")
result = cursor.fetchall()
names = [row[0] for row in result]
with c3:
    selected_name = st.selectbox('Select the name:', names)
if selected_name:

    cursor.execute(
        "SELECT Name, Designation, Mobile, Email, Company, Area, City,State, Pincode, Website, Image FROM Card_Information WHERE Name = ?",
        (selected_name,))
    result = cursor.fetchone()
    with c3:
        st.markdown(
            """
            <div style="display: flex; justify-content: center; font-family: "Roboto", sans-serif;">
                <h3>Update/Delete the Database</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("Update the Database"):
            name = st.text_input('Name', result[0])
            designation = st.text_input('Designation', result[1])
            mobile = st.text_input('Mobile', result[2])
            email = st.text_input('Email', result[3])
            company = st.text_input('Company', result[4])
            area = st.text_input('Area', result[5])
            city = st.text_input('City', result[6])
            state = st.text_input('State', result[7])
            pincode = st.text_input('Pincode', result[8])
            website = st.text_input('Website', result[9])
            image = result[10]

            coll1, coll2 = st.columns([3, 1])
            with coll1:
                submitted = st.form_submit_button("Update")
                if submitted:
                    update_query = """
                            UPDATE Card_Information
                            SET
                                Name = ?,
                                Designation = ?,
                                Mobile = ?,
                                Email = ?,
                                Company = ?,
                                Area = ?,
                                City = ?,
                                State = ?,
                                Pincode = ?,
                                Website = ?
                            WHERE Image = ?
                            """
                    update_data = (
                        name,
                        designation,
                        mobile,
                        email,
                        company,
                        area,
                        city,
                        state,
                        pincode,
                        website,
                        image
                    )
                    cursor.execute(update_query, update_data)
                    conn.commit()

            with coll2:
                delete_button = st.form_submit_button(":red[Delete]")

                if delete_button:
                    delete_query = """
                        DELETE FROM Card_Information
                        WHERE Image = ?
                    """
                    cursor.execute(delete_query, (result[10],))

                    # Commit the changes and close the connection
                    conn.commit()
with ccc[0]:

    if os.path.exists(image_folder):
        query = 'SELECT Name, Designation, Mobile, Email, Company, Area, City, State, Pincode, Website FROM Card_Information'
        cursor.execute(query)
        data = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        df = pd.DataFrame(data, columns=column_names)


        css_style = """
        <style>
                                                           .centered table{
                                                               font-family: "Roboto", sans-serif;
                                                               border-collapse: separate;
                                                               style="display: flex; 
                                                               justify-content: center;
                                                               text-transform: capitalize;


                                                           }
                                                           .centered td{
                                                           font-family: "Roboto", sans-serif;
                                                               border: none;

                                                           }
                                                           .centered tr{
                                                           font-family: "Roboto", sans-serif;
                                                               border: none;
                                                               text-align: center;
                                                               text-transform: capitalize; 
                                                           }
                                                           .centered th {
                                                           font-family: "Roboto", sans-serif;
                                                               text-align: center;
                                                               background-color: #22222a;
                                                               text-transform: capitalize;
                                                               color: white;
                                                               border: none;
                                                           }
                                                           </style>


                                                           """
        st.markdown(css_style, unsafe_allow_html=True)

        html_table = df.to_html(index=False, escape=False, classes='centered', border=False)

        centered_html = f"""
        <div style="display: flex; flex-direction: column; align-items: center; text-align: center; font-family: "Roboto", sans-serif;">
    <h4>Data Stored in the Database</h4>
    {html_table}
</div>
        """

        # Display the HTML table with embedded images and "View Image" links
        st.write(centered_html, unsafe_allow_html=True)


