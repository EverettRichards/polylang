for i in range(1,101): # For loop will repeat over the range [1,100]
    if i%3 == 0 and i%5 == 0: # If divisible by both 3 and 5, print "FizzBuzz"
        print("FizzBuzz")
    elif i%3 == 0: # If divisible by ONLY 3, print "Fizz"
        print("Fizz")
    elif i%5 == 0: # If divisible by ONLY 5, print "Buzz"
        print("Buzz")
    else: # If NOT divisible by 3 or 5, print the number itself
        print(i)