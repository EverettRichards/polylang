p

public class fizzbuzz {
    public static void main(String[] args){
       for (int i = 1; i <= 100; i++) { // Iterate i over the range [1,100]
            if (i%5==0 && i%3==0){ // If i is divisible by both 3 and 5, print FizzBuzz
                System.out.println("FizzBuzz");
            } else if (i%3==0){ // If i is divisible by only 3, print Fizz
                System.out.println("Fizz");
            } else if (i%5==0){ // If i is divisible by only 5, print Buzz
                System.out.println("Buzz");
            } else { // Otherwise, print i
                System.out.println(i);
            }
       }
    }
}
