from datetime import datetime
import re
import itertools
from pygments.lexers import CppLexer
from pygments.formatters import TerminalFormatter
from pygments import highlight
import functools

# This class will help generate in context matches for regex
class IndexLineMapper:
    # Instance variables
        # lines
        # pretty_lines
        # max_line_num

    def __init__(self, file: str):
        # Init instance variables
        self.lines =  []
        self.pretty_lines = []
        self.max_line_num = -1

        lexer = CppLexer(stripnl=False)
        formatter = TerminalFormatter(style='default')
        pretty_file = highlight(file, lexer, formatter)

        if (file.strip() == ""):
            return

        self.lines = file.split('\n')
        self.pretty_lines = pretty_file.split('\n')

        # Line nums matches each line in the list with its line number
        line_nums = [i for i in range(1, len(self.lines) + 1)]

        # Accum line length denotes the length of each line *including* the \n
        # This means that accum_line_length[i] denotes the index of the first character of lines[i+1] in the file string
        # accum_line_length[-1] should be equal to len(file)
        accum_line_length = [len(l) for l in self.lines]
        accum_line_length = [a + 1 for a in accum_line_length]
        accum_line_length[-1] -= 1     # The last line, by definition, is not followed by a \n
        accum_line_length = list(itertools.accumulate(accum_line_length))

        self.lines = list(zip(self.lines, line_nums, accum_line_length))
        self.pretty_lines = list(zip(self.pretty_lines, line_nums, accum_line_length))

        # Setting this to make line numbering easier
        self.max_line_num = max(line_nums)


    
    def stringIndexToLineNum(self, strindex: int):
        # Find the line index that corresponds to the index of a character
        # in the string using Binary Search.

        lineIndex = None
        low = 0
        high = len(self.lines) - 1

        while (lineIndex == None):
            mid = low + (high - low) // 2
            last_line_offset = self.lines[mid - 1][2] if mid - 1 >= 0 else 0
            
            if (strindex < self.lines[mid][2] and strindex >= last_line_offset):
                lineIndex = mid
                break

            elif (strindex >= self.lines[mid][2]):
                low = mid + 1
                if (low > high or low > len(self.lines)):
                    lineIndex = -1
                    break
                else:
                    continue

            elif ( strindex < last_line_offset):
                high = mid - 1
                if (high < low or high < 0):
                    lineIndex = -1
                    break
                else:
                    continue

        
        if (lineIndex == -1):
            raise ValueError("Could not get line because string index is out of range.")

        # Convert the found index into a line number and return.
        return lineIndex + 1


    def getLine(self, line_number: int):
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        index = line_number - 1
        return self.lines[index][0]

    def getNumberedLine(self, line_number: int):
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        index = line_number - 1
        len_max_line_num = len(str(self.max_line_num))
        return f"{str(self.lines[index][1]).ljust(len_max_line_num)} │ {self.lines[index][0]}"

    def getNumberedLineWithContext(self, line_number: int, context_radius=1):
        # Validity check
        if (line_number < 1 or line_number > self.max_line_num):
            raise ValueError("Invalid line number.")
        
        # Put together the lines safely
        index = line_number - 1
        output_line_indices = range(max(0, index - context_radius), min(index + context_radius + 1, len(self.lines)))
        output_lines = [self.getNumberedLine(oli + 1) for oli in output_line_indices]
        return "\n".join(output_lines)

    def getNumberedLinesWithContext(self, line_numbers: list[int], context_radius=1):
        if (len(line_numbers) == 1):
            return self.getNumberedLineWithContext(line_numbers[0], context_radius)

        # Validity check
        max_gap = 0
        increasing = True
        for i in range(len(line_numbers) - 1):
            increasing = increasing and (line_numbers[i+1] - line_numbers[i] > 0)
            max_gap = max(max_gap, abs(line_numbers[i+1] - line_numbers[i]))

        if (max_gap != 1 or increasing == False or line_numbers[0] < 1 or line_numbers[-1] > self.max_line_num):
            raise ValueError("Line numbers array is invalid.")
        
        # Put together the lines
        istart = line_numbers[0] - 1 - context_radius
        iend = line_numbers[-1] - 1 + context_radius
        output_line_indices = range(max(0, istart), min(iend + context_radius + 1, len(self.lines)))
        output_lines = [self.getNumberedLine(oli + 1) for oli in output_line_indices]
        return "\n".join(output_lines)
        
    def getMaxLineNum(self):
        return self.max_line_num
    
    def printAll(self):
        for ln in range(1, len(self.lines) + 1):
            print(self.getLine(ln))
        

