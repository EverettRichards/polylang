#lang racket
(define (FizzBuzz)
  (for ([i (in-range 1 101)]) ; Loop through numbers in [1,100]
    (if (and (= (remainder i 3) 0) (= (remainder i 5) 0)) ; If i is divisible by both 3 and 5, print "FizzBuzz", else proceed to next *if*
        (displayln "FizzBuzz")
        (if (= (remainder i 3) 0) ; If i is divisible by only 3, print "Fizz", else proceed to next *if*
            (displayln "Fizz")
            (if (= (remainder i 5) 0) ; If i is divisible by only 5, print "Buzz", else proceed to next *if*
                (displayln "Buzz")
                (displayln i)))))) ; In the final *else*, print the number itself, since it's not divisible by 3 or 5
     
(FizzBuzz)