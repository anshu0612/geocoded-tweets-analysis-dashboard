import json
import collections as col
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib.cm as cm

# graph analysis
import networkx as nx
import community as community_louvain
from constants.dash_constants import *


def get_all_interacting_users(tweets):
    users = set()
    retweeted_users = set()
    quoted_users = set()
    replied_users = set()

    # merged csvs created user_screenname_x and user_screenname_y
    for u in tweets['user_screenname_x']:
        users.add(u)
    print('Count unique users: ', len(users))

    for u in tweets[tweets['replied_to_user_screenname'].notna()]['replied_to_user_screenname']:
        if u == u:
            replied_users.add(u)
    print('Count unique replied users: ', len(replied_users))

    for u in tweets[tweets['retweeted_user_screenname'].notna()]['retweeted_user_screenname']:
        if u == u:
            retweeted_users.add(u)
    print('Count unique retweeted users: ', len(retweeted_users))

    for u in tweets[tweets['quoted_user_screenname'].notna()]['quoted_user_screenname']:
        if u == u:
            quoted_users.add(u)
    print('Count unique quoted users: ', len(quoted_users))

    common_interacting_users = set.intersection(
        users, replied_users, retweeted_users, quoted_users)
    print('{} total unique interacting users'.format(
        len(common_interacting_users)))

    return set.union(users, replied_users, retweeted_users, quoted_users)


def get_weighted_interacting_edges(tweets):
    interacting_edges = dict()  # try set as well

    # replies interaction
    replies = tweets[tweets['tweet_enagagement_type'] == 'Reply'][[
        'user_screenname_x', 'replied_to_user_screenname']]
    for user, iuser in zip(replies['user_screenname_x'], replies['replied_to_user_screenname']):
        if user and iuser and (user != iuser):
            if (user, iuser) in interacting_edges:
                interacting_edges[(user, iuser)] += 1
            else:
                interacting_edges[(user, iuser)] = 1

    # retweets interaction
    retweets = tweets[tweets['tweet_enagagement_type'] == 'Retweet'][[
        'user_screenname_x', 'retweeted_user_screenname']]
    for user, iuser in zip(retweets['user_screenname_x'], retweets['retweeted_user_screenname']):
        if user and iuser and (user != iuser):
            if (user, iuser) in interacting_edges:
                interacting_edges[(user, iuser)] += 1
            else:
                interacting_edges[(user, iuser)] = 1

    # quotes interaction
    quotes = tweets[tweets['tweet_enagagement_type'] == 'Quote'][[
        'user_screenname_x', 'quoted_user_screenname']]
    for user, iuser in zip(quotes['user_screenname_x'], quotes['quoted_user_screenname']):
        if user and iuser and (user != iuser):
            if (user, iuser) in interacting_edges:
                interacting_edges[(user, iuser)] += 1
            else:
                interacting_edges[(user, iuser)] = 1

    weighted_interacting_edges_ = set()
    for k, v in interacting_edges.items():
        weighted_interacting_edges_.add(k + (v,))
    return weighted_interacting_edges_


def create_weighted_directed_graph(nodes, edges):
    G = nx.MultiDiGraph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)
    return G


def graph_details(G):
    degrees = [val for (node, val) in G.degree()]
    print('The maximum degree of the graph is ' + str(np.max(degrees)))
    print('The minimum degree of the graph is ' + str(np.min(degrees)))
    print('There are ' + str(G.number_of_nodes()) + ' nodes and ' +
          str(G.number_of_edges()) + ' edges present in the graph')
    print('The average degree of the nodes in the graph is ' + str(np.mean(degrees)))


def get_top_ranked_users(G, top_users_count=50):
    ranked_users = nx.pagerank(G, 0.9)
    ranked_users = dict(sorted(ranked_users.items(),
                        key=lambda item: item[1], reverse=True))

    return list(ranked_users)[:top_users_count]


def generate_prominenet_groups(G, k=2):
    groups = nx.algorithms.centrality.prominent_group(G, 2)
    print(groups)


