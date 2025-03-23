import sys
from math import comb
import re
import time
from abc import ABC, abstractmethod
import traceback
import subprocess
import os
import tempfile
import shutil
import shlex
import builtins

# TODO:
# Detect Parentheses
# Make compilation and execution instructions more modular
# Order of Operations

s = {}

operators = { # a list of each valid operator, and a small lambda function that says what to do if that operator is encountered
    "$nCr$": lambda x,y: comb(int(x),int(y)), # n choose c
    "^": lambda x,y: float(x)**float(y),
    "$root$": lambda x,y: float(x)**(1/float(y)),
    "%": lambda x,y: x%y,
    "*": lambda x,y: x*y,
    "/": lambda x,y: x/y,
    "+": lambda x,y: x+y,
    "-": lambda x,y: x-y,
    "$min$": lambda x,y: min(x,y),
    "$max$": lambda x,y: max(x,y),
} # Important: List must be in order of operations

def isNumeric(operand):
    return operand.replace('.','',1).isdigit()

op_pad_size = 7

adjusted_operators = {}
for op in operators:
    adjusted_operators[op] = ";"*(op_pad_size-len(op))+op
inverse_adjusted_operators = {}
for i,j in adjusted_operators.items():
    inverse_adjusted_operators[j]=i

def get_operators(string):
    ops = []
    for op in operators:
        string = string.replace(op,adjusted_operators[op])
    for i in range(0,len(string)-op_pad_size+1):
        substring = string[i:i+op_pad_size]
        if substring in inverse_adjusted_operators:
            ops.append(inverse_adjusted_operators[substring])
    return ops

def eval_basic_expr(expr):
    if expr in s:
        return s[expr]
    result = 0

    ops = get_operators(expr)
    mod_expr = expr
    for op in operators:
        mod_expr = mod_expr.replace(op,";")
    digits = mod_expr.split(";")
    if len(digits) != len(ops)+1:
        raise Exception(f"The number of operands does not align with the number of operators.")
    if len(digits)==1:
        return digits[0]
    result = digits[0]
    ### Old parser
    # for i in range(len(ops)):
    #     result = apply_operator(str(result),str(digits[i+1]),ops[i])
    ### Order of Operations parser
    for this_op in operators:
        i=0
        while i < len(ops):
            op = ops[i]
            if op==this_op:
                digits[i] = apply_operator(str(digits[i]),str(digits[i+1]),op)
                digits.pop(i+1)
                ops.pop(i) # fix issue where not working sometimes. also make it supported beyond print function, i.e. with closing )
            else:
                i += 1
    result = digits[0]
    #print("Result:",digits[0])
    return result

def eval_expr(expr):
    if expr in s:
        return s[expr]
    
    if not ("(" in expr or ")" in expr):
        return eval_basic_expr(expr)
    
    depth = 0
    current_part = ""
    parts = []

    for ch in expr:
        if ch=="(":
            if depth == 0:
                parts.append(current_part)
                current_part = ""
            else:
                current_part += "("
            depth += 1
        elif ch==")":
            if depth == 1:
                parts.append(current_part)
                current_part = ""
            else:
                current_part += ")"
            depth -= 1
        else:
            current_part = current_part + ch
    parts.append(current_part)
    new_parts = []

    for part in parts:
        if len(part)==0: continue
        if "(" in part and ")" in part:
            new_parts.append(str(eval_expr(part)))
        elif all(part!=op for op in operators) and not isNumeric(part) and not any(part.startswith(op) for op in operators): # make sure it isn't just a single operator
            new_parts.append(str(eval_basic_expr(part)))
        else:
            new_parts.append(part)
    new_expr = "".join(new_parts)
    return eval_expr(new_expr)

