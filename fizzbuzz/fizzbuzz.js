for (let i = 1; i <= 100; i++){ // Iterate i over the range [1,100]
    if (i % 3 === 0 && i % 5 === 0){ // If i is divisible by both 3 and 5, print FizzBuzz
        console.log('FizzBuzz');
    } else if (i % 3 === 0){ // If i is divisible by only 3, print Fizz
        console.log('Fizz');
    } else if (i % 5 === 0){ // If i is divisible by only 5, print Buzz
        console.log('Buzz');
    } else { // Otherwise, print i
        console.log(i);
    }
}