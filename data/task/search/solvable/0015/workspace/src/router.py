from parser import parse_header

def load_request(line):
    return parse_header(line)