def eval_bool_expr(expr):

    # here's my problem! not implemented
    # re.split(r"[()]",expr) will return just the basic characters AND operations
    if expr=="True":
        return True
    elif expr=="False":
        return False
    result = False
    included_comps = [comp for comp in comparers if comp in expr]
    if isNumeric(expr):
        result = int(expr)!=0 # True if non-zero, False if zero
    elif len(included_comps)==1: # only one comparer is being used
        comp = included_comps[0]
        op1,op2 = expr.split(comp)
        result = apply_comparer(op1,op2,comp) # apply the specified operation to the operands
    elif len(included_comps)>1:
        raise Exception(f"Attempted to use {len(included_comps)} comparers at the same time.")
    else:
        raise Exception(f"Invalid boolean expression '{expr}' provided.")
    return result

def varmap(var,s):
    if var not in s: raise Exception(f"Variable '{var}' not defined")
    return s[var]

def eval_var(var, s): # find the value of a variable
    if var in s:
        return varmap(var,s)
    else:
        raise Exception(f"Variable '{var}' not defined")

comparers = {
    "==": lambda x,y: x==y,
    ">": lambda x,y: x>y,
    "<": lambda x,y: x<y,
    "$geq$": lambda x,y: x>=y,
    "$leq$": lambda x,y: x<=y,
    "!=": lambda x,y: x!=y,
}

def apply_operator(op1,op2,operator):
    op1,op2 = op1.strip(), op2.strip()
    if not isNumeric(op1):
        op1 = eval_var(op1,s)
    if not isNumeric(op2):
        op2 = eval_var(op2,s)
    if operator in operators:
        return operators[operator](float(op1),float(op2))
    
def apply_comparer(op1,op2,comparer):
    op1,op2 = op1.strip(), op2.strip()
    if not isNumeric(op1):
        op1 = eval_expr(op1)
    if not isNumeric(op2):
        op2 = eval_expr(op2)
    if comparer in comparers:
        return comparers[comparer](float(op1),float(op2))
    
def removeComments(line): # Removes comments from the end of a line
    line = line.strip() # clear whitespace
    if not "#" in line:
        return line
    else:
        split = line.split("#")
        line = split[0]
        return line.strip()
    
def isValidVariable(var):
    if type(var) != str: return False
    if len(var)==0: return False
    start = var[0]
    if not start.isalpha(): return False # non-alphabetic character detected
    for char in var:
        if not char.isalpha() and not char.isdigit():
            return False
    return True

class Scope(ABC):
    @abstractmethod
    def endEncountered(self,PROGRAM_STACK,_):
        pass

# allows the program to keep track of a scope that it didn't execute, due to a conditional statement.
# if not for this, it wouldn't know what to do when an "end" is encountered!
class SkippedScope(Scope):
    def __init__(self,PROGRAM_STACK):
        PROGRAM_STACK.append(self)

    def endEncountered(self,PROGRAM_STACK,_):
        PROGRAM_STACK.pop()

class Conditional(Scope):
    def __init__(self,PROGRAM_STACK,line):
        _,cond = line.split("if(")
        if not line.endswith(")then"): raise Exception("Missing closing parentheses with 'then'.")
        bool_expr,_ = cond.split(")then")
        self.bool_expr = bool_expr
        val = eval_bool_expr(bool_expr)
        self.has_been_true = val
        self.skip_to_end = not val
        PROGRAM_STACK.append(self)

    def elseifEncountered(self,line):
        _,condition = line.split("elseif(")
        if not line.endswith(")then"): raise Exception("Missing closing parentheses with 'then'.")
        val,_ = condition.split(")then")
        
        if self.has_been_true:
            self.skip_to_end = True
        else:
            val = eval_bool_expr(val)
            self.has_been_true = val
            self.skip_to_end = not val

    def elseEncountered(self):
        if self.has_been_true:
            self.skip_to_end = True
        else:
            self.has_been_true = True
            self.skip_to_end = False

    def endEncountered(self,PROGRAM_STACK,_,didBreak=False): # what to do when you reach an end?
        PROGRAM_STACK.pop()

