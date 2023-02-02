import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

# credit to Riley Wong on github
# https://github.com/rileynwong/simple-pagerank/blob/master/graph.py

class Node(object):
    def __init__(self, inbound=None, outbound=None):
        self.name = ''

        if inbound:
            self.inbound = inbound
        else:
            self.inbound = []

        if outbound:
            self.outbound = outbound
        else:
            self.outbound = []

    def add_outbound_edge(self, node):
        # Add directed edge from this node to another node
        self.outbound.append(node)
        node.inbound.append(self)

    def add_inbound_edge(self, node):
        # Add directed edge from another node to this node
        self.inbound.append(node)
        node.outbound.append(self)


class Graph(object):
    # Note: Does not account for error-checking
    """ A dictionary of Nodes. Key is node name, value is node object. """

    def __init__(self, nodes=None):
        if nodes:
            self.nodes = nodes
        else:
            self.nodes = {}

    def add_node(self, node_name, node):
        # Add node to graph
        node.name = node_name
        self.nodes[node_name] = node

    def add_edge(self, start_node, end_node):
        # Add edge from start node to end node
        start = self.nodes[start_node]
        end = self.nodes[end_node]

        start.add_outbound_edge(end)

    def get_neighbors(self, node_name):
        # Return outbound neighbors for a given node
        node = self.nodes[node_name]
        neighbors = node.outbound
        return neighbors

    def remove_node(self, node_name):
        # Remove node and its outbound edges from the graph
        if node_name in self.graph:
            del self.nodes[node_name]

    """ # Running out of time ...
    def remove_edge(self, start_node, end_node):
        start = self.nodes[start_node]
        end = self.nodes[end_node]
        # Remove directed edge from start node to end node
        self.nodes[start_node].remove(end_node)
    """

    def get_nodes(self):
        # Return a list of nodes
        nodes = list(self.nodes.values())
        return nodes
#-------------------------------------------------- end of setup



class frontier_url():
    def __init__(self, url, count, flag):
        self.url = url
        self.count = count
        self.flag = flag
        self.pagerank = 0

    def add_count(self):
        self.count += 1

    def visited(self):
        self.flag = True

    def set_pagerank(self, pagerank):
        self.pagerank = pagerank

def pagerank(graph):
    """
    Graph object as input
    Returns a dictionary where the keys are the node names and the values are
    the calculated pagerank score for that given node.
    """

    # Initialize values for all nodes s.t. that add up to one
    n = len(graph.nodes)
    init_val = 1.0/n
    ranks = dict(zip(graph.get_nodes(), [init_val] * n))

    new_ranks = ranks

    # Calculate new rank for each node
    for node, prev_rank in ranks.items():
        rank_sum = 0.0

        # Iterate through incoming nodes
        for incoming_node in node.inbound:
            numerator = ranks[incoming_node]
            denominator = len(incoming_node.outbound)
            transfer_amount = numerator / denominator

            # Transfer rank score
            new_ranks[incoming_node] = new_ranks[incoming_node] - transfer_amount
            rank_sum = rank_sum + transfer_amount

        new_ranks[node] = ranks[node] + rank_sum

    # Set ranks to the new ranks calculated in this iteration
    ranks = new_ranks

    return ranks

global found, url_graph, sites_crawled, frontier
found = ['https://www.cnn.com']
frontier = []
url_graph = Graph()
sites_crawled = 0
url_graph.add_node('https://www.cnn.com',Node())

class pagerankspider(CrawlSpider):
    name = 'pagerank'
    allowed_domains = ['cnn.com']
    #start_urls = ['https://en.wikipedia.org/wiki/Cat']


    def start_requests(self):
        yield scrapy.Request('https://www.cnn.com', self.parse)

    def parse(self, response):
        global frontier, found, sites_crawled, url_graph

        for href in response.xpath('//a/@href').getall(): # finds all links
            if sites_crawled >= 3000:
                return

            url = response.urljoin(href)

            if url not in found: # add new url to frontier
                found.append(url)
                temp = Node()
                url_graph.add_node(url, temp) # gives the node a name

                item = frontier_url(url, 1, False)
                frontier.append(item)
                # can query current url with resposne.request.url
                url_graph.add_edge(response.request.url, url)
            else:
                # can query current url with resposne.request.url
                url_graph.add_edge(response.request.url, url)
                continue


            
            
            ranks = pagerank(url_graph)
            # change pagerank values for frontier
            for node, value in ranks.items():
                for i in range(len(frontier)):
                    if frontier[i].url == node.name:
                        # set pagerank for frontier_url objects
                        frontier[i].set_pagerank(value)


            # sort list by decending pagerank
            frontier.sort(reverse=True, key=lambda x:x.pagerank)

            for i in range(len(frontier)):
                if not frontier[i].flag: # if haven't been checked
                    frontier[i].visited() # flips flag
                    sites_crawled += 1
                    yield {"url": url, "sitenumber": sites_crawled} # prints into JSON
                    yield scrapy.Request(frontier[i].url, self.parse)
                    break # ends instance


            