def generate_dash_influential_users(tweets, top_ranking,
                                    save=False,
                                    influential_users_save_path=INFLUENTIAL_USERS_PATH):
    normal_users = tweets[tweets['user_screenname_x'].isin(
        top_ranking)][['user_id_x', 'user_screenname_x', 'user_geo_coding', 'user_verified']]
    normal_users.rename(
        columns={'user_id_x': 'user_id', 'user_screenname_x': 'user_screenname'}, inplace=True)

    rts_users = tweets[tweets['retweeted_user_screenname'].isin(top_ranking)][[
        'retweeted_user_id', 'retweeted_user_screenname', 'retweeted_user_geo_coding', 'retweeted_user_verified']]
    rts_users.rename(columns={'retweeted_user_id': 'user_id',
                              'retweeted_user_screenname': 'user_screenname',
                              'retweeted_user_geo_coding': 'user_geo_coding',
                              'retweeted_user_verified': 'user_verified'}, inplace=True)

    quoted_users = tweets[tweets['quoted_user_screenname'].isin(top_ranking)][[
        'quoted_user_id', 'quoted_user_screenname', 'quoted_user_geo_coding', 'quoted_user_verified']]
    quoted_users.rename(columns={
        'quoted_user_id': 'user_id',
        'quoted_user_screenname': 'user_screenname',
        'quoted_user_geo_coding': 'user_geo_coding',
        'quoted_user_verified': 'user_verified'}, inplace=True)

    influential_users = pd.concat(
        [normal_users, rts_users, quoted_users]).drop_duplicates().reset_index(drop=True)

    if save:
        pd.DataFrame.to_csv(influential_users, influential_users_save_path)
        print('Saved:', influential_users_save_path)

    return influential_users


def generate_dash_influential_users_tweets(tweets, top_ranking,
                                           save=False,
                                           influential_users_tweets_save_path=INFLUENTIAL_USERS_TWEETS_PATH):
    normal_users = tweets[tweets['user_screenname_x'].isin(
        top_ranking)][['user_screenname_x', 'tweet_text']]
    normal_users.rename(
        columns={'user_screenname_x': 'user_screenname'}, inplace=True)

    rts_users = tweets[tweets['retweeted_user_screenname'].isin(
        top_ranking)][['retweeted_user_screenname', 'tweet_text']]
    rts_users.rename(
        columns={'retweeted_user_screenname': 'user_screenname'}, inplace=True)

    quoted_users = tweets[tweets['quoted_user_screenname'].isin(
        top_ranking)][['quoted_user_screenname', 'quoted_tweet_text']]
    quoted_users.rename(columns={'quoted_user_screenname': 'user_screenname',
                                 'quoted_tweet_text': 'tweet_text'}, inplace=True)

    influential_users_tweets = pd.concat(
        [normal_users, rts_users, quoted_users]).reset_index(drop=True)

    if save:
        pd.DataFrame.to_csv(influential_users_tweets,
                            influential_users_tweets_save_path)
        print('Saved:', influential_users_tweets_save_path)

    return influential_users_tweets


def quality_check_pagerank(tweets, top_ranking, top_users_count):
    verified_users = tweets[tweets['user_verified']
                            == True]['user_screenname_x']
    rt_verified_users = tweets[(tweets['tweet_enagagement_type'] == 'Retweet') & (
        tweets['retweeted_user_verified'] == True)]['retweeted_user_screenname']
    q_verified_users = tweets[(tweets['tweet_enagagement_type'] == 'Quote') & (
        tweets['quoted_user_verified'] == True)]['quoted_user_screenname']

    all_verified_users = set(list(verified_users) +
                             list(rt_verified_users) + list(q_verified_users))
    z = set(top_ranking).intersection(all_verified_users)
    print('The number of verified users in the top {} rankings - {}%'.format(
        top_users_count, len(z)/top_users_count*100))
    return len(z)/top_users_count*100


