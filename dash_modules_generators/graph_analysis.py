import json
import collections as col
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# graph analysis
import networkx as nx
import community as community_louvain
from utils.dash_constants import *


def get_all_interacting_users(tweets):
    sg_users = set()
    retweeted_users = set()
    quoted_users = set()
    replied_users = set()

    # merged csvs created user_screenname_x and user_screenname_y
    for u in tweets['user_screenname_x']:
        sg_users.add(u)
    print('Count unique SG users: ', len(sg_users))

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
        sg_users, replied_users, retweeted_users, quoted_users)
    print('{} total unique common interacting users'.format(
        len(common_interacting_users)))

    return set.union(sg_users, replied_users, retweeted_users, quoted_users)


def get_weighted_interacting_edges(tweets):
    interacting_edges = dict()  # try set as well

    # replies interaction
    replies_sg = tweets[tweets['tweet_enagagement_type'] == 'Reply'][[
        'user_screenname_x', 'replied_to_user_screenname']]
    for user, iuser in zip(replies_sg['user_screenname_x'], replies_sg['replied_to_user_screenname']):
        if user and iuser and (user != iuser):
            if (user, iuser,) in interacting_edges:
                interacting_edges[(user, iuser,)] += 1
            else:
                interacting_edges[(user, iuser,)] = 1

    # retweets interaction
    retweets_sg = tweets[tweets['tweet_enagagement_type'] == 'Retweet'][[
        'user_screenname_x', 'retweeted_user_screenname']]
    for user, iuser in zip(retweets_sg['user_screenname_x'], retweets_sg['retweeted_user_screenname']):
        if user and iuser and (user != iuser):
            if (user, iuser,) in interacting_edges:
                interacting_edges[(user, iuser,)] += 1
            else:
                interacting_edges[(user, iuser,)] = 1

    # quotes interaction
    quotes_sg = tweets[tweets['tweet_enagagement_type'] == 'Quote'][[
        'user_screenname_x', 'quoted_user_screenname']]
    for user, iuser in zip(quotes_sg['user_screenname_x'], quotes_sg['quoted_user_screenname']):
        if user and iuser and (user != iuser):
            if (user, iuser,) in interacting_edges:
                interacting_edges[(user, iuser,)] += 1
            else:
                interacting_edges[(user, iuser,)] = 1

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


def generate_dash_influential_users(tweets, top_ranking,
                                    save=False,
                                    influential_users_save_path=INFLUENTIAL_USERS_PATH):
    # TODO: Can add followers counts but missing for retweeted_user_screenname and quoted_user_screenname
    # tweets = tweets.dropna(axis=0, subset=['user_id_x'])
    # tweets = tweets.dropna(axis=0, subset=['retweeted_user_id'])
    # tweets = tweets.dropna(axis=0, subset=['quoted_user_id'])

    # tweets[['user_id_x', 'retweeted_user_id', 'quoted_user_id']] = tweets[[
    #     'user_id_x', 'retweeted_user_id', 'quoted_user_id']].fillna(0).astype(int)

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
    # TODO: Can add followers counts but missing for retweeted_user_screenname and quoted_user_screenname
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
    sg_verified_users = tweets[tweets['user_verified']
                                  == True]['user_screenname_x']
    rt_verified_users = tweets[(tweets['tweet_enagagement_type'] == 'Retweet') & (
        tweets['retweeted_user_verified'] == True)]['retweeted_user_screenname']
    q_verified_users = tweets[(tweets['tweet_enagagement_type'] == 'Quote') & (
        tweets['quoted_user_verified'] == True)]['quoted_user_screenname']

    all_verified_users = set(list(sg_verified_users) +
                             list(rt_verified_users) + list(q_verified_users))
    z = set(top_ranking).intersection(all_verified_users)
    print('The number of verified users in the top {} rankings - {}%'.format(
        top_users_count, len(z)/top_users_count*100))
    return len(z)/top_users_count*100


