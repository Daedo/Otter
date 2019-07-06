# Otter
Optimal Testsuites from Requirements

# Requirements:
Python 3

# Generating Testcases for a requirement function
For an example pipeline consider the run_pipeline function in main.py
Just Provide a boolean function and let it run.

# Generating CEGs
The CEG Class provides all functions to create CEGs.
Use CEGNode.arcTo to construct arcs.
You can use get_cause_function to generate a boolean function from an effect node.
This function can be used in the pipeleine.
Alternatively you can use get_testcases in basicPathSensitization.py to run BPS on the effect node.
