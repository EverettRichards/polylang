import subprocess
import os

def run_java_file(java_file_path):
    """
    Runs a java file and returns the output.

    Args:
        java_file_path: The path to the java file.

    Returns:
        A string containing the output of the java program, or None if an error occurred.
    """
    try:
        # Compile the java file
        subprocess.run(["javac", java_file_path], check=True, capture_output=True)

        # Get the class name from the file name
        class_name = os.path.splitext(os.path.basename(java_file_path))[0]

        # Run the compiled java class file
        process = subprocess.run(["java", class_name], capture_output=True, text=True)
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing java file: {e}")
        return None
    except FileNotFoundError:
        print("Please ensure that you have the Java Development Kit (JDK) installed correctly and that the 'java' and 'javac' commands are available in your system's PATH environment variable.")
        return None

if __name__ == "__main__":
    # Example usage
    java_file = "HelloWorld.java"
    # Create a dummy java file
    with open(java_file, "w") as f:
        f.write("public class HelloWorld { public static void main(String[] args) { System.out.println(\"Hello, world!\"); } }")

    output = run_java_file(java_file)
    if output:
        print(f"Java program output:\n{output}")

    # Clean up the created file
    os.remove(java_file)
    os.remove("HelloWorld.class")