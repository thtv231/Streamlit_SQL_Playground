import streamlit as st
import pandas as pd
import sqlite3
import tempfile

st.set_page_config(layout="wide")  # Bố cục toàn màn hình

# CSS để chiếm toàn màn hình
st.markdown("""
    <style>
        /* Xóa khoảng cách thừa */
        .css-18e3th9 {
            padding: 0 !important;
        }

        /* Tùy chỉnh phần chính (main container) */
        .css-1d391kg {
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Toàn màn hình */
        .main {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        h1 {
            font-size: 3rem;
            color: white;
        }
    </style>
    
""", unsafe_allow_html=True)

# Fxn Make Execution
def sql_executor(c, raw_code):
    c.execute(raw_code)
    data = c.fetchall()
    return data

# Lấy thông tin cột của bảng
def get_table_columns(c, table_name):
    c.execute(f"PRAGMA table_info({table_name});")
    columns = c.fetchall()
    return [column[1] for column in columns]  # Lấy tên cột từ kết quả

# Tạo giao diện
def main():
    st.title("SQL Playground")

    # Menu
    menu = ["Home", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home Page")

        # Tải file SQLite
        uploaded_file = st.file_uploader("Upload a SQLite file", type=["sqlite"])

        if uploaded_file is not None:
            # Tạo file tạm thời để lưu SQLite file đã tải lên
            with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name

            # Kết nối đến file SQLite đã lưu tạm thời
            conn = sqlite3.connect(tmp_file_path)
            c = conn.cursor()

            st.success("SQLite file loaded successfully")

            # Columns/Layout
            col1, col2 = st.columns(2)

            with col1:
                with st.form(key='query_form'):
                    raw_code = st.text_area("SQL Code Here")
                    submit_code = st.form_submit_button("Execute")

                # Table Info
                with st.expander("Table Info"):
                    try:
                        # Truy vấn tất cả các bảng
                        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        tables = c.fetchall()
                        
                        table_names = [table[0] for table in tables]

                        if table_names:
                            # Hiển thị thông tin bảng và các cột của bảng
                            table_info = {}
                            for table_name in table_names:
                                columns = get_table_columns(c, table_name)
                                table_info[table_name] = columns

                            # Hiển thị dưới dạng JSON
                            st.json(table_info)
                        else:
                            st.warning("No tables found in the database.")
                    except Exception as e:
                        st.error(f"Error fetching table names: {e}")
            
            # Results Layout
            with col2:
                if submit_code:
                    st.success('Query Submitted')
                    st.code(raw_code)

                    # Execute SQL query
                    try:
                        query_results = sql_executor(c, raw_code)
                        with st.expander("Results"):
                            st.write(query_results)

                        with st.expander("Pretty Table"):
                            # Lấy tên cột từ query_results (giả sử query_results là danh sách các bản ghi)
                            columns = [desc[0] for desc in c.description]  # Lấy tên cột từ mô tả của câu truy vấn SQL
                            query_df = pd.DataFrame(query_results, columns=columns)  # Tạo DataFrame với tên cột
                                # Hiển thị DataFrame
                            st.dataframe(query_df)
                    except Exception as e:
                        st.error(f"Error executing query: {e}")
        else:
            st.info("Please upload a SQLite file to get started.")

    else:
        st.subheader("About")
        st.write("This is a simple SQL Playground built with Streamlit.")

if __name__ == '__main__':
    main()
