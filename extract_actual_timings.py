#!/usr/bin/env python3
"""
Extract actual timing constants from working 24C_High code
"""

from app.core.tuya_encoder import decode_ir

# Working code
WORKING = "EfcMNAbRAYIB0QFWAdEBkwTRAeADB0ALQANAF0ADQAvAA0APQAPAD0AHwEdAC+ADA0AXQAPAE0A3QA9AA8ATwAdAE0AfwA/AB0AT4BMD4AMnwAvAB0BTwANAE8BHQAtAA0APQAdAI0AH4AMDQBvAF0ALwBsAgmABAdEBQA/AFwCCYAEB0QHgAQ8C0QGCYAFABwHRAUAr4AMHAIJgAUAHgAOAH8ABAdEBQANAE0ADAILgAAFAC4ADgBcC0QGCYAFAB4ADQBcHkwSCAYIB0QFAC0ADBJME0QGCIAFAB0ADC1YB0QGCAdEBggHRAQ=="

signal = decode_ir(WORKING)

print("="*80)
print("EXTRACTING ACTUAL TIMING CONSTANTS")
print("="*80)

print(f"\nTotal timings: {len(signal)}")
print(f"First 20 timings: {signal[:20]}")

# Header (first 2 timings)
header_mark = signal[0]
header_space = signal[1]

print(f"\nHeader:")
print(f"  MARK:  {header_mark} μs")
print(f"  SPACE: {header_space} μs")

# Data timings (skip header)
data_timings = signal[2:]

# Collect all unique marks and spaces
marks = []
spaces = []

for i in range(0, len(data_timings), 2):
    if i < len(data_timings):
        marks.append(data_timings[i])
    if i + 1 < len(data_timings):
        spaces.append(data_timings[i + 1])

print(f"\nData timings:")
print(f"  Marks: {len(marks)} values")
print(f"  Spaces: {len(spaces)} values")

# Find unique values
unique_marks = sorted(set(marks))
unique_spaces = sorted(set(spaces))

print(f"\nUnique marks: {unique_marks}")
print(f"\nUnique spaces: {unique_spaces}")

# Identify which is zero/one based on frequency and value
from collections import Counter

mark_counts = Counter(marks)
space_counts = Counter(spaces)

print(f"\nMark frequencies:")
for mark, count in sorted(mark_counts.items()):
    print(f"  {mark:4d} μs: {count:3d} times")

print(f"\nSpace frequencies:")
for space, count in sorted(space_counts.items()):
    print(f"  {space:4d} μs: {count:3d} times")

# Typical IR protocol:
# - BIT_MARK: same for all bits
# - ZERO_SPACE: short space
# - ONE_SPACE: long space

# Guess based on data:
if len(unique_marks) == 1:
    bit_mark = unique_marks[0]
    print(f"\n✓ BIT_MARK: {bit_mark} μs (all marks same)")
elif len(unique_marks) == 2:
    # Take most common
    bit_mark = mark_counts.most_common(1)[0][0]
    print(f"\n✓ BIT_MARK: {bit_mark} μs (most common)")
else:
    # Average
    bit_mark = int(sum(marks) / len(marks))
    print(f"\n✓ BIT_MARK: {bit_mark} μs (average)")

# Spaces should have 2 main values: short (0) and long (1)
if len(unique_spaces) >= 2:
    sorted_spaces = sorted(unique_spaces)
    zero_space = sorted_spaces[0]  # Shortest
    one_space = sorted_spaces[-1]   # Longest
    print(f"✓ ZERO_SPACE: {zero_space} μs")
    print(f"✓ ONE_SPACE: {one_space} μs")

print(f"\n" + "="*80)
print("RECOMMENDED CONSTANTS")
print("="*80)

print(f"""
# Timing constants from working 24C_High code
FUJITSU_HEADER_MARK = {header_mark}
FUJITSU_HEADER_SPACE = {header_space}
FUJITSU_BIT_MARK = {bit_mark}
FUJITSU_ZERO_SPACE = {zero_space}
FUJITSU_ONE_SPACE = {one_space}
""")

# Compare with current constants
from app.core.fujitsu_encoder import (
    FUJITSU_HEADER_MARK as CURRENT_HEADER_MARK,
    FUJITSU_HEADER_SPACE as CURRENT_HEADER_SPACE,
    FUJITSU_BIT_MARK as CURRENT_BIT_MARK,
    FUJITSU_ZERO_SPACE as CURRENT_ZERO_SPACE,
    FUJITSU_ONE_SPACE as CURRENT_ONE_SPACE,
)

print("="*80)
print("COMPARISON WITH CURRENT CONSTANTS")
print("="*80)

print(f"\nHEADER_MARK:  {CURRENT_HEADER_MARK} → {header_mark} (diff: {header_mark - CURRENT_HEADER_MARK:+d})")
print(f"HEADER_SPACE: {CURRENT_HEADER_SPACE} → {header_space} (diff: {header_space - CURRENT_HEADER_SPACE:+d})")
print(f"BIT_MARK:     {CURRENT_BIT_MARK} → {bit_mark} (diff: {bit_mark - CURRENT_BIT_MARK:+d})")
print(f"ZERO_SPACE:   {CURRENT_ZERO_SPACE} → {zero_space} (diff: {zero_space - CURRENT_ZERO_SPACE:+d})")
print(f"ONE_SPACE:    {CURRENT_ONE_SPACE} → {one_space} (diff: {one_space - CURRENT_ONE_SPACE:+d})")

print(f"\n✓ Use these ACTUAL timing values to match your working code!")
