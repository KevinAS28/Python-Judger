#index less argument
#line output
#add debug
#add main in solution

import sys
import importlib
import os
import time

def usage():
    print("usage: judge [solution.py] [judgment.py]")
    exit(0)    

cwd = os.getcwd()
sys.path.append(cwd)

default_solution_file = os.path.join(cwd, "solution.py")
default_judgment_file = os.path.join(cwd, "judgment.py")
default_solution_file_avail = os.path.isfile(default_solution_file)
default_judgment_file_avail = os.path.isfile(default_judgment_file)

if len(sys.argv)==1:
    if default_judgment_file_avail and default_solution_file_avail:
        print()
        solution = "solution.py"
        judgment = "judgment.py"
    else:        
        usage()
        
elif len(sys.argv)==2:
    if default_judgment_file_avail:
        solution = sys.argv[1]
        judgment = "judgment.py"
    else:
        usage()
else:
    solution = sys.argv[1]
    judgment = sys.argv[2]


print(f"Using {solution} as solution file and {judgment} as judgment file")

main_function_name = "solution"
naive_solution_function_name = "naive_solution"
sys.path.append(cwd)
main_module = importlib.import_module(solution.split(".")[0])
main_module_attributes = dir(main_module)

use_preparation = False
if "preparation" in main_module_attributes:
    use_preparation = True
    preparation_function = getattr(main_module, "preparation")

try:
    main_function = getattr(main_module, main_function_name)
except:
    print(f"There is no function named '{main_function_name}' (as defined in judeger) in module '{str(main_module)}'")
    print(f"module '{str(main_module)}' attributes: ")
    print(str(main_module_attributes))
judgment_module = importlib.import_module(judgment.split(".")[0])
naive_solution = getattr(judgment_module, naive_solution_function_name)

args_results_len = len(judgment_module.args_results)
all_failures = 0

all_time_epls = []

for arg_result in judgment_module.args_results:
    len_arg_result = len(arg_result)
    args = arg_result[0]
    constant_result = None #defined below when we want to use it
    
    if len(arg_result)>=3:
        exception_use_naive_solution = arg_result[2]
    else:
        exception_use_naive_solution = True
        
    if len(arg_result)>=4:
        exception_use_constant_result = arg_result[3]
    else:
        exception_use_constant_result = True

    
    args_parsed =  str(', '.join( [str(i) for i in args])) 
    print(f"{main_function_name}({args_parsed})", "... ", end="")    

    if use_preparation:
        preparation_function()

    start = time.process_time_ns()
    result_fun = main_function(*args)
    
    if type(result_fun)==str:
        if "\n" in result_fun:
            print()
            print(result_fun)
    else:
        print("=>", result_fun)

    fail = False
    
    if judgment_module.use_naive_solution:
        if (not exception_use_naive_solution):
            print("Not using naive_solution result")        
        else:
            print(f"{naive_solution_function_name}({args_parsed})", "... ", end="")    
            naive_solution_result = naive_solution(*args)
            if type(naive_solution_result) == str:
                if "\n" in naive_solution_result:
                    print()
                    print(naive_solution_result)
            else:                    
                print("=>", naive_solution_result, end="")
            if result_fun == naive_solution_result:
                print("[V]")
            else:
                print("[X]")
                all_failures += 1
                fail = True
        
    if judgment_module.use_constant_result:
        if (not exception_use_constant_result):
            print("Not using constant result")
        else:
            constant_result = arg_result[1]
            print("Constant value ", "=>", constant_result, end="")
            if result_fun == constant_result:
                print(" [V]")
            else:
                print(" [X]")
                if not fail:
                    all_failures += 1
                fail = True

    time_epl = (time.process_time_ns()-start)/1000000000
    print(f"time: {str(time_epl)}s")            
    all_time_epls.append(time_epl)
    
    if not fail:
        print("[OKAY]", end="")
    else:
        print("[WRONG]", end="")
    
    if (judgment_module.use_constant_result and judgment_module.use_naive_solution and exception_use_constant_result and exception_use_naive_solution):
        if naive_solution_result!=constant_result:
            print("  [Warning], naive solution result and constant result are not same")
    
    print("\n\n")
    

print("\n\n"+"#"*20)
if (all_failures==0):
    print(f"[ALL OKAY], average times: {'{:.20f}'.format(sum(all_time_epls)/len(all_time_epls))}")
else:
    print(f"{all_failures} / {args_results_len} FAILED")
print("#"*20)