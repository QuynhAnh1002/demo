import streamlit as st
import pandas as pd
import numpy as np
import os
import pandas as pd
from collections import Counter
import io
#hello ive switched to branch tlam01


# from utils_frontend.openai_api import ask_question 

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Define the base data directory
data_dir = "../databases/private/neu-tctk-feather"

# Utility: recursively get .feather files in subfolders
def get_feather_files_by_subfolder(base_dir):
    feather_map = {}
    for subdir, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".feather"):
                full_path = os.path.join(subdir, f)
                relative_subdir = os.path.relpath(subdir, base_dir)
                label = os.path.join(relative_subdir, f)
                feather_map[label] = {
                    "path": full_path,
                    "subfolder": relative_subdir
                }
    return feather_map



# Set wide layout
st.set_page_config(page_title="Data Analysis App", layout="wide")

# App Title
st.title("GAIA Minerva")

# =================Main Tabs====================
# Create tabs
tab_ProjectManager, tab_DataWhisper, tab_AutoTuneML = st.tabs(["📁 Project Manager", "🧠 Data Whispering", "🎯 AutoTuneML"])

# Fill each tab with content
with tab_ProjectManager:
    st.header("Project Manager")
    st.write("Manage your projects, datasets, and workflows here.")


with tab_DataWhisper:
    st.header("Data Whisper")
    feather_files = get_feather_files_by_subfolder(data_dir)
    if not feather_files:
        st.warning("No .feather files found in any subfolder.")
    else:
        with st.container(border= True):
            # Extract available subfolders
            all_subfolders = sorted(set(info["subfolder"] for info in feather_files.values()))
            # Pill-style subfolder selection
            selected_subfolders = st.multiselect(
                "📂 **Select subfolders:**",
                options=all_subfolders,
                default=all_subfolders,
                format_func=lambda x: f"📁 {x}",
            )
            # Filter files by selected subfolders
            filtered_files = {
                label: info["path"]
                for label, info in feather_files.items()
                if info["subfolder"] in selected_subfolders
            }
            if not filtered_files:
                st.info("No datasets match the selected subfolders.")
            else:
                selected_file = st.selectbox("📑 **Select a dataset:**", list(filtered_files.keys()))  
                data_category = selected_file.split('/')[0]
                df = pd.read_feather(filtered_files[selected_file])
                st.success(f"✅ Loaded: {selected_file}")
                def process_neu_tctk(df, data_category):

                    def clean_column_names(columns):
                        # Replace NaN with placeholder and strip spaces
                        columns = [str(col).strip() if pd.notnull(col) else 'Unnamed' for col in columns]

                        # Add suffixes to duplicated columns
                        counts = Counter(columns)
                        seen = {}
                        new_cols = []
                        for col in columns:
                            if counts[col] > 1:
                                seen[col] = seen.get(col, 0) + 1
                                new_cols.append(f"{col}_{seen[col]}")
                            else:
                                new_cols.append(col)
                        return new_cols

                    if data_category in ['du-lich']:
                        df = df.iloc[1:, :]        # skip first row
                        df = df.iloc[:, 1:]        # remove first column
                        df = df.T                  # transpose
                        df.columns = df.iloc[0, :].astype(str).str.strip()  # new column names from first row
                        df = df.iloc[1:, :]        # remove the new header row
                        df.columns = clean_column_names(df.columns)  # clean duplicates and whitespace
                        df = df.reset_index(drop=True)
                        return df
                    elif data_category in ['chi-so-gia']:
                        df = df.iloc[1:, :]        # skip first row
                        #df = df.iloc[:, 1:]        # remove first column
                        df = df.T                  # transpose
                        df.columns = df.iloc[0, :].astype(str).str.strip()  # new column names from first row
                        df = df.iloc[1:, :]        # remove the new header row
                        df.columns = clean_column_names(df.columns)  # clean duplicates and whitespace
                        df = df.dropna(axis=1, how='all')  # ✅ This drops columns with all NaN

                        df = df.reset_index(drop=True)
                        return df

                    else:
                        df = df.dropna(how='all')    # drop rows where all values are NaN
                        df.columns = clean_column_names(df.columns)  # clean duplicates and whitespace
                        df = df.reset_index(drop=True)
                        return df

                with st.expander('**Original dataset**'):
                    #st.dataframe(df)
                    df = process_neu_tctk(df, data_category)
                    st.dataframe(df)

        # === KHỐI ĐÃ SỬA LỖI 'NĂM' ===
        with st.expander('📊 **Data Exploratory Analysis Dashboard**'):
            if 'df' in locals() or 'df' in globals():
                if df is not None and not df.empty:
                    
                    # Kiểm tra xem cột 'Năm' có tồn tại không
                    if 'Năm' in df.columns:
                        asset_cols = [col for col in df.columns if col != 'Năm']
                        fig = make_subplots(
                            rows=2, cols=2,
                            column_widths=[0.6, 0.4],
                            specs=[
                                [ {"type": "pie", "rowspan": 2}, {"type": "scatter"} ],
                                [ None,                        {"type": "box"} ]
                            ],
                            subplot_titles=(
                                "📊 Pie Chart",
                                "📈 Time Series",
                                "📦 Box Plots"
                            )
                        )

                        # --- 1. Pie Chart ---
                        total_sums = df[asset_cols].sum()
                        fig.add_trace(
                            go.Pie(
                                labels=total_sums.index,
                                values=total_sums.values,
                                name="Asset Share",
                                showlegend=False,
                                hole=0.1,
                                sort=False,
                                textinfo='label+percent',
                                textposition='inside',
                            ),
                            row=1, col=1
                        )

                        # --- 2. Time Series ---
                        for asset in asset_cols:
                            fig.add_trace(
                                go.Scatter(
                                    x=df['Năm'], # Dòng này sẽ an toàn vì đã được kiểm tra
                                    y=df[asset],
                                    mode='lines+markers',
                                    name=asset,
                                    showlegend=True
                                ),
                                row=1, col=2
                            )

                        # --- 3. Box Plots ---
                        for asset in asset_cols:
                            fig.add_trace(
                                go.Box(
                                    y=df[asset],
                                    name=asset,
                                    showlegend=False,
                                ),
                                row=2, col=2
                            )

                        fig.update_layout(
                            height=800,
                            margin=dict(t=60, b=30, l=30, r=30),
                            showlegend=True
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        # Nếu không có cột 'Năm', chỉ hiển thị cảnh báo
                        st.warning("⚠️ Bộ dữ liệu này không chứa cột 'Năm' nên không thể vẽ biểu đồ Time Series.")

                else:
                    st.warning("⚠️ DataFrame is empty.")
            else:
                st.error("❌ DataFrame `df` not found.")

    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display clickable sample questions
    with st.expander('**Sample Questions**'):
        sample_questions = [
            "Show me a summary of the dataset",
            "What are the correlations between numeric columns?",
            "Find outliers in the dataset",
            "Group by [column_name] and show mean values"
        ]
        # Use CSS to ensure uniform button size
        st.markdown(
            """
            <style>
            div.stButton > button {
                width: 100%;
                height: 60px;
                white-space: normal;
                font-size: 14px;
                padding: 10px;
                text-align: center;
                margin-bottom: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Create full-width buttons for each sample question
        for question in sample_questions:
            if st.button(question, key=question):
                # Store and display the sample question as a user message
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)

                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        # === THAY ĐỔI 2: Thay thế DataWhisper bằng lời gọi đến OpenAI ===
                        # Tạo một prompt chi tiết hơn cho AI
                        dataframe_head = df.head().to_string()
                        prompt_for_ai = f"""
                        Dựa vào 5 dòng đầu của dataframe sau:
                        {dataframe_head}

                        Hãy trả lời câu hỏi của người dùng: "{question}"
                        """
                        response = ask_question(prompt_for_ai) # Gọi hàm của OpenAI
                        
                        # Giữ nguyên phần hiển thị kết quả
                        if isinstance(response, pd.DataFrame):
                            st.dataframe(response, use_container_width=True)
                        elif isinstance(response, dict) and "plot" in response:
                            st.image(response.pop("plot"), use_column_width=True)
                            st.write(response)
                        else:
                            st.write(response)

                # Store assistant response
                st.session_state.messages.append({"role": "assistant", "content": response})

    # Display chat history
    with st.expander("Chat History"):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], (pd.DataFrame, dict)):
                    st.write(message["content"])
                else:
                    st.markdown(message["content"])

    # Input prompt from user
    prompt = st.chat_input("Ask about your data (e.g., summary, correlations, outliers)")

    if prompt:
        # Display and store user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Data Whispering..."):
                # === THAY ĐỔI 3: Thay thế DataWhisper bằng lời gọi đến OpenAI (lần 2) ===
                dataframe_head = df.head().to_string()
                prompt_for_ai = f"""
                Dựa vào 5 dòng đầu của dataframe sau:
                {dataframe_head}

                Hãy trả lời câu hỏi của người dùng: "{prompt}"
                """
                response = ask_question(prompt_for_ai) # Gọi hàm của OpenAI

                if isinstance(response, pd.DataFrame):
                    st.dataframe(response, use_container_width=True)
                elif isinstance(response, dict) and "plot" in response:
                    st.image(response.pop("plot"), use_column_width=True)
                    st.write(response)
                else:
                    st.write(response)

        # Store assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})

with tab_AutoTuneML:
    st.header("AutoTuneML")
    st.write("Run automated ML workflows with optimized tuning.")