def get_communities(G_pruned, tweets, save=False,
                    communities_user_save_path=COMMUNITIES_USERS_PATH,
                    communities_plot_save_path=COMMUNITIES_PLOT_PATH,
                    communities_tweets_save_path=COMMUNITIES_TWEETS_PATH,
                    user_to_community_save_path=USER_TO_COMMUNITY_PATH):
    G2 = G_pruned.to_undirected()
    communities = community_louvain.best_partition(G2)
    communities_plot = nx.spring_layout(G2)

    cmap = cm.get_cmap('viridis', max(communities.values()) + 1)
    nx.draw_networkx_nodes(G2, communities_plot, communities.keys(), node_size=40,
                           cmap=cmap, node_color=list(communities.values()))
    nx.draw_networkx_edges(G2, communities_plot, alpha=0.5)

    communities_grouped = col.defaultdict(list)
    for k, v in communities.items():
        communities_grouped[v].append(k)

    communities_grouped_ = {}
    for k, v in communities_grouped.items():
        communities_grouped_[k] = {
            "users": v,
            "color": CLUSTER_COLORS_DICT[str(k)]
        }

    # communities_tweets = {'cluster': [], 'tweets': []}
    communities_tweets = {}
    for c, u in communities_grouped.items():
        # print(u)
        cluster_tweets = tweets[
            (tweets['user_screenname_x'].isin(u) |
             tweets['retweeted_user_screenname'].isin(u) |
             tweets['quoted_user_screenname'].isin(u) |
             tweets['replied_to_user_screenname'].isin(u)) &
            (tweets['processed_tweet_text'].notna())]['processed_tweet_text'].tolist()
        # cluster_tweets = cluster_tweets

        communities_tweets[c] = cluster_tweets
        # communities_tweets['cluster'].extend(len(cluster_tweets)*[c])
        # communities_tweets['cluster'].extend(cluster_tweets)

    if save:
        plt.savefig(communities_plot_save_path, bbox_inches='tight')

        with open(user_to_community_save_path, 'w') as f:
            json.dump(communities, f)

        with open(communities_user_save_path, 'w') as f:
            json.dump(communities_grouped_, f)

        with open(communities_tweets_save_path, 'w') as f:
            json.dump(communities_tweets, f)

        print('Saved:', communities_user_save_path,
              user_to_community_save_path, communities_tweets_save_path)

    print('number of clusters created:', len(communities_grouped))
    return communities_grouped, communities_plot


def get_min_graph_degree(Graph):
    degrees = [val for (_, val) in Graph.degree()]
    print('The minimum degree of the graph is ' + str(np.min(degrees)))
    return np.min(degrees)


def remove_low_degree_edges(G):
    G_pruned = G.copy()
    low_degree_nodes = [node for node, degree in dict(
        G_pruned.degree()).items() if degree < 10]
    # print('Number of users to be removed with degree less than {}: {}'.format(en(low_degree_nodes)))
    G_pruned.remove_nodes_from(low_degree_nodes)
    return G_pruned


def get_min_degree_graph(G, min_degree):
    while get_min_graph_degree(G) < min_degree:
        G = remove_low_degree_edges(G)
    return G


def generate_cytograph_data(G):
    G_pos = nx.spring_layout(G)
    cyto_data = {'data': []}

    file = open(NETWORKING_GRAPH_DATA, 'w')

    with open(USER_TO_COMMUNITY_PATH, 'r') as f:
        user_community = json.load(f)

    for node in G.nodes:
        node_data = {'data': {'id': node, 'label': node},
                     'classes': str(user_community[node]),
                     'position': {'x': G_pos[node][0], 'y': G_pos[node][1]}}
        cyto_data['data'].append(node_data)

    for edge in G.edges:
        edge_data = {'data': {'source': edge[0], 'target': edge[1]}}
        cyto_data['data'].append(edge_data)
        # file.write(node_data)

    json.dump(cyto_data, file)
    file.close()
    return cyto_data
