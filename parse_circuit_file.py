import re

def parse_circuit_file(file_path):
    """
    Parse the circuit file and extract relevant information.
    
    Returns dictionary with parsed information.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Data structure to hold the parsed information.
    circuit_info = {
        "total_nodes": 0,
        "node_delays": [],
        "edge_delays": {},
        "max_clock_cycle": 0
    }

    for line in lines:
        # Ignore comments and empty lines.
        if line.startswith('//') or line.strip() == '':
            continue

        # Split the line into key and value components.
        key, value = line.split('=')
        value = value.strip()  # Remove any leading/trailing whitespace.

        if key == 'TotalNodes':
            circuit_info["total_nodes"] = int(value)
        elif key == 'NodeDelays':
            # Split the delays and convert them to integers.
            circuit_info["node_delays"] = list(map(int, value.split(',')))
        elif key == 'MaxClockCycle':
            circuit_info["max_clock_cycle"] = int(value)
        else:
            # We assume this is an edge delay entry. We'll parse the edge's name and delay.
            # The edge's name is everything before the "=" character.
            edge_name = key
            edge_delay = int(value)
            circuit_info["edge_delays"][edge_name] = edge_delay

    return circuit_info


# Bolierplate
if __name__ == "__main__":
    file_path_txt = 'example_input.txt'
    parsed_info = parse_circuit_file(file_path_txt)
    print(parsed_info)