class ForLoop(Scope):
    def __init__(self,PROGRAM_STACK,line_num,line):
        _,contents = line.split("for(")
        if not line.endswith(")do"): raise Exception("Missing closing parentheses with 'do'.")
        contents,_ = contents.split(")do")
        var_name,params = contents.split(":")
        parameters = [int(x) for x in params.split(",")]
        min,max,inc = 0,1,1
        if len(parameters)==1:
            min,max,inc = 1,parameters[0],1
        elif len(parameters)==2:
            min,max,inc = parameters[0],parameters[1],1
        elif len(parameters)==3:
            min,max,inc = parameters[0],parameters[1],parameters[2]
        else:
            raise Exception(f"Improper number of parameters specified for 'for' loop.")
        
        self.is_decreasing = max < min
        
        s[var_name] = min
        self.line_num, self.var, self.max, self.inc = line_num, var_name, max, inc
        PROGRAM_STACK.append(self)

    def endEncountered(self,PROGRAM_STACK,endline):
        #print("End encountered:",s[self.var],self.line)
        if ((not self.is_decreasing) and s[self.var] + self.inc <= self.max) or ((self.is_decreasing) and s[self.var] + self.inc >= self.max): # current + iter <= max
            s[self.var] = s[self.var] + self.inc # increment the iterator variable
            if DEBUG_MODE:
                printColor("yellow",f"ITERATOR: {self.var} = {s[self.var]}")
            return self.line_num # tell the thread to restart the loop
        else:
            if DEBUG_MODE:
                printColor("yellow","loop ended")
            PROGRAM_STACK.pop()
            return endline # tell the thread to end the loop
        
