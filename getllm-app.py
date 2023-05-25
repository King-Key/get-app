import streamlit as st

# 引入其他页面函数
from search_github_app import search_github
from search_arxiv_app import search_arxiv

# 设置页面标题
st.set_page_config(page_title='Streamlit App')

# 创建多页面应用程序
app_pages = {
    'GitHub': search_github,
    'Arxiv': search_arxiv
}

# 显示页面选择器
st.sidebar.write("搜索🔨")
st.sidebar.write("---")
page = st.sidebar.radio('选择页面', tuple(app_pages.keys()))

# 执行选择的页面
app_pages[page]()
