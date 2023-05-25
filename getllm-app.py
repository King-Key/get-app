import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# 设置页面标题
st.set_page_config(page_title='多页面应用')

# 创建第一个页面
def search_github():
    st.title('GitHub 项目搜索')

    # 输入关键词
    keyword = st.text_input("输入关键词")
    count = st.number_input("输入数量", min_value=1, step=1)

    # 当用户点击“搜索”按钮时执行的函数
    if st.button('搜索'):
        # 使用GitHub API进行搜索
        url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc"
        response = requests.get(url).json()
        projects = response['items'][:count]

        for project in projects:
            st.subheader(project['name'])
            st.write(f"Star Count: {project['stargazers_count']}")
            st.write(f"Project Link: [{project['html_url']}]({project['html_url']})")
            st.write(f"Description: {project['description']}")
            st.write('---')


# 创建第二个页面
def search_arxiv():
    st.title('Arxiv 最新论文')

    def translate_english_to_chinese(text):
        model_name = "Helsinki-NLP/opus-mt-en-zh"  # 英文到中文的翻译模型
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        max_length = 4000  # 每个拆分的最大长度，根据模型的最大输入长度进行调整
        split_texts = [text[i:i+max_length] for i in range(0, len(text), max_length)]

        translated_texts = []
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        for split_text in split_texts:
            inputs = tokenizer.encode(split_text, return_tensors="pt", padding=True, truncation=True).to(device)
            outputs = model.generate(inputs)
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            translated_texts.append(translated_text)

        return ''.join(translated_texts)


    # 输入关键词
    keywords = st.text_input('输入关键词（用逗号分隔）')
    quantity = st.number_input('请输入要搜索的项目数量', min_value=1, step=1)


    if st.button('搜索'):
        st.write('正在搜索 Arxiv...')
        keyword_list = keywords.split(',')

        for keyword in keyword_list:
            st.subheader(f'关键词: {keyword}')
            today = datetime.date.today()
            url = f"https://arxiv.org/search/?query={keyword}&searchtype=all&abstracts=show&order=-announced_date_first&size=50"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            paper_list = soup.find_all('li', class_='arxiv-result')

            if len(paper_list) == 0:
                st.write('没有找到匹配的论文。')
            else:
                for i, paper in enumerate(paper_list):
                    title = paper.find('p', class_='title is-5 mathjax').text.strip()
                    authors = paper.find('p', class_='authors').text.strip()
                    abstract = paper.find('span', class_='abstract-full').text.strip()
                    published_date = paper.find("p", class_="is-size-7").text.strip()

                    if i < quantity:
                        st.write(f'### {i+1}. {title}')
                        st.write(f'{"".join(authors.split())}')
                        st.write(f'提交时间: {published_date}')
                        st.write(f'摘要: {abstract}')
                        abstract=translate_english_to_chinese(abstract)
                        st.write(f'中文翻译: {abstract}')
                            
                            
                        st.write('---')

# 创建多页面应用程序
app_pages = {
    'GitHub': search_github,
    'Arxiv': search_arxiv
}

# 显示页面选择器
#page = st.sidebar.selectbox('选择页面', tuple(app_pages.keys()))
st.sidebar.write("搜索🔨")
st.sidebar.write("---")
page = st.sidebar.radio('选择页面', tuple(app_pages.keys()))

# 执行选择的页面
app_pages[page]()
