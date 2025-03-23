#include <stdio.h>
int main(){
    for (int i=1; i<=100; i++){ // Iterate over the numbers 1 to 100
        if (i%5 == 0 && i%3 == 0){ // If divisible by 3 and 5, FizzBuzz!
            printf("FizzBuzz\n");
        } else if (i%3 == 0){ // If divisible by 3, it's Fizz time!
            printf("Fizz\n");
        } else if (i%5 == 0){ // If divisible by 5, it's Buzz time!
            printf("Buzz\n");
        } else { // Not divisible by 3 or 5. Womp womp! Just print i
            printf("%d\n",i); // Use format string to help print i
        }
    }
    return 0;
}
