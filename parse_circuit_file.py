
import numpy as np

def parse_circuit_file(file_path):
    """
    Parse the circuit file and extract relevant information.
    
    Returns dictionary with parsed information.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Dictionary to hold circuit information
    circuit_info = {
        "total_nodes": 0,
        "node_delays": [],
        "edge_delays": {},
        "max_clock_cycle": 0
    }

    for line in lines:
        # Ignore comments and empty lines
        if line.startswith('//') or line.strip() == '':
            continue

        # Split the line into key and value
        key, value = line.split('=')
        value = value.strip()  # Remove any leading/trailing whitespace

        if key == 'TotalNodes':
            circuit_info["total_nodes"] = int(value)
        elif key == 'NodeDelays':
            # Split the delays and convert them to integers
            circuit_info["node_delays"] = list(map(int, value.split(',')))
        elif key == 'MaxClockCycle':
            circuit_info["max_clock_cycle"] = int(value)
        else:
            # If key doesn't match any of of the options above, this must
            # be an edge delay entry. Parse the edge's name and delay value
            edge_name = key
            edge_delay = int(value)
            circuit_info["edge_delays"][edge_name] = edge_delay

    return circuit_info

def create_wmatrix(circuit_info):
    """
    Create initial W Matrix
    
    Populate matrix with edge weights from circuit info
    """
# Create a 2D array with n rows and columns
size = circuit_info.get("total_nodes")

# Populating matrices with zeros initially...
# Will need to change to large value at some point=
w_matrix = np.zeros((size,size))

# Access or modify elements using array[row, col]



# Bolierplate
if __name__ == "__main__":
    file_path_txt = 'example_input2.txt'
    parsed_info = parse_circuit_file(file_path_txt)
    print(parsed_info)
