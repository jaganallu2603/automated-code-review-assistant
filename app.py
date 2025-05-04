import streamlit as st
from langchain_google_genai import GoogleGenerativeAI
import os

# Custom CSS for a clean and professional look
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
            font-family: 'Arial', sans-serif;
        }
        .stTitle {
            color: #2c3e50;
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .stSidebar {
            background-color: #4DB6AC;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
        }
        .stTextArea textarea {
            background-color: #ffffff;
            color: #2c3e50;
            border-radius: 5px;
            padding: 10px;
            border: 1px solid #7b1fa2;
        }
        .stTextArea label {
            color: white;
            font-size: 1.2em;
            font-weight: bold;
        }
        .stButton > button {
            background-color: #3498db;
            color: white !important;
            font-size: 1.2em;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2980b9; 
            color: white !important; 
        }
        .stCodeBlock {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .stError {
            color: #e74c3c;
            font-size: 1.1em;
            margin-top: 10px;
        }
        .stHeader {
            color: #2c3e50;
            font-size: 1.8em;
            font-weight: bold;
            margin-top: 20px;
        }
        .stDownloadButton > button {
            background-color: #27ae60;
            color: white !important;
            font-size: 1.2em;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .stDownloadButton > button:hover {
            background-color: #219653;
            color: white !important; 
        }
    </style>
""", unsafe_allow_html=True)

# Set up the Streamlit app
st.markdown('<div class="stTitle">Automated code reviewer</div>', unsafe_allow_html=True)

GEMINI_API_KEY = ""  # Replace with your actual Gemini API key

# Sidebar for input options
with st.sidebar:
    st.markdown("### Input Options")
    input_method = st.radio(
        "Choose how to input your code:",
        ("Paste code directly", "Upload a file")
    )

# Initialize variables for code input
code_to_review = ""
uploaded_file_extension = ""

# Handle direct code paste
if input_method == "Paste code directly":
    code_input = st.text_area("Paste your code here:")
    if code_input:
        code_to_review = code_input

# Handle file upload
else:
    uploaded_file = st.file_uploader(
        "Upload your code file", 
        type=["txt", "py", "js", "java", "cpp", "html", "css", "php", "go", "rb", "ts"]
    )
    if uploaded_file:
        code_to_review = uploaded_file.read().decode("utf-8")
        uploaded_file_extension = uploaded_file.name.split('.')[-1]  # Get file extension

# Function to check if the input resembles code
def is_code(text):
    code_keywords = ["def ", "class ", "function ", "import ", "return ", "var ", "let ", "const ", "public ", "private "]
    return any(keyword in text for keyword in code_keywords)

# Button to trigger code review
if st.button("Review Code"):
    if not code_to_review:
        st.error("Please upload a file or paste code to review.")
    else:
        # Check if the input resembles code
        if not is_code(code_to_review):
            st.error("The input does not resemble code. Please upload a code file or paste valid code.")
        else:
            # Display the original code for reference
            st.markdown('<div class="stHeader">Original Code</div>', unsafe_allow_html=True)
            st.code(code_to_review, language="python")

            # Initialize the Gemini model with the API key
            model = GoogleGenerativeAI(api_key=GEMINI_API_KEY, model="gemini-pro")

            # Create a structured prompt for code review with clear instructions
            prompt = f"""
            Please review the following code and provide:
            1. **Suggestions**: At least three suggestions for improvement directly related to the provided code.
            2. **Bugs**: Any bugs or issues in the code (if none, say "No bugs found").
            3. **Improvements**: At least one general improvement for the code.
            4. **Updated Code**: Only provide the updated lines of code with the suggested improvements and explain the changes related to the code.

            Return the response in the following format:
            ### Suggestions
            - [Suggestion 1]
            - [Suggestion 2]
            - [Suggestion 3]

            ### Bugs
            - [Bug 1]
            - [Bug 2]

            ### Improvements
            - [Improvement 1]

            ### Updated Code
            
            [Updated lines here]
            ```

            ### Explanation
            - [Explanation of changes]

            Code:
            {code_to_review}
            """

            try:
                # Generate the response from the Gemini model
                response = model.generate([prompt])

                # Extract the text content from the LLMResult object
                if response and response.generations:
                    response_text = response.generations[0][0].text

                    # Display the results
                    st.markdown('<div class="stHeader">Code Review Results</div>', unsafe_allow_html=True)

                    # Parse the response into sections
                    sections = {
                        "Suggestions": [],
                        "Bugs": [],
                        "Improvements": [],
                        "Updated_Code": "",
                        "Explanation": []
                    }

                    current_section = None
                    for line in response_text.split("\n"):
                        line = line.strip()
                        if line.startswith("### Suggestions"):
                            current_section = "Suggestions"
                        elif line.startswith("### Bugs"):
                            current_section = "Bugs"
                        elif line.startswith("### Improvements"):
                            current_section = "Improvements"
                        elif line.startswith("### Updated Code"):
                            current_section = "Updated_Code"
                        elif line.startswith("### Explanation"):
                            current_section = "Explanation"
                        elif current_section and line:
                            if current_section == "Updated_Code":
                                sections[current_section] += line + "\n"
                            else:
                                sections[current_section].append(line)

                    # Display Suggestions
                    if sections["Suggestions"]:
                        st.markdown('<div class="stHeader">Suggestions</div>', unsafe_allow_html=True)
                        st.write("\n".join(sections["Suggestions"]))

                    # Display Bugs
                    if sections["Bugs"]:
                        st.markdown('<div class="stHeader">Bugs</div>', unsafe_allow_html=True)
                        st.write("\n".join(sections["Bugs"]))

                    # Display Improvements
                    if sections["Improvements"]:
                        st.markdown('<div class="stHeader">Improvements</div>', unsafe_allow_html=True)
                        st.write("\n".join(sections["Improvements"]))

                    # Display Updated Code (only the updated lines)
                    if sections["Updated_Code"]:
                        st.markdown('<div class="stHeader">Updated Code (Changes Only)</div>', unsafe_allow_html=True)
                        st.code(sections["Updated_Code"].strip(), language="python")

                    # Display Explanation
                    if sections["Explanation"]:
                        st.markdown('<div class="stHeader">Explanation of Changes</div>', unsafe_allow_html=True)
                        st.write("\n".join(sections["Explanation"]))

                    # Prepare the download button for the updated code
                    if sections["Updated_Code"]:
                        # Create the download link for the updated code with the correct file extension
                        updated_code = sections["Updated_Code"].strip()
                        st.download_button(
                            label="Download Updated Code",
                            data=updated_code,
                            file_name=f"reviewed_code.{uploaded_file_extension}",
                            mime=f"text/{uploaded_file_extension}"
                        )

                else:
                    st.error("No response from the Gemini API.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
