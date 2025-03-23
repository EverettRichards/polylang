using System;
class FizzBuzz
{
static void Main(string[] args)
    {
        for (int i=1; i<=100; i++){ // Iterate i over the range [1,100]
            if (i%5 == 0 && i%3 == 0){ // If i is divisible by both 3 and 5, print FizzBuzz
                Console.WriteLine("FizzBuzz");
            } else if (i%3 == 0){ // If i is divisible by only 3, print Fizz
                Console.WriteLine("Fizz");
            } else if (i%5 == 0){ // If i is divisible by only 5, print Buzz
                Console.WriteLine("Buzz");
            } else { // Otherwise, print i
                Console.WriteLine(i);
            }
        }  
    }
}