def parseCSharp(content):
    with tempfile.TemporaryDirectory() as tmpdirname:
        project_path = os.path.join(tmpdirname, "MyApp")

        # Step 1: Create a new C# console project
        subprocess.run(
            ["dotnet", "new", "console", "-o", project_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        program_cs_path = os.path.join(project_path, "Program.cs")

        # Step 2: Replace Program.cs with user's code
        with open(program_cs_path, "w") as cs_file:
            cs_file.write(content)

        # Step 3: Build the project
        build_result = subprocess.run(
            ["dotnet", "build", project_path, "-c", "Release"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        if build_result.returncode != 0:
            return f"Compilation Error:\n{build_result.stderr}"

        # Step 4: Run the compiled program
        # Detect actual DLL path (from bin/Release)
        release_path = os.path.join(project_path, "bin", "Release")
        frameworks = os.listdir(release_path)
        if not frameworks:
            return "No compiled framework folder found."

        dll_path = os.path.join(release_path, frameworks[0], "MyApp.dll")

        # Fix: run dotnet with proper DLL path
        run_result = subprocess.run(
            ["dotnet", dll_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if run_result.returncode != 0:
            print("Run returned non-zero exit code:")
            print("STDERR:\n", run_result.stderr)
            print("STDOUT:\n", run_result.stdout)

            return f"Runtime Error:\n{run_result.stderr}"

        printColor("purple",run_result.stdout.strip())

def parseRacket(content):
    with tempfile.TemporaryDirectory() as tmpdirname:
        racket_path = os.path.join(tmpdirname, "script.rkt")

        with open(racket_path, "w") as f:
            f.write(content)

        run_result = subprocess.run(
            ["racket", racket_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if run_result.returncode != 0:
            return f"Runtime Error:\n{run_result.stderr}"

        printColor("purple",run_result.stdout.strip())
        
def parseCpp(contents):
    filename = "Main"
    with tempfile.TemporaryDirectory() as tmpdirname:
        cpp_path = os.path.join(tmpdirname, f"{filename}.cpp")
        exe_path = os.path.join(tmpdirname, filename)

        # Step 1: Write the C++ code to file
        with open(cpp_path, "w") as cpp_file:
            cpp_file.write(contents)

        # Step 2: Compile the C++ code
        compile_result = subprocess.run(
            ["g++", cpp_path, "-o", exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if compile_result.returncode != 0:
            return f"Compilation Error:\n{compile_result.stderr}"

        # Step 3: Run the compiled program
        run_result = subprocess.run(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if run_result.returncode != 0:
            return f"Runtime Error:\n{run_result.stderr}"

        printColor("purple",run_result.stdout.strip())

def parseJava(contents):
    class_name = "Main"
    with tempfile.TemporaryDirectory() as tmpdirname:
        java_file = os.path.join(tmpdirname, f"{class_name}.java")
        
        with open(java_file, "w") as f:
            f.write(contents)

        # Compile
        compile_result = subprocess.run(
            ["javac", f"{class_name}.java"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=tmpdirname
        )

        if compile_result.returncode != 0:
            return f"Compilation Error:\n{compile_result.stderr}"

        # Run
        run_result = subprocess.run(
            ["java", "-cp", ".", class_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=tmpdirname
        )

        if run_result.returncode != 0:
            return f"Runtime Error:\n{run_result.stderr}"

        printColor("purple",run_result.stdout.rstrip()) # output the Java output
    
def parseJavaScript(content):
    with tempfile.TemporaryDirectory() as tmpdirname:
        js_path = os.path.join(tmpdirname, "script.js")

        # Step 1: Write JS code to file
        with open(js_path, "w") as js_file:
            js_file.write(content)

        # Step 2: Run the JS file with Node.js
        run_result = subprocess.run(
            ["node", js_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if run_result.returncode != 0:
            return f"Runtime Error:\n{run_result.stderr}"

        printColor("purple",run_result.stdout.strip())

def parseJavaMini(contents):
    contents = "public class Main { public static void main(String[] args) {" + contents + "}}"
    parseJava(contents)

class PurpleOutput:
    def write(self, text):
        PURPLE = "\033[95m"
        RESET = "\033[0m"
        sys.__stdout__.write(PURPLE + text + RESET)

    def flush(self):
        sys.__stdout__.flush()

def parsePython(contents):
    original_stdout = sys.stdout
    sys.stdout = PurpleOutput()
    try:
        exec(contents)
    finally:
        sys.stdout = original_stdout

def parseLua(content):
    with tempfile.TemporaryDirectory() as tmpdirname:
        lua_path = os.path.join(tmpdirname, "script.lua")

        with open(lua_path, "w") as f:
            f.write(content)

        run_result = subprocess.run(
            ["lua", lua_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if run_result.returncode != 0:
            return f"Runtime Error:\n{run_result.stderr}"

        printColor("purple",run_result.stdout.strip())

def parseR(content):
    with tempfile.TemporaryDirectory() as tmpdirname:
        r_path = os.path.join(tmpdirname, "script.R")

        # Write R code to a file
        with open(r_path, "w") as r_file:
            r_file.write(content)

        # Run the script using Rscript
        run_result = subprocess.run(
            ["Rscript", r_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if run_result.returncode != 0:
            return f"Runtime Error:\n{run_result.stderr}"

        printColor("purple",run_result.stdout.strip())

LANGUAGES = {
    "javamini": parseJavaMini, # Java, but you don't need to define a class (it does this implicitly)
    "java": parseJava, # Full Java functionality (within the Main class, at least...)
    "python": parsePython,
    "lua": parseLua,
    "c++": parseCpp,
    "cpp": parseCpp,
    "c": parseCpp,
    "js": parseJavaScript,
    "javascript": parseJavaScript,
    "csharp": parseCSharp,
    "racket": parseRacket,
    "r": parseR,
}

UNIQUE_LANGUAGES = ["java","python","lua","c++","javascript","csharp","racket","r"]

HELLO_PROGRAMS = {
    "java": "./hello/hello.java",
    "python": "./hello/hello.py",
    "lua": "./hello/hello.lua",
    "c++": "./hello/hello.cpp",
    "javascript": "./hello/hello.js",
    "csharp": "./hello/hello.cs",
    "racket": "./hello/hello.rkt",
    "r": "./hello/hello.r",
}

class PolyLang(Scope):
    def __init__(self,PROGRAM_STACK,line):
        _,lang = line.split("poly(")
        if not line.endswith("){polystart}"): raise Exception("Missing closing parentheses with '{polystart}'.")
        lang,_ = lang.split("){polystart}")
        if not lang in LANGUAGES: raise Exception(f"Invalid programming language specified: {lang}.")
        self.language = lang
        self.CODE = []
        PROGRAM_STACK.append(self)

    def addLine(self,line):
        self.CODE.append(line)

    def endEncountered(self, PROGRAM_STACK, _): # fired when detected {polyend}
        printColor("yellow",f"Attempting to execute {len(self.CODE)} line(s) of {self.language} code.")
        CODE = "".join(self.CODE)
        execute = LANGUAGES[self.language]
        execute(CODE)
        PROGRAM_STACK.pop()
        
SCOPE_START_KEYWORDS = ["if","for","while","poly"]

color_starts = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
}

color_reset = "\033[0m"

def printColor(color,text):
    print(color_starts[color]+str(text)+color_reset)

def doSkipToEnd(STACK):
    if len(STACK)>0 and type(STACK[-1])==SkippedScope:
        return True
    conditionals = [scope for scope in STACK if type(scope)==Conditional]
    if DEBUG_MODE:
        for i,cond in enumerate(conditionals):
            printColor("red","    ^ SKIP: "+str(i)+": "+str(cond.skip_to_end))
    for cond in conditionals:
        if cond.skip_to_end == True:
            return True
    return False

def getFirstScope(STACK,Type=None):
    if len(STACK) == 0: return None
    if Type == None: return STACK[-1]
    for scope in reversed(STACK):
        if type(scope) == Type:
            return scope
    return None

def tryUndefinedVariableError(string,str_mode):
    if str_mode: return
    if isNumeric(string): return
    if any(op in string for op in operators): return
    if not string in s:
        raise Exception(f"Undefined variable '{string}' detected.")

def parseStringList(input): # known error: turns invalid variables into mere strings
    #a,"hello, there",b,3,4
    if isNumeric(input): return input
    parts = []
    str_mode_tracker = []
    current_str = ""
    str_mode = False
    for i,ch in enumerate(input):
        if ch=='"':
            if current_str != "":
                tryUndefinedVariableError(current_str,str_mode)
                parts.append(current_str)
                str_mode_tracker.append(str_mode)
            str_mode = not str_mode
            current_str = ""
        elif ch==',' and not str_mode:
            if current_str != "":
                tryUndefinedVariableError(current_str,str_mode)
                parts.append(eval_expr(current_str))
                str_mode_tracker.append(str_mode)
            current_str = ""
        else:
            current_str = current_str + ch
            if i == len(input)-1:
                if current_str != "":
                    tryUndefinedVariableError(current_str,str_mode)
                    parts.append(current_str)
                    str_mode_tracker.append(str_mode)
    parts = [str(part) for part in parts]
    for i,part in enumerate(parts):
        str_mode = str_mode_tracker[i]
        if str_mode: continue
        included_ops = [op for op in operators if op in part]
        if len(included_ops)>0:
            parts[i] = str(eval_expr(part))
        elif part in s:
            parts[i] = str(eval_var(part,s))

    output = "".join(parts)
    return output

def interpretProgram(filename):
    file = open(filename,'r')

    s.clear()

    lines = file.readlines()

    #skip_to_end = False # is it in skip mode, due to a conditional statement?
    #has_been_true = False # tool for elseif
    #loop_info = (0,"i",0,0,0) # [first_line, var_name, i_value, i_max, i_increment]

    finished_executing = False
    counter = 0

    PROGRAM_STACK = [] # .append(), .pop()
    # idea: for an `if` or `for`, add new Stackable to the stack. Then work on them in order!

    while not finished_executing:
        if counter >= len(lines):
            break
        line = lines[counter]
        counter += 1

        if type(getFirstScope(PROGRAM_STACK)) == PolyLang:
            scope = getFirstScope(PROGRAM_STACK)
            if line.startswith("{polyend}"):
                scope.endEncountered(PROGRAM_STACK,None)
            else:
                scope.addLine(line)
            continue

        line = removeComments(line) # remove comments and whitespace
        if line.startswith("#") or line=="": continue

        if DEBUG_MODE:
            printColor("blue","STACK: "+str([type(i) for i in PROGRAM_STACK]))
            printColor("green",f"    ^ LINE {counter}: {line}")
        
        if line=="end": # end a conditional statement; proceed as normal
            top_scope = getFirstScope(PROGRAM_STACK)
            if top_scope:
                counter = top_scope.endEncountered(PROGRAM_STACK,counter) or counter
            time.sleep(0.01)
        elif type(getFirstScope(PROGRAM_STACK)) == SkippedScope: # The only time not to ignore is at an end, when it can be popped.
            continue
        elif line.startswith("poly("):
            scope = PolyLang(PROGRAM_STACK,line)
        elif line.startswith("for("):
            scope = ForLoop(PROGRAM_STACK,counter,line)
        elif line=="else": # switch the condition; if not skipping before, start skipping. otherwise, stop skipping
            cond = getFirstScope(PROGRAM_STACK)
            if type(cond) != Conditional: raise Exception("Scope mismatch error in elseif.")
            cond.elseEncountered()
        elif line.startswith("elseif("):
            cond = getFirstScope(PROGRAM_STACK)
            if type(cond) != Conditional: raise Exception("Scope mismatch error in elseif.")
            cond.elseifEncountered(line)
        elif doSkipToEnd(PROGRAM_STACK): # if in skip mode, and didn't hit an 'end' or 'else', then ignore the line
            if any(line.startswith(i+"(") for i in SCOPE_START_KEYWORDS):
                scope = SkippedScope(PROGRAM_STACK)
            continue
        elif line.startswith("if("): # conditional statement begins
            scope = Conditional(PROGRAM_STACK,line)
        elif line.startswith("print("): # we're doing a print!
            _,call = line.split("print(")
            if not call.endswith(")"): raise Exception("Missing closing parentheses.")
            val = call.removesuffix(")") # find the text inside the parentheses
            val = val.strip() # remove whitespace just in case
            included_ops = [op for op in operators if op in val]
            print(parseStringList(val))
        elif line.startswith("hello(") and line.endswith(")"):
            contents = line.removeprefix("hello(").removesuffix(")")
            if len(contents)==0:
                for lang,program in HELLO_PROGRAMS.values():
                    LANGUAGES[lang](program)
            elif any(contents==lang for lang in HELLO_PROGRAMS):
                program = HELLO_PROGRAMS[lang]
                LANGUAGES[lang](program)
        elif "=" in line: # assume variable assignment
            var,expr = line.split("=")
            if not isValidVariable(var): raise Exception(f"Invalid variable name provided: '{var}'.")
            s[var] = eval_expr(expr)
        else:
            raise Exception(f"Line '{line}' does not match any known instruction.")
    printColor("green","> Successfully finished execution with no errors.")

EXECUTE_MAIN_THREAD = False
VERBOSE_ERRORS = False
DEBUG_MODE = False

def runProgram(name):
    try:
        interpretProgram(f"./examples/{name}.poly")
    except Exception as e:
        if VERBOSE_ERRORS:
            printColor("red",f"Error: {traceback.format_exc()}")
        else:
            printColor("red",f"Error: {e}")

def TEST_CASES(): # Used when I want to test specific functions for debugging purposes
    runProgram("program11")

if len(sys.argv) > 1:
    runProgram(sys.argv[1])
elif EXECUTE_MAIN_THREAD:
    printColor("yellow","-"*50)
    for i in range(11,11+1):
        printColor("cyan",f"Program {i} Output:")
        runProgram(f"program{i}")
        printColor("yellow","-"*50)
else:
    TEST_CASES()