from main import LMT_Statistics

lmt = LMT_Statistics()
lmt.make_graphs(return_to_self=True)
server = lmt.run_server()