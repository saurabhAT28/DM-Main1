import streamlit as st
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from .Graph import Graph


def app(data):
    st.title('Assingment 8')

    def printf(url):
        st.markdown(
            f'<p style="color:#000;font:lucida;font-size:25px;">{url}</p>', unsafe_allow_html=True)

    options = ["BFS", "DFS", "Rank of Web Page", "HITS Algorithm"]
    operation = st.selectbox("Algorithms", options)

    # if operation!="BFS" and operation!="DFS":
    #     st.subheader("Dataset")
    #     st.write(data)

    def is_valid(url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def getLinks(url):
        reqs = None
        try:
            reqs = requests.get(url, timeout=5)
        except:
            return []

        urls = []
        if reqs:
            soup = BeautifulSoup(reqs.text, 'html.parser')

            for link in soup.find_all('a'):
                urls.append(link.get('href'))
        return urls

    if operation == "BFS":
        seedLink = st.text_input("Enter seed link")
        data = []
        que = []
        level = 0
        que.append(seedLink)
        dict = {}
        size = 0

        table = st.table(data=None)

        while (len(que)):
            size = len(que)
            while size:
                front = que.pop()
                if is_valid(front) and not front in dict.keys():
                    df = pd.DataFrame(data=[front], columns=["Links"])
                    table.add_rows(df)
                    data.append(front)
                    if level <= 3:
                        links = getLinks(front)
                        que.extend(links)
                    dict[front] = True
                size -= 1
            level += 1

    if operation == "DFS":
        seedLink = st.text_input("Enter seed link")
        dict = {}
        data = []
        table = st.table(data=None)

        def dfs(link, level):
            if level == 3 or not is_valid(link):
                return

            # print(link)
            df = pd.DataFrame(data=[link], columns=["Links"])
            table.add_rows(df)
            data.append(link)

            dict[link] = True

            links = getLinks(link)

            for i in links:
                if not i in dict.keys():
                    dfs(i, level+1)

        dfs(seedLink, 0)
        if len(data) > 0:
            df = pd.DataFrame(data=data, columns=["Links"])
            table = st.table(df)

    def init_graph(file):

        def split(line):
            str = ""
            flag = False
            for j in line:
                if not flag and j == '	':
                    str = str+','
                    flag = True
                else:
                    str = str+j
            return str.split(',')

        f = open(file.name)
        lines = f.readlines()

        graph = Graph()

        for line in lines:
            [parent, child] = split(line)

            graph.add_edge(parent, child)

            graph.sort_nodes()

        return graph

    if operation == "Rank of Web Page":
        file = data

        if file:

            def PageRank_one_iter(graph, d):
                node_list = graph.nodes
                # print(node_list)
                for node in node_list:
                    node.update_pagerank(d, len(graph.nodes))
                graph.normalize_pagerank()
                # print(graph.get_pagerank_list())
                # print()

            def PageRank(iteration, graph, d):
                for i in range(int(iteration)):
                    # print(i)
                    PageRank_one_iter(graph, d)

            iteration = 100
            damping_factor = 0.15

            graph = init_graph(file)

            nodes = graph.nodes

            PageRank(iteration, graph, damping_factor)

            ranks_by_nodes = []
            page_ranks = graph.get_pagerank_list()

            for i in range(len(nodes)):
                ranks_by_nodes.append([nodes[i].name, [child.name for child in nodes[i].children], [
                                      parent.name for parent in nodes[i].parents], page_ranks[i]])

            df = pd.DataFrame(ranks_by_nodes, columns=[
                              "Node", "Children", "parents", "Page Rank"])
            df = df.sort_values(by=["Page Rank", "Node"])
            table = st.table(df)

            st.write("Total page rank sum: " +
                     str(np.sum(graph.get_pagerank_list())))

    if operation == "HITS Algorithm":
        file = data
        if file:
            def HITS_one_iter(graph):
                node_list = graph.nodes

                for node in node_list:
                    node.update_auth()

                for node in node_list:
                    node.update_hub()

                graph.normalize_auth_hub()

            def HITS(graph, iteration=100):
                for i in range(iteration):
                    HITS_one_iter(graph)
                    # graph.display_hub_auth()
                    # print()

            iteration = 10

            graph = init_graph(file)

            HITS(graph, iteration)
            auth_list, hub_list = graph.get_auth_hub_list()

            nodes = [node.name for node in graph.nodes]

            my_data = []

            # print(hub_list)
            for i in range(len(nodes)):
                my_data.append([nodes[i], auth_list[i], hub_list[i]])

            df = pd.DataFrame(my_data, columns=[
                              "Node", "Auth Value", "Hub Value"])

            df = df.sort_values(["Auth Value", "Hub Value"])
            table = st.table(df)

            # print(sum(auth_list)," ",sum(hub_list))
