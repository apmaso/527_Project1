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

    # Create a 3D array with 3 dimensions equal to the number of nodes
    # Populate this 3D array with a high number as initial value (9999)
    # This default value represents no path between the two nodes
    size = circuit_info.get("total_nodes")
    shape = (size,size,size)
    fill_value = 9999
    w_matrix = np.full(shape,fill_value)

    # All elements where row == col should be zero
    # U==V -> W(u,v)==0
    for e in range(size):
        for n in range(size):
            w_matrix[e,n,n] = 0

    # Modify elements in w-matrix using "edge_delays" dictionary in circuit_info
    # Access using edge_name as key and edge_delay as the value. 
    # edge_name ends in two integers: first=row, second=col 
    for edge_name, edge_delay in circuit_info["edge_delays"].items():
    
        # First four characters are always the same, 'Edge'
        # Arrays start from 0. Row = (node-1) and Col = (node-1)
        i, j = map(int, edge_name[4:])
        for e in range(size):
            w_matrix[e,i-1,j-1] = edge_delay

    # Parameterized the algorithm by adding a 3rd dimension to my array
    # e represents the maximum number of edges considered in any given path
    for e in range(1,size):
        for r in range(size):
            for c in range(size):
                not_c = list(range(0,c))+list(range(c+1,size))
                for i in not_c:
                        if (w_matrix[e-1,r,i] + w_matrix[e-1,i,c]) < w_matrix[e,r,c]:
                            w_matrix[e,r,c] = (w_matrix[e-1,r,i] + w_matrix[e-1,i,c]) 
                        else:
                            w_matrix[e,r,c]=w_matrix[e,r,c]
    
    return w_matrix


def create_gpmatrix(circuit_info):
    """
    Create G-Prime Matrix
    
    Populate initial matrix using w'(e)=m*w(e)-d(u)
    """
    
    # Create a 3D array with 3 dimensions equal to the number of nodes
    # Populate this 3D array with a high number as initial value (9999)
    # This default value represents no path between the two nodes
    size = circuit_info.get("total_nodes")
    shape = (size,size,size)
    fill_value = 9999
    gp_matrix = np.full(shape,fill_value)

    # Initialize gp-matrix using edge_delays, node_delays and M 
    node_delay = circuit_info.get("node_delays")
    m_value = size * max(node_delay)
    for edge_name, edge_delay in circuit_info["edge_delays"].items():
    
        i, j = map(int, edge_name[4:])
        for e in range(size):
            gp_matrix[e,i-1,j-1] = m_value * edge_delay - node_delay[i-1]
 
    # Parameterized the algorithm by adding a 3rd dimension to my array
    # e represents the maximum number of edges considered in any given path
    for e in range(1,size):
        for r in range(size):
            for c in range(size):
                not_c = list(range(0,c))+list(range(c+1,size))
                for i in not_c:
                        if (gp_matrix[e-1,r,i] + gp_matrix[e-1,i,c]) < gp_matrix[e,r,c]:
                            gp_matrix[e,r,c] = (gp_matrix[e-1,r,i] + gp_matrix[e-1,i,c]) 
                        else:
                            gp_matrix[e,r,c]=gp_matrix[e,r,c]
    
    return gp_matrix


def create_dmatrix(circuit_info, w_matrix, gp_matrix):
    """
    Create D Matrix
    
    Populate matrix using D(u,v)=m*W(u,v)-G'(u,v)+d(v) 
    """
    
    # Create a 3D array with 3 dimensions equal to the number of nodes
    # Populate this 3D array with a high number as initial value (9999)
    # This default value represents no path between the two nodes
    size = circuit_info.get("total_nodes")
    shape = (size,size)

    # Initialize d-matrix 
    # All elements where row == col should be zero
    # U==V -> W(u,v)==0
    fill_value = 9999
    d_matrix = np.full(shape,fill_value)

    node_delay = circuit_info.get("node_delays")
    m_value = size * max(node_delay)
    for i in range(size):
        for j in range(size):
            if i != j:
                d_matrix[i-1,j-1] = m_value * w_matrix[i-1,j-1] - gp_matrix[i-1,j-1] + node_delay[j-1]
            else:
                d_matrix[i-1,j-1] = node_delay[i-1]

    return d_matrix


def ineq_matrix(circuit_info, w_matrix, d_matrix):
    """
    Create and Print Inequalities
    """
    
    size = circuit_info.get("total_nodes")
    c_value = circuit_info.get("max_clock_cycle")
    node_delay = circuit_info.get("node_delays")



    # Create a 3D array with 3 dimensions equal to the number of nodes
    # Populate this 3D array with a high number as initial value (9999)
    # This array will be used to store the sets of inequalites created 
    # 1 axis will represent each new set of inequalites
    ineq_sets = c_value-max(node_delay)+2
    shape = (ineq_sets,size,size)
    fill_value = 9999
    ineq_matrix = np.full(shape,fill_value)


    # Store the inequalities in a 3D array with the initial set 
    # of inequalities as layer/generation 0 and then each new layer
    # representing inequalites for our decrementing c_value
    for edge_name, edge_delay in circuit_info["edge_delays"].items():
    
        # First four characters are always the same, 'Edge'
        i, j = map(int, edge_name[4:])
        ineq_matrix[0,i-1,j-1] = edge_delay


    # Compare D and W matrices to create each new set of inequalities
    # Decrement c & repeat while c >= max node delay in our circuit
    # Store each new matrix as a new layer/generation along axis 0
    g = 1
    while c_value >= max(node_delay):
        for i in range(size):
            for j in range(size):
                if d_matrix[i,j] > c_value:
                    ineq_matrix[g,i,j] = w_matrix[i,j]-1
                else:
                    continue
        g = g + 1
        c_value = c_value-1
    

    return ineq_matrix


def reduced_ineq(circuit_info, ineq_matrix, new_c_value):
    """
    Takes matrix of all sets of inequalities from initial set down to
    the desired max clock cylce and compiles them in to a single matrix, 
    removing ay redundancies
    """
 
    size = circuit_info.get("total_nodes")
    c_value = circuit_info.get("max_clock_cycle")
    node_delay = circuit_info.get("node_delays")



    # Create a 2D array with 2 dimensions equal to the number of nodes
    # Populate this 2D array with a high number as initial value (9999)
    # This array will be used remove redundant inequalites
    sets_to_reduce = c_value - new_c_value + 2
    shape = (size,size)
    fill_value = 9999
    reduced_ineq = np.full(shape,fill_value)




    # Compare cells across one axis to reduce/remove redundant ineq
    for g in range(sets_to_reduce):
        for r in range(size):
            for c in range(size):
                if ineq_matrix[g,r,c] < reduced_ineq[r,c]:
                    reduced_ineq[r,c] = ineq_matrix[g,r,c] 
                else:
                    continue 
    

    # Display our reduced set of inequalities
    print("----------------------------------------")
    print(f"      Reduced Set of Inequalities       ")
    print("----------------------------------------")
    
    for k in range(size):
        for l in range(size):
            if reduced_ineq[k,l] != 9999:
                print(f"r({k+1}) - r({l+1}) <= {reduced_ineq[k,l]}")
            else:
                continue

    return reduced_ineq



def constraint_graph(circuit_info,ineq_matrix):
    """
    Represent constraint graph with a matrix
    Constraint graph has one additional node
    Populate matrix from ineq_matrix but swap U <=> V
    """

    # Trying with only 1 dimensions equal to the number of nodes+1
    size = circuit_info.get("total_nodes")
    shape = (size,size+1,size)
    fill_value = 9999
    constraint_matrix = np.full(shape,fill_value)


    # Fill all layers with cells from ineq_matrix, switching U and V
    # Fill the extra row with 0s
    for g in range(size):
 
        for n in range(size):
            constraint_matrix[g,size,n] = 0

        for i in range(size):
            for j in range(size):
                constraint_matrix[g,i,j] = ineq_matrix[j,i]

    # Parameterized the algorithm by adding a 3rd dimension to my array
    # g represents the each generation of matrix the algorithm creates
    for g in range(1,size):
        for r in range(size+1):
            for c in range(size):
                not_c = list(range(0,c))+list(range(c+1,size))
                for i in not_c:
                        if (constraint_matrix[g-1,r,i] + constraint_matrix[g-1,i,c]) < constraint_matrix[g,r,c]:
                            constraint_matrix[g,r,c] = (constraint_matrix[g-1,r,i] + constraint_matrix[g-1,i,c]) 
                        else:
                            constraint_matrix[g,r,c]=constraint_matrix[g,r,c]
    
    return constraint_matrix

def retimed_circuit_file(circuit_info, new_c_value, retimed_matrix, new_file_path):

    size = circuit_info.get("total_nodes") 
    with open(new_file_path, 'w') as file:
        # Write the total number of nodes
        file.write("// Specifies the total number of nodes in the graph\n")
        file.write(f"TotalNodes={size}\n\n")
        
        # Write the delays for each node
        file.write("// Specifies the delay for each node in the graph\n")
        node_delays = ','.join(map(str, circuit_info['node_delays']))
        file.write(f"NodeDelays={node_delays}\n\n")
        
        # Write the delays for each edge
        file.write("// Specifies the delay for each edge between nodes in the graph\n")
        for edge, delay in circuit_info['edge_delays'].items():
            i, j = map(int, edge[4:])
            file.write(f"{edge}={retimed_matrix[i-1][j-1]}\n")
        
        # Write the maximum clock cycle
        file.write("\n// Specifies the maximum clock cycle for the algorithm\n")
        file.write(f"MaxClockCycle={new_c_value}\n")
    
    return


   
# Run the thing and do the stuff 
if __name__ == "__main__":
    
    #############################################################
    ## Usage:
    ## Path for our circuit file and for the retimed circuit file
    file_path_txt = 'example_input.txt'
    new_file_path = 'retimed_circuit.txt'
    #############################################################


    parsed_info = parse_circuit_file(file_path_txt)
    last_gen = parsed_info.get("total_nodes")-1
    c_value = parsed_info.get("max_clock_cycle")
    node_delay = parsed_info.get("node_delays")
    size = parsed_info.get("total_nodes")
    
    w_matrix = create_wmatrix(parsed_info)
    gp_matrix = create_gpmatrix(parsed_info)
    d_matrix = create_dmatrix(parsed_info,w_matrix[last_gen],gp_matrix[last_gen])
    




    # Will need to call inequalities matrix as well as contraing
    # matrix calculation here to help group items for readability

    print("----------------------------------------")
    print("          Initial Circuit Info          ")
    print("----------------------------------------")
    print(parsed_info)
    print()
    
    user_input = input("Would you like to see the matrix generations?(y/n)")
    
    print("----------------------------------------")
    print("                W Matrix                ")
    print("----------------------------------------")
    if user_input == 'y':
        print(w_matrix)
    elif user_input == 'n':
        print(w_matrix[last_gen])
    else:
        print("Invalid response, only displaying final gen by default")
        print(w_matrix[last_gen])

    print("----------------------------------------")
    print("                W' Matrix               ")
    print("----------------------------------------")
    if user_input == 'y':
        print(gp_matrix)
    elif user_input == 'n':
        print(gp_matrix[last_gen])
    else:
        print("Invalid response, only displaying final gen by default")
        print(gp_matrix[last_gen])

    print("----------------------------------------")
    print("                D Matrix                ")
    print("----------------------------------------")
    print(d_matrix)
    
    ineq_matrix = ineq_matrix(parsed_info,w_matrix[last_gen],d_matrix)

    

    # Would you like to miminimize the clock period or set a different c value
    minimize = input("Would you like to minimize the clock period?(y/n)")
    minimum_c = max(node_delay)
    if minimize == 'y':
        new_c_value = minimum_c
        print(f"Minimizing circuit with c = {new_c_value}")
    elif user_input == 'n':
        new_c_value = int(input("What new c_value would you like to try?"))
        print(f"Minimizing circuit with c = {new_c_value}")
    else:
        new_c_value = minimum_c
        print("Invalid response, minimizing circuit as default")
        print(f"Minimizing circuit with c = {new_c_value}")

    reduced_ineq = reduced_ineq(parsed_info,ineq_matrix,new_c_value)

    constraint_matrix = constraint_graph(parsed_info,reduced_ineq)
    
    print("----------------------------------------")
    print("           Constraint Matrix            ")
    print("----------------------------------------")
    if user_input == 'y':
        print(constraint_matrix)
    elif user_input == 'n':
        print(constraint_matrix[last_gen])
    else:
        print("Invalid response, only displaying final gen by default")
        print(constraint_matrix[last_gen]) 
    
    print("----------------------------------------")
    print("            Retiming Vector             ")
    print("----------------------------------------")
    retiming_vector = constraint_matrix[last_gen][last_gen+1] 
    print(retiming_vector)

    retimed_matrix = ineq_matrix[0]
    retime = input("Would you like to use this retiming vector to create a new circuit file?(y/n)")
    if retime == 'y':
        for r in range(size):
            for c in range(size):
                if retimed_matrix[r,c] != 9999:
                    retimed_matrix[r,c] = retimed_matrix[r,c] - retiming_vector[r]
                if retimed_matrix[c,r] != 9999:
                    retimed_matrix[c,r] = retimed_matrix[c,r] + retiming_vector[r]
        retimed_circuit_file(parsed_info,new_c_value,retimed_matrix,new_file_path)
        print("Done! New Circuit File Created")
    elif retime == 'n':
        print("Not using retiming vector, ending scrip")
    else:
        print("Invalid response, retiming vector ignored")