def get_communities(G_pruned, tweets, save=False,
                    communities_user_save_path=COMMUNITIES_USERS_PATH,
                    # communities_plot_save_path=COMMUNITIES_PLOT_PATH,
                    communities_tweets_save_path=COMMUNITIES_TWEETS_PATH,
                    user_to_community_save_path=USER_TO_COMMUNITY_PATH):

    G2 = G_pruned.to_undirected()

    # Running the Louvain's algorithm for communities detection
    communities = community_louvain.best_partition(G2)

    communities_grouped = col.defaultdict(list)
    for k, v in communities.items():
        communities_grouped[v].append(k)

    # taking top 8 large communities
    larger_communities = sorted(communities_grouped, key=lambda c: len(
        communities_grouped[c]), reverse=True)[:8]

    reamapped_communities = {}
    for k, v in communities.items():
        # if community not among the largest communities then slip it
        if v not in larger_communities:
            continue

        # remapping the communities in the range of 0-8
        reamapped_communities[k] = larger_communities.index(v)

    communities_grouped_with_colors = {}
    for idx, community_no in enumerate(larger_communities):
        communities_grouped_with_colors[idx] = {
            "users": communities_grouped[community_no],
            "color": COMMUNITIES_COLORS_DICT[str(idx)]
        }

    communities_tweets = {}
    for idx, community_no in enumerate(larger_communities):
        community_tweets = tweets[
            (tweets['user_screenname_x'].isin(communities_grouped[community_no]) |
             tweets['retweeted_user_screenname'].isin(communities_grouped[community_no]) |
             tweets['quoted_user_screenname'].isin(communities_grouped[community_no]) |
             tweets['replied_to_user_screenname'].isin(communities_grouped[community_no])) &
            (tweets['processed_tweet_text'].notna())]['processed_tweet_text'].tolist()
        communities_tweets[idx] = community_tweets

    if save:
        # plt.savefig(communities_plot_save_path, bbox_inches='tight')

        with open(user_to_community_save_path, 'w') as f:
            json.dump(reamapped_communities, f)

        with open(communities_user_save_path, 'w') as f:
            json.dump(communities_grouped_with_colors, f)

        with open(communities_tweets_save_path, 'w') as f:
            json.dump(communities_tweets, f)

        print('Saved:', communities_user_save_path,
              user_to_community_save_path, communities_tweets_save_path)

    print('number of communities created:',
          len(communities_grouped_with_colors))
    return communities_grouped


def get_graph_min_degree(Graph):
    degrees = [val for (_, val) in Graph.degree()]
    print('The minimum degree of the graph is ' + str(np.min(degrees)))
    return np.min(degrees)


def create_min_degree_graph(G_old, min_degree=MIN_DEGREE_OF_NETWORKING_GRAPH):
    print("MIN_DEGREE_OF_NETWORKING_GRAPH", MIN_DEGREE_OF_NETWORKING_GRAPH)
    G = nx.Graph()
    for u, v, data in G_old.edges(data=True):
        w = data['weight'] if 'weight' in data else 1.0
        if G.has_edge(u, v):
            G[u][v]['weight'] += w
        else:
            G.add_edge(u, v, weight=w)

    G = nx.k_core(G, k=min_degree)
    return G


def generate_networking_graph_data(G):
    # Generating position of the nodes using the `spring_layout`
    G_pos = nx.spring_layout(G)
    networking_graph__data = {'data': []}

    file = open(NETWORKING_GRAPH_DATA, 'w')

    with open(USER_TO_COMMUNITY_PATH, 'r') as f:
        user_community = json.load(f)

    for node in G.nodes:
        if node in user_community:
            node_data = {'data': {'id': node, 'label': node},
                         'classes': str(user_community[node]),
                         'position': {'x': G_pos[node][0], 'y': G_pos[node][1]}}
            networking_graph__data['data'].append(node_data)

    for edge in G.edges:
        if edge[0] in user_community and edge[1] in user_community:
            edge_data = {'data': {'source': edge[0], 'target': edge[1]}}
            networking_graph__data['data'].append(edge_data)
            # file.write(node_data)

    json.dump(networking_graph__data, file)
    file.close()
    return networking_graph__data
