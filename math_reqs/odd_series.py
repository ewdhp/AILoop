
"""
In a quadratic sequence, the first differences are not constant, but the second differences are constant, and halving the second difference gives the coefficient of the n² term.
Understanding Differences in Quadratic Sequences
A quadratic sequence is a sequence of numbers where the nth term can be expressed as a quadratic formula: an² + bn + c, where a, b, and c are constants, and n is the term position 
Third Space Learning
Third Space Learning
+1
. Unlike linear sequences, the first differences (differences between consecutive terms) are not constant, but the second differences (differences of the first differences) are constant 
igcsemathstutor.com
igcsemathstutor.com
+1
.
For example, consider the sequence: 1, 4, 9, 16, 25.

First differences: 3, 5, 7, 9 (not constant)
Second differences: 2, 2, 2 (constant)
This constant second difference is the hallmark of a quadratic sequence 
igcsemathstutor.com
igcsemathstutor.com
.
Why Halve the Second Difference?
The coefficient a of the n² term in the quadratic formula is half of the second difference. This is because the first difference of n² terms grows linearly, and the second difference represents 2a. Therefore, dividing the second difference by 2 gives the actual value of a 
Studocu
Studocu
+1
.
For the sequence above:

Second difference = 2
Coefficient a = 2 ÷ 2 = 1
Hence, the nth term formula starts with 1·n² = n².
Using Differences to Find the nth Term
Calculate first differences between consecutive terms.
Calculate second differences from the first differences.
Halve the second difference to find a.
Subtract an² from the original sequence to form a linear sequence.
Find b and c by solving the remaining arithmetic sequence or substituting known term positions into the formula 
MME Revise
MME Revise
+1
.
This method allows you to generate any term in the sequence and extend it systematically.
Summary
First differences: change each time in a quadratic sequence.
Second differences: constant, indicating the sequence is quadratic.
Coefficient a: half of the second difference.
nth term formula: an² + bn + c, derived using the difference method.
Understanding these differences is essential for identifying quadratic sequences and deriving their nth term formulas.  
"""
import matplotlib.pyplot as plt

# Formula #2:
# 1 + 3 + 5 + ... + (2n - 1) = n^2

max_n = 20
total = 0

print("SUM OF THE FIRST n ODD NUMBERS")
print("1 + 3 + 5 + ... + (2n - 1) = n^2\n")

print(f"{'n':>3} {'Odd term':>10} {'Sum':>10} {'n^2':>10} {'Verified':>10}")
print("-" * 50)

values_n = []
sums = []
squares = []

for n in range(1, max_n + 1):
    odd = 2 * n - 1
    total += odd
    square = n ** 2

    verified = total == square

    print(f"{n:>3} {odd:>10} {total:>10} {square:>10} {str(verified):>10}")

    values_n.append(n)
    sums.append(total)
    squares.append(square)

# Plot both results
plt.plot(values_n, sums, "o-", label="Sum of odd numbers")
plt.plot(values_n, squares, "--", label="n^2")

plt.xlabel("n (number of terms)")
plt.ylabel("Total")
plt.title("1 + 3 + 5 + ... + (2n - 1) = n^2")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Examine one example
n = 5
terms = [2 * k - 1 for k in range(1, n + 1)]

print("\nWorked example:")
print(" + ".join(map(str, terms)), "=", sum(terms))
print(f"{n}^2 =", n ** 2)



increments = [sums[0]] + [
    sums[i] - sums[i - 1]
    for i in range(1, len(sums))
]

plt.figure()
plt.plot(values_n, increments, "o-", label="Increment: S(n) - S(n-1)")
plt.plot(values_n, [2*n - 1 for n in values_n], "--",
         label="2n - 1")

plt.xlabel("n")
plt.ylabel("Increment")
plt.title("The added amount grows linearly")
plt.grid(True)
plt.legend()
plt.show()