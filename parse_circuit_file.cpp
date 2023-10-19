#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <cstdlib> // for atoi

// Struct to hold information parsed from the circuit file
struct CircuitInfo {
    int total_nodes;
    std::vector<int> node_delays;
    std::map<std::string, int> edge_delays;
    int max_clock_cycle;
};

CircuitInfo parse_circuit_file(const std::string& file_path) {
    // Open the file
    std::ifstream file(file_path.c_str());
    if (!file.is_open()) {
        std::cerr << "Error opening file" << std::endl;
        exit(EXIT_FAILURE); // Ensure you include <cstdlib>
    }

    CircuitInfo circuit_info = {0, {}, {}, 0}; // Initialize the struct
    std::string line;

    while (getline(file, line)) {
        if (line.empty() || line[0] == '/') { // Ignore empty lines and comments
            continue;
        }

        std::istringstream iss(line);
        std::string key;
        std::string value;

        if (getline(iss, key, '=') && getline(iss, value)) {
            // Remove whitespace around the key, if any
            key.erase(0, key.find_first_not_of(" \t"));
            key.erase(key.find_last_not_of(" \t") + 1);

            if (key == "TotalNodes") {
                circuit_info.total_nodes = std::atoi(value.c_str());
            } 
            else if (key == "NodeDelays") {
                std::istringstream ss(value);
                std::string delay;
                while (getline(ss, delay, ',')) {
                    circuit_info.node_delays.push_back(std::atoi(delay.c_str()));
                }
            } 
            else if (key == "MaxClockCycle") {
                circuit_info.max_clock_cycle = std::atoi(value.c_str());
            } 
            else { // Parsing edge delays
                circuit_info.edge_delays[key] = std::atoi(value.c_str());
            }
        }
    }

    file.close(); // Don't forget to close the file
    return circuit_info;
}

int main() {
    // Path to the circuit file
    std::string file_path = "example_input.txt"; 

    // Parse the circuit file 
    CircuitInfo circuit_info = parse_circuit_file(file_path);

    // Print information stored in the struct
    std::cout << "Total Nodes: " << circuit_info.total_nodes << std::endl;

    // Don't forget to handle the rest of the data as per your requirements

    return 0;